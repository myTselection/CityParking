"""The shellrecharge API code."""

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

from .models import CityParkingModel, SeetyLocation, SeetyStreetComplete, SeetyStreetRules, SeetyUser, ShellChargingStation, Coords, EnecoChargingStation, NearestChargingStations, EnecoTariff
from .user import User

import logging

_LOGGER = logging.getLogger(__name__)
_RADIUS = 100

class SeetyApi:
    """Class to make API requests."""

    def __init__(self, websession: ClientSession):
        """Initialize the session."""
        self.websession = websession
        self.logger = logging.getLogger("evrecharge")
        self.retry_client = RetryClient(
            client_session=self.websession,
            retry_options=ExponentialRetry(attempts=3, start_timeout=5),
        )

    async def getSeetyToken(self):
        url = URL(f"https://api.cparkapp.com/user/")
        response = await self.json_post_with_retry_client(url, payload={})

        if pydantic.version.VERSION.startswith("1"):
            seetyUser = SeetyUser.parse_obj(response.json())
        else:
            seetyUser = SeetyUser.model_validate(response.json())

        return seetyUser
    

    async def getAddressForCoordinate(self, coordinates: Coords, seetyUser: SeetyUser = None):
        if seetyUser is None:
            seetyUser = await self.getSeetyToken()
        url = URL(f"https://api.cparkapp.com/geocode/{coordinates.latitude}/{coordinates.longitude}")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "auth-token": seetyUser.access_token, "Referer": "https://map.seety.co/"}
        response = await self.json_get_with_retry_client(url, header=header)

        if pydantic.version.VERSION.startswith("1"):
            seetyLocationInfo = SeetyLocation.parse_obj(response.json())
        else:
            seetyLocationInfo = SeetyLocation.model_validate(response.json())

        return seetyLocationInfo

    async def getAddressSeetyInfo(self, coordinates: Coords, seetyUser: SeetyUser = None, seetyLocationInfo: SeetyLocation = None):
        if seetyUser is None:
            seetyUser = await self.getSeetyToken()
        if seetyLocationInfo is None:
            seetyLocationInfo = await self.getAddressForCoordinate(coordinates, seetyUser)
        formatted_address = seetyLocationInfo.formatted_address
        url = URL(f"https://api.cparkapp.com/street/rules/{formatted_address}/{coordinates.latitude}/{coordinates.longitude}")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "auth-token": seetyUser.access_token, "Referer": "https://map.seety.co/"}
        response = await self.json_get_with_retry_client(url, header=header)
        
        if pydantic.version.VERSION.startswith("1"):
            seetyStreetRules = SeetyStreetRules.parse_obj(response.json())
        else:
            seetyStreetRules = SeetyStreetRules.model_validate(response.json())

        
        url = URL(f"https://api.cparkapp.com/street/complete/{formatted_address}/{coordinates.latitude}/{coordinates.longitude}")
        responseComplete = await self.json_get_with_retry_client(url, header=header)
        
        if pydantic.version.VERSION.startswith("1"):
            seetyStreetComplete = SeetyStreetComplete.parse_obj(responseComplete.json())
        else:
            seetyStreetComplete = SeetyStreetComplete.model_validate(responseComplete.json())

        cityParkingModel: CityParkingModel
        cityParkingModel = CityParkingModel(
            user = seetyUser,
            rules = seetyStreetRules, 
            streetComplete = seetyStreetComplete
        )
        return cityParkingModel 

    
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
                _LOGGER.debug(f"response url {url}, status: {response.status}")
                if response.status == 200:
                    result = await response.json()
                    _LOGGER.debug(f"response get url {url}, status: {response.status}, response: {result}")
                    if result:
                        json_response = result
                    else:
                        raise EmptyResponseError()
                elif response.status == 429:
                    raise RateLimitHitError("Rate limit of API has been hit")
                else:
                    self.logger.exception(
                        "HTTPError %s occurred while requesting %s",
                        response.status,
                        url,
                    )
        except ValidationError as err:
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
            ) as err:
            # Something else failed
            raise err
        return json_response


    async def json_post_with_retry_client(self, url, payload, header=None):
        json_response = None
        try:
            async with self.retry_client.post(url, headers=header, json=payload) as response:
                _LOGGER.debug(f"response post url {url}, status: {response.status}, payload: {payload}")
                if response.status == 200:
                    result = await response.json()
                    _LOGGER.debug(f"response post url {url}, status: {response.status}, payload: {payload}, response: {result}")
                    if result:
                        json_response = result
                    else:
                        raise EmptyResponseError()
                elif response.status == 429:
                    raise RateLimitHitError("Rate limit of API has been hit")
                else:
                    self.logger.exception(
                        "HTTPError %s occurred while requesting %s",
                        response.status,
                        url,
                    )
        except ValidationError as err:
            _LOGGER.error(err)
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
        ) as err:
            _LOGGER.warning(err)
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
