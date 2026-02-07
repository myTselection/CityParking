"""Shell Recharge data update coordinators."""

from copy import deepcopy
import logging
import asyncio
from asyncio.exceptions import CancelledError

from aiohttp.client_exceptions import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.location import find_coordinates
from homeassistant.util import dt as dt_util
from .seetyApi import SeetyApi, EmptyResponseError
from .seetyApi.models import *
from .seetyApi.extract_info import *
# from .location import LocationSession
from pywaze.route_calculator import CalcRoutesResponse, WazeRouteCalculator

from .const import DOMAIN, UPDATE_INTERVAL,CONF_ORIGIN
_LOGGER = logging.getLogger(__name__)
SECONDS_BETWEEN_API_CALLS = 0.5
MAX_RESULT_AGE = 30

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
    update_restriction_status(cityParkingInfo, dt_util.now())

    return cityParkingInfo.model_dump()



def update_restriction_status(cityParkingInfo: CityParkingModel, update_time: dt_util.dt.datetime = None):
    """Update restriction status based on current time."""
    time_restriction = cityParkingInfo.extra_data.get(ParkingSensorType.TIME.value + "_src", None)
    days_restriction = cityParkingInfo.extra_data.get(ParkingSensorType.DAYS.value + "_src", None)
    max_stay = cityParkingInfo.extra_data.get(ParkingSensorType.MAXSTAY.value + "_src", None)
    is_active_now = is_hours_active_now(time_restriction)
    is_active_today = is_days_active_today(days_restriction)
    is_restriction_active = is_active_now and is_active_today
    is_max_stay_passed_value, max_stay_elapsed, max_stay_remaining = is_max_stay_passed(start_dt=update_time, max_minutes=max_stay)
    extra_data = cityParkingInfo.extra_data if cityParkingInfo.extra_data else {}
    extra_data.update({
        TIME_RESTRICTION_ACTIVE_NOW: is_active_now,
        DAY_RESTRICTION_ACTIVE_NOW: is_active_today,
        MAXSTAY_PASSED_NOW: is_max_stay_passed_value,
        MAXSTAY_ELAPSED: max_stay_elapsed,
        MAXSTAY_REMAINING: max_stay_remaining,
        MAXSTAY_START_TIME: update_time,
        RESTRICTION_ACTIVE: is_restriction_active,
        LAST_UPDATE: update_time,
        LAST_RESTRICTION_CHECK: dt_util.now(),
    })
    cityParkingInfo.extra_data = extra_data


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
        self._previousResults : CityParkingModel = None
        self._previousCoordinates : Coords = None
        self._previousResultAge = 0
        self._previousUpdate = None

    # async def async_set_stay_start(self, unique_id: str, start_iso: str) -> None:
    #     """Set stay_start for a specific parking entry and notify listeners."""
    #     new_data = deepcopy(self.data)

    #     self._previousUpdate = start_iso
    #     self._previousResultAge = 0
    #     self._previousResults = new_data.get(unique_id, {})

    #     # Example for dict-based data:
    #     item = dict(new_data.get(unique_id, {}))
    #     extra = dict(item.get("extra_data", {}))
    #     extra["stay_start"] = start_iso
    #     item["extra_data"] = extra
    #     new_data[unique_id] = item

    #     # Atomically set new coordinator data which triggers updates
    #     await self.async_set_updated_data(new_data)
        
    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        data: CityParkingModel = None
        _LOGGER.debug("Coordinator _async_update_data called, origin: %s", self._origin)
        resolved_origin = find_coordinates(self.hass, self._origin)
        origin_coordinates_json = await self._routeCalculatorClient._ensure_coords(resolved_origin)
        origin_coordinates = Coords.model_validate(origin_coordinates_json)
        _LOGGER.info(f"coordinator origin_coordinates: {origin_coordinates}, resolved_origin: {resolved_origin}, origin: {self._origin}, previousCoordinates: {self._previousCoordinates}")


        self._previousResultAge += 1
        if self._previousResults is not None and self._previousCoordinates == origin_coordinates and (self._previousResultAge < MAX_RESULT_AGE):
            _LOGGER.debug("Coordinator _async_update_data using cached previousResults, no coordinate change detected.")
            # extend / update seety info with actual restriction status
            update_restriction_status(self._previousResults, self._previousUpdate)
            return self._previousResults
        try:
            data = await self._seetyApi.getAddressSeetyInfo(origin_coordinates)
            data.origin = self._origin
            data.origin_coordinates = origin_coordinates
            extract_readable_info(data)
            # _LOGGER.debug(f"nearby_stations: {data}")
            self._previousResults = data
            self._previousCoordinates = origin_coordinates
            self._previousResultAge = 0
            self._previousUpdate = dt_util.now()
            # extend / update seety info with actual restriction status
            update_restriction_status(data, self._previousUpdate)
        except EmptyResponseError as exc:
            _LOGGER.error(
                "EmptyResponseError occurred while fetching data for %s (%s): %s",
                self._origin,
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except CancelledError as exc:
            _LOGGER.error(
                "CancelledError occurred while fetching data for %s (%s): %s",
                self._origin,
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except TimeoutError as exc:
            _LOGGER.error(
                "TimeoutError occurred while fetching data for %s (%s): %s",
                self._origin,
                resolved_origin, exc
            )
            raise UpdateFailed() from exc
        except ClientError as exc:
            _LOGGER.error(
                "ClientError error occurred while fetching data for %s (%s): %s",
                self._origin,
                resolved_origin,
                exc,
                exc_info=True,
            )
            raise UpdateFailed() from exc
        except Exception as exc:
            _LOGGER.error(
                "Unexpected error occurred while fetching data for %s (%s): %s",
                self._origin,
                resolved_origin,
                exc,
                exc_info=True,
            )
            raise UpdateFailed() from exc

        if data is None:
            _LOGGER.error(
                "API returned None data for %s (%s)",
                self._origin,
                resolved_origin)
            raise UpdateFailed(f"API returned None data for {self._origin} ({resolved_origin})")

        return data