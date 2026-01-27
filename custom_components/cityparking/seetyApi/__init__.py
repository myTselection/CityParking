"""The API code."""

import logging
import math

from asyncio import CancelledError, TimeoutError
from typing import Optional
import math

import pydantic
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from aiohttp_retry import ExponentialRetry, RetryClient
from pydantic import ValidationError
from yarl import URL
from typing import Optional, Dict, Any

from .models import CityParkingModel, SeetyLocationResponse, SeetyStreetComplete, SeetyStreetRules, SeetyUser, Coords

import logging

_LOGGER = logging.getLogger(__name__)

class SeetyApi:
    """Class to make API requests."""

    def __init__(self, websession: ClientSession):
        """Initialize the session."""
        self.websession = websession
        self.retry_client = RetryClient(
            client_session=self.websession,
            retry_options=ExponentialRetry(attempts=3, start_timeout=5),
        )

    async def getSeetyToken(self):
        url = URL(f"https://api.cparkapp.com/user/")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "Referer": "https://map.seety.co/", "Origin": "https://map.seety.co"}
        response = await self.json_post_with_retry_client(url, payload={}, header=header)

        if pydantic.version.VERSION.startswith("1"):
            seetyUser = SeetyUser.parse_obj(response)
        else:
            seetyUser = SeetyUser.model_validate(response)

        return seetyUser
    

    async def getAddressForCoordinate(self, coordinates: Coords, seetyUser: SeetyUser = None):
        if seetyUser is None:
            seetyUser = await self.getSeetyToken()
        url = URL(f"https://api.cparkapp.com/geocode/{coordinates.lat}/{coordinates.lon}")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "auth-token": seetyUser.access_token, "Referer": "https://map.seety.co/", "Origin": "https://map.seety.co"}
        response = await self.json_get_with_retry_client(url, header=header)

        if pydantic.version.VERSION.startswith("1"):
            seetyLocationInfo = SeetyLocationResponse.parse_obj(response)
        else:
            seetyLocationInfo = SeetyLocationResponse.model_validate(response)

        return seetyLocationInfo

    async def getAddressSeetyInfo(self, coordinates: Coords, seetyUser: SeetyUser = None, seetyLocationInfo: SeetyLocationResponse = None):
        if seetyUser is None:
            seetyUser = await self.getSeetyToken()
        if seetyLocationInfo is None:
            seetyLocationInfo = await self.getAddressForCoordinate(coordinates, seetyUser)
        formatted_address = self.get_street_address(seetyLocationInfo)
        if not formatted_address:
            raise ValidationError("No street address found for the given coordinates")
        url = URL(f"https://api.cparkapp.com/street/rules/{formatted_address}/{coordinates.lat}/{coordinates.lon}")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "auth-token": seetyUser.access_token, "Referer": "https://map.seety.co/", "Origin": "https://map.seety.co"}
        response = await self.json_get_with_retry_client(url, header=header)
        
        if pydantic.version.VERSION.startswith("1"):
            seetyStreetRules = SeetyStreetRules.parse_obj(response)
        else:
            seetyStreetRules = SeetyStreetRules.model_validate(response)

        
        url = URL(f"https://api.cparkapp.com/street/complete/{formatted_address}/{coordinates.lat}/{coordinates.lon}")
        responseComplete = await self.json_get_with_retry_client(url, header=header)
        
        if pydantic.version.VERSION.startswith("1"):
            seetyStreetComplete = SeetyStreetComplete.parse_obj(responseComplete)
        else:
            seetyStreetComplete = SeetyStreetComplete.model_validate(responseComplete)

        cityParkingModel: CityParkingModel
        cityParkingModel = CityParkingModel(
            user = seetyUser,
            rules = seetyStreetRules, 
            streetComplete = seetyStreetComplete
        )
        return cityParkingModel 



    def get_street_address(self, response:SeetyLocationResponse) -> Optional[str]:
        """
        Extract the formatted_address where result type is 'street_address'.
        Returns None if not found.
        """
        if response.status != "OK":
            return None

        for result in response.results:
            if "street_address" in result.types:
                return result.formatted_address

        return None


    def haversine_distance(self, lat1, lon1, lat2, lon2):
        # Radius of the Earth in kilometers
        earth_radius = 6371

        # Convert latitude and longitude from degrees to radians
        lat1 = math.radians(lat1)
        lon1 = math.radians(lon1)
        lat2 = math.radians(lat2)
        lon2 = math.radians(lon2)

        # Haversine formula
        dlat = lat2 - lat1
        dlon = lon2 - lon1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        # Calculate the distance
        distance = round(earth_radius * c, 2)
        # _LOGGER.debug(f"distance: {distance}, lat1: {lat1}, lon1: {lon1}, lat2: {lat2}, lon2: {lon2}")

        return distance

        # # Example usage
        # lat1 = 52.5200  # Latitude of location 1
        # lon1 = 13.4050  # Longitude of location 1
        # lat2 = 48.8566  # Latitude of location 2
        # lon2 = 2.3522   # Longitude of location 2

        # distance = haversine_distance(lat1, lon1, lat2, lon2)
        # print(f"Approximate distance: {distance:.2f} km")



    async def json_get_with_retry_client(self, url, header=None):
        json_response = None
        try:
            async with self.retry_client.get(url, headers=header) as response:
                status = response.status
                reason = response.reason
                headers = dict(response.headers)

                _LOGGER.debug("GET %s -> %s %s", url, status, reason)
                if response.status == 200:
                    result = await response.json(content_type=None)
                    _LOGGER.debug(f"response get url {url}, status: {response.status}, response: {result}")
                    if result:
                        json_response = result
                    else:
                        raise EmptyResponseError()
                elif response.status == 429:
                    raise RateLimitHitError("Rate limit of API has been hit")
                else:
                    _LOGGER.exception(
                        "HTTPError %s occurred while requesting %s, reason: %s, headers: %s",
                        response.status,
                        url,
                        reason,
                        headers
                    )
        except ValidationError as err:
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
            ) as err:
            # Something else failed
            response_body = await response.text()
            _LOGGER.exception(
                "Error while requesting %s: %s, error: %s",
                url,
                response_body,
                err,
                exc_info=True
            )
            raise err
        return json_response


    async def json_post_with_retry_client(self, url, payload, header=None):
        json_response = None
        try:
            async with self.retry_client.post(url, headers=header, json=payload) as response:
                _LOGGER.debug(f"response post url {url}, status: {response.status}, payload: {payload}")
                if response.status == 200:
                    result = await response.json(content_type=None)
                    _LOGGER.debug(f"response post url {url}, status: {response.status}, payload: {payload}, response: {result}")
                    if result:
                        json_response = result
                    else:
                        raise EmptyResponseError()
                elif response.status == 429:
                    raise RateLimitHitError("Rate limit of API has been hit")
                else:
                    error_message = await response.text()
                    _LOGGER.exception(
                        "HTTPError %s occurred while requesting %s, error message: %s",
                        response.status,
                        url,
                        error_message
                    )
        except ValidationError as err:
            _LOGGER.error(err)
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
        ) as err:
            response_body = await response.text()
            _LOGGER.warning(f"Error while requesting {url} {response_body}, error: {err}, exc_info: {err.__traceback__}")
            # Something else failed
            raise err
        return json_response


class EmptyResponseError(Exception):
    """Raised when returned Location API data is empty."""

    pass


class ValidationError(Exception):
    """Raised when returned Location API data is in the wrong format."""

    pass


class RateLimitHitError(Exception):
    """Raised when the rate limit of the API has been hit."""

    pass
