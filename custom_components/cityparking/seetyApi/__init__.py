"""The API code."""

import logging
import math

from asyncio import CancelledError, TimeoutError
from typing import Optional

import pydantic
from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from aiohttp_retry import ExponentialRetry, RetryClient
from pydantic import ValidationError as PydanticValidationError
from yarl import URL

from ..const import API_MODE_LEGACY, API_MODE_OFFICIAL, DEFAULT_SEETY_API_KEY
from .models import (
    CityParkingModel,
    Coords,
    SeetyExternalRulesResponse,
    SeetyLocationResponse,
    SeetyStreetComplete,
    SeetyStreetRules,
    SeetyUser,
)

_LOGGER = logging.getLogger(__name__)

class SeetyApi:
    """Class to make API requests."""
    # store the seety user token for reuse in different API calls
    # the token seems to be valid for a long time and reduces the number of API calls needed to get the token for each request
    _seety_user_token: Optional[SeetyUser] = None

    def __init__(
        self,
        websession: ClientSession,
        api_mode: str = API_MODE_LEGACY,
        api_key: Optional[str] = None,
        geoapify_api_key: Optional[str] = None,
    ):
        """Initialize the session."""
        self.websession = websession
        self.api_mode = api_mode or API_MODE_LEGACY
        self.api_key = (api_key or DEFAULT_SEETY_API_KEY).strip()
        self.geoapify_api_key = (geoapify_api_key or "").strip()
        self.retry_client = RetryClient(
            client_session=self.websession,
            retry_options=ExponentialRetry(attempts=3, start_timeout=5),
        )

    @property
    def use_official_api(self) -> bool:
        """Return true when configured to use Seety's official external API."""
        return self.api_mode == API_MODE_OFFICIAL

    def clearSeetyUserToken(self):
        """Clear the cached Seety user token."""
        self._seety_user_token = None

    def _parse_model(self, model, response):
        try:
            if pydantic.version.VERSION.startswith("1"):
                return model.parse_obj(response)
            return model.model_validate(response)
        except PydanticValidationError as err:
            raise ValidationError(err) from err

    async def getSeetyToken(self) -> SeetyUser:

        if self._seety_user_token is not None:
            _LOGGER.debug("Reusing existing Seety user token")
            return self._seety_user_token
        url = URL(f"https://api.cparkapp.com/user/")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "Referer": "https://map.seety.co/", "Origin": "https://map.seety.co"}
        response = await self.json_post_with_retry_client(url, payload={}, header=header)

        seetyUser = self._parse_model(SeetyUser, response)

        return seetyUser
    

    async def getAddressForCoordinate(self, coordinates: Coords, seetyUser: SeetyUser = None) -> SeetyLocationResponse:
        if self.geoapify_api_key:
            try:
                return await self.getGeoapifyAddressForCoordinate(coordinates)
            except Exception as err:
                _LOGGER.warning(
                    "Geoapify reverse geocoding failed for %s,%s, falling back to Seety geocode: %s",
                    coordinates.lat,
                    coordinates.lon,
                    err,
                )
        else:
            _LOGGER.debug("Geoapify API key is missing, using Seety geocode fallback")

        return await self.getSeetyAddressForCoordinate(coordinates, seetyUser)

    async def getGeoapifyAddressForCoordinate(self, coordinates: Coords) -> SeetyLocationResponse:
        if not self.geoapify_api_key:
            raise ValidationError("Geoapify API key is required")

        url = URL("https://api.geoapify.com/v1/geocode/reverse").with_query(
            {
                "lat": coordinates.lat,
                "lon": coordinates.lon,
                "format": "json",
                "limit": 1,
                "apiKey": self.geoapify_api_key,
            }
        )
        response = await self.json_get_with_retry_client(url)
        geoapify_result = self._geoapify_first_result(response)
        formatted_address = self._geoapify_formatted_address(geoapify_result)
        if not formatted_address:
            raise EmptyResponseError("Geoapify reverse geocode did not return an address")

        seety_location_info = {
            "status": "OK",
            "results": [
                {
                    "formatted_address": formatted_address,
                    "countryCode": (geoapify_result.get("country_code") or "").upper(),
                    "geometry": {
                        "location": {
                            "lat": geoapify_result.get("lat", coordinates.lat),
                            "lng": geoapify_result.get("lon", coordinates.lon),
                        }
                    },
                    "types": ["street_address"],
                }
            ],
        }

        return self._parse_model(SeetyLocationResponse, seety_location_info)

    def _geoapify_first_result(self, response) -> dict:
        if not isinstance(response, dict) or not response:
            raise EmptyResponseError("Geoapify reverse geocode returned no response")

        if response.get("results"):
            return response["results"][0]

        features = response.get("features") or []
        if features:
            return features[0].get("properties") or {}

        raise EmptyResponseError("Geoapify reverse geocode returned no results")

    def _geoapify_formatted_address(self, result: dict) -> str:
        if not result:
            return ""

        formatted_address = result.get("formatted")
        if formatted_address:
            return formatted_address

        return ", ".join(
            part
            for part in [
                result.get("address_line1"),
                result.get("address_line2"),
                result.get("city"),
                result.get("country"),
            ]
            if part
        )

    def _redact_sensitive_url(self, url) -> URL:
        url = URL(url)
        query = dict(url.query)
        for key in ("apiKey", "apikey", "api_key", "key"):
            if key in query:
                query[key] = "***"
        return url.with_query(query)

    async def getSeetyAddressForCoordinate(self, coordinates: Coords, seetyUser: SeetyUser = None) -> SeetyLocationResponse:
        if seetyUser is None:
            seetyUser = await self.getSeetyToken()
        url = URL(f"https://api.cparkapp.com/geocode/{coordinates.lat}/{coordinates.lon}")
        header={"Content-Type": "application/json", "App-client": "web", "App-lang": "en", "App-version": "12", "auth-token": seetyUser.access_token, "Referer": "https://map.seety.co/", "Origin": "https://map.seety.co"}
        response = await self.json_get_with_retry_client(url, header=header)

        seetyLocationInfo = self._parse_model(SeetyLocationResponse, response)

        return seetyLocationInfo

    async def getAddressSeetyInfo(self, coordinates: Coords, seetyUser: SeetyUser = None, seetyLocationInfo: SeetyLocationResponse = None) -> CityParkingModel:
        if self.use_official_api:
            return await self.getOfficialAddressSeetyInfo(coordinates)

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
        
        seetyStreetRules = self._parse_model(SeetyStreetRules, response)

        
        url = URL(f"https://api.cparkapp.com/street/complete/{formatted_address}/{coordinates.lat}/{coordinates.lon}")
        responseComplete = await self.json_get_with_retry_client(url, header=header)
        
        seetyStreetComplete = self._parse_model(SeetyStreetComplete, responseComplete)

        cityParkingModel: CityParkingModel
        cityParkingModel = CityParkingModel(
            user = seetyUser,
            location = seetyLocationInfo,
            rules = seetyStreetRules, 
            streetComplete = seetyStreetComplete,
            api_mode = API_MODE_LEGACY,
        )
        return cityParkingModel 

    async def getOfficialRulesForCoordinate(self, coordinates: Coords) -> SeetyExternalRulesResponse:
        """Get parking rules from Seety's official external API."""
        if not self.api_key:
            raise ValidationError("Official Seety API key is required")

        url = URL(f"https://api.cparkapp.com/extern/rules/{coordinates.lat}/{coordinates.lon}")
        header={"Content-Type": "application/json", "API-Key": self.api_key}
        response = await self.json_get_with_retry_client(url, header=header)
        seetyExternalRules = self._parse_model(SeetyExternalRulesResponse, response)

        if seetyExternalRules.status != "OK" or not seetyExternalRules.rules:
            raise EmptyResponseError(f"Official Seety API returned status: {seetyExternalRules.status}")

        return seetyExternalRules

    async def getOfficialAddressSeetyInfo(self, coordinates: Coords) -> CityParkingModel:
        """Map official external API rules into the integration model."""
        seetyExternalRules = await self.getOfficialRulesForCoordinate(coordinates)
        return CityParkingModel(
            externalRules=seetyExternalRules,
            api_mode=API_MODE_OFFICIAL,
        )



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
        safe_url = self._redact_sensitive_url(url)
        try:
            async with self.retry_client.get(url, headers=header) as response:
                status = response.status
                reason = response.reason
                headers = dict(response.headers)

                _LOGGER.debug("GET %s -> %s %s", safe_url, status, reason)
                if response.status == 200:
                    result = await response.json(content_type=None)
                    _LOGGER.debug(f"response get url {safe_url}, status: {response.status}, response: {result}")
                    if result:
                        json_response = result
                    else:
                        raise EmptyResponseError()
                elif response.status == 429:
                    raise RateLimitHitError("Rate limit of API has been hit")
                else:
                    self.clearSeetyUserToken()
                    _LOGGER.exception(
                        "HTTPError %s occurred while requesting %s, reason: %s, headers: %s",
                        response.status,
                        safe_url,
                        reason,
                        headers
                    )
        except ValidationError as err:
            self.clearSeetyUserToken()
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
            ) as err:
            self.clearSeetyUserToken()
            # Something else failed
            response_body = await response.text()
            _LOGGER.exception(
                "Error while requesting %s: %s, error: %s",
                safe_url,
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
                    self.clearSeetyUserToken()

                    error_message = await response.text()
                    _LOGGER.exception(
                        "HTTPError %s occurred while requesting %s, error message: %s",
                        response.status,
                        url,
                        error_message
                    )
        except ValidationError as err:
            self.clearSeetyUserToken()
            _LOGGER.error(err)
            raise ValidationError(err)
        except (
            ClientError,
            TimeoutError,
            CancelledError,
        ) as err:
            self.clearSeetyUserToken()
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
