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
from .seetyApi.models import CityParkingModel
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
    origin_coordinates = await routeCalculatorClient._ensure_coords(resolved_origin)
    _LOGGER.debug(f"EVCS coordinator find origin_coordinates: {origin_coordinates}, resolved_origin: {resolved_origin}, origin: {origin}")
    
    cityParkingInfo:CityParkingModel = await seetyApi.getAddressSeetyInfo(origin_coordinates)

    return cityParkingInfo.model_dump()



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
        origin_coordinates = await self._routeCalculatorClient._ensure_coords(resolved_origin)
        _LOGGER.info(f"coordinator origin_coordinates: {origin_coordinates}, resolved_origin: {resolved_origin}, origin: {self._origin}")
        try:
            data = await self._seetyApi.getAddressSeetyInfo(origin_coordinates)
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