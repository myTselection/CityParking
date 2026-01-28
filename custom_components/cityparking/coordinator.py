"""Shell Recharge data update coordinators."""

import logging
import asyncio
from asyncio.exceptions import CancelledError

from aiohttp.client_exceptions import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.location import find_coordinates
from .seetyApi import SeetyApi, EmptyResponseError
from .seetyApi.models import Coords, CityParkingModel
# from .location import LocationSession
from pywaze.route_calculator import CalcRoutesResponse, WazeRouteCalculator


from .const import DOMAIN, UPDATE_INTERVAL,CONF_ORIGIN
_LOGGER = logging.getLogger(__name__)
SECONDS_BETWEEN_API_CALLS = 0.5

async def async_find_city_parking_info(
        hass: HomeAssistant,
        seetyApi: SeetyApi,
        routeCalculatorClient: WazeRouteCalculator,
        origin: str
    ) -> list[CalcRoutesResponse]:
    """Get station matching criteria."""

    resolved_origin = find_coordinates(hass,origin)
    origin_coordinates_json = await routeCalculatorClient._ensure_coords(resolved_origin)
    origin_coordinates = Coords.model_validate(origin_coordinates_json)
    _LOGGER.debug(f"EVCS coordinator find origin_coordinates: {origin_coordinates}, resolved_origin: {resolved_origin}, origin: {origin}")
    
    cityParkingInfo:CityParkingModel = await seetyApi.getAddressSeetyInfo(origin_coordinates)
    cityParkingInfo.origin = origin
    cityParkingInfo.origin_coordinates = Coords.model_validate(origin_coordinates)


    # self._attr_name = self.station.name
    extract_readable_info(cityParkingInfo)

    return cityParkingInfo.model_dump()

def extract_readable_info(cityParkingInfo):
    rules = cityParkingInfo.rules.model_dump() if cityParkingInfo.rules else {}
    streetComplete = cityParkingInfo.streetComplete.model_dump() if cityParkingInfo.streetComplete else {}
    locationResults = cityParkingInfo.location.model_dump().get('results', [{}])[0] if cityParkingInfo.location else {}
    _LOGGER.debug(f"Sensor _read_coordinator_data rules: {rules}")
    type = rules.get('rules', {}).get('type', 'unknown')
    zone_type = rules.get('properties', {}).get('type', 'unknown')
    rules_complete_zone = streetComplete.get('rules', {}).get(zone_type, {})
    address = f"{locationResults.get('formatted_address', '')}, {locationResults.get('countryCode', '')}" if locationResults else ''
    origin_coordinates = cityParkingInfo.origin_coordinates.model_dump() if cityParkingInfo.origin_coordinates else {}
    extra_data = {
        "origin": cityParkingInfo.origin,
        "latitude": origin_coordinates.get('lat', ''),
        "longitude": origin_coordinates.get('lon', ''),
        "type": type,
        "time_restrictions": rules.get('rules', {}).get('hours', ""),
        "days_restrictions": days_to_string(rules.get('rules', {}).get('days', [])),
        "prices": prices_to_string(rules.get('rules', {}).get('prices', {})),
        "remarks": " - ".join(rules_complete_zone.get('remarks', "")),
        "maxStay": minutes_to_string(rules_complete_zone.get('maxStay', "")),
        "zone": rules.get('properties', {}).get('type', 'unknown'),
        "address": address,
    }
    cityParkingInfo.extra_data = extra_data


def days_to_string(days):
    names = ['sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat']

    # normalize & sort
    sorted_days = sorted(set(days))

    # 7d/7
    if len(sorted_days) == 7:
        return '7d/7'

    # weekend (sat + sun)
    if len(sorted_days) == 2 and 0 in sorted_days and 6 in sorted_days:
        return 'sat-sun'

    # check consecutive
    consecutive = all(
        sorted_days[i] == sorted_days[i - 1] + 1
        for i in range(1, len(sorted_days))
    )

    if consecutive:
        return f"{names[sorted_days[0]]}-{names[sorted_days[-1]]}"

    # fallback: comma-separated list
    return ",".join(names[d] for d in sorted_days)

def prices_to_string(prices: dict) -> str:
    if not prices:
        return ""

    parts = []

    for hours, price in sorted(prices.items(), key=lambda x: int(x[0])):
        h = int(hours)
        if h > 0:
            parts.append(f"{price}€ ({h}h)")

    return " - ".join(parts)

def minutes_to_string(minutes_str: str) -> str:
    try:
        minutes = int(minutes_str)
    except (ValueError, TypeError):
        return "0m"  # fallback for invalid input

    if minutes <= 0:
        return "0m"

    hours = minutes // 60
    mins = minutes % 60

    if hours == 0:
        return f"{mins}m"
    if mins == 0:
        return f"{hours}h"

    return f"{hours}h {mins}m"

class CityParkingUserDataUpdateCoordinator(DataUpdateCoordinator):
    """Handles data updates for public chargers."""

    config_entry: ConfigEntry

    def __init__(
        self, hass: HomeAssistant, seetyApi: SeetyApi, config_entry: ConfigEntry, routeCalculatorClient: WazeRouteCalculator
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            config_entry=config_entry,
            update_interval=UPDATE_INTERVAL,
        )
        self._seetyApi = seetyApi
        self._origin = config_entry.data.get(CONF_ORIGIN)
        self._routeCalculatorClient = routeCalculatorClient

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        data: CityParkingModel = None
        
        resolved_origin = find_coordinates(self.hass, self._origin)
        origin_coordinates_json = await self._routeCalculatorClient._ensure_coords(resolved_origin)
        origin_coordinates = Coords.model_validate(origin_coordinates_json)
        _LOGGER.info(f"coordinator origin_coordinates: {origin_coordinates}, resolved_origin: {resolved_origin}, origin: {self._origin}")

        try:
            data = await self._seetyApi.getAddressSeetyInfo(origin_coordinates)
            data.origin = self._origin
            data.origin_coordinates = origin_coordinates
            extract_readable_info(data)
            # _LOGGER.debug(f"nearby_stations: {data}")
        except EmptyResponseError as exc:
            _LOGGER.error(
                "Error occurred while fetching data for charger(s) %s, not found, or coordinates are invalid, %s",
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except CancelledError as exc:
            _LOGGER.error(
                "CancelledError occurred while fetching data for charger(s) %s, %s",
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except TimeoutError as exc:
            _LOGGER.error(
                "TimeoutError occurred while fetching data for charger(s) %s, %s",
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except ClientError as exc:
            _LOGGER.error(
                "ClientError occurred while fetching data for charger(s) %s: %s",
                resolved_origin,
                exc,
                exc_info=True,
            )
            raise UpdateFailed() from exc
        except Exception as exc:
            _LOGGER.error(
                "Unexpected error occurred while fetching data for charger(s) %s: %s",
                resolved_origin,
                exc,
                exc_info=True,
            )
            raise UpdateFailed() from exc

        if data is None:
            _LOGGER.error(
                "API returned None data for charger(s) %s",
                resolved_origin,
            )
            raise UpdateFailed("API returned None data")

        return data