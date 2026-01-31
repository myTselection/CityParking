"""Shell Recharge data update coordinators."""

import logging
import asyncio
from asyncio.exceptions import CancelledError
import re

from aiohttp.client_exceptions import ClientError
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.location import find_coordinates
from .seetyApi import SeetyApi, EmptyResponseError
from .seetyApi.models import Coords, CityParkingModel, ParkingSensorType, SeetyLocationResponse, SeetyUser
# from .location import LocationSession
from pywaze.route_calculator import CalcRoutesResponse, WazeRouteCalculator
from typing import List, Tuple


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

    return cityParkingInfo.model_dump()

def extract_readable_info(cityParkingInfo: CityParkingModel):
    rules = cityParkingInfo.rules.model_dump() if cityParkingInfo.rules else {}
    streetComplete = cityParkingInfo.streetComplete.model_dump() if cityParkingInfo.streetComplete else {}
    locationResults = cityParkingInfo.location.model_dump().get('results', [{}])[0] if cityParkingInfo.location else {}
    _LOGGER.debug(f"Sensor _read_coordinator_data rules: {rules}")
    type = rules.get('rules', {}).get('type', 'unknown')
    zone_type = rules.get('properties', {}).get('type', 'unknown')
    display, emoji = name_and_emoji(zone_type)
    rules_complete_zone = streetComplete.get('rules', {}).get(zone_type, {})
    address = f"{locationResults.get('formatted_address', '')}, {locationResults.get('countryCode', '')}" if locationResults else ''
    origin_coordinates = cityParkingInfo.origin_coordinates.model_dump() if cityParkingInfo.origin_coordinates else {}
    extra_data = {
        "origin": cityParkingInfo.origin,
        "latitude": origin_coordinates.get('lat', ''),
        "longitude": origin_coordinates.get('lon', ''),
        ParkingSensorType.TYPE.value: type,
        ParkingSensorType.TIME.value: hours_array_to_string(rules.get('rules', {}).get('hours', [])),
        ParkingSensorType.DAYS.value: days_to_string(rules.get('rules', {}).get('days', [])),
        ParkingSensorType.PRICE.value: prices_to_string(rules.get('rules', {}).get('prices', {})),
        ParkingSensorType.REMARKS.value: " - ".join(rules_complete_zone.get('remarks', "")),
        ParkingSensorType.MAXSTAY.value: minutes_to_string(rules_complete_zone.get('maxStay', "")),
        ParkingSensorType.ZONE.value: f"{display} {emoji}",
        ParkingSensorType.ADDRESS.value: address,
    }
    cityParkingInfo.extra_data = extra_data


def days_to_string(days):
    names = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    # normalize & sort
    sorted_days = sorted(set(days))

    # 7d/7
    if len(sorted_days) == 7:
        return '7d/7'

    # weekend (sat + sun)
    if len(sorted_days) == 2 and 0 in sorted_days and 6 in sorted_days:
        return 'Sat-Sun'

    # check consecutive
    if len(sorted_days) < 2:
        return ",".join(names[d] for d in sorted_days)

    consecutive = all(
        sorted_days[i] == sorted_days[i - 1] + 1
        for i in range(1, len(sorted_days))
    )

    if consecutive:
        return f"{names[sorted_days[0]]}-{names[sorted_days[-1]]}"

    # fallback: comma-separated list
    return ",".join(names[d] for d in sorted_days)


def hours_array_to_string(hours: List[str]) -> str:
    if not hours or len(hours) != 2:
        return ""

    start, end = hours

    # Full-day special case
    if start == "00:00" and end == "24:00":
        return "24h/24"

    return f"{start} - {end}"


def prices_to_string(prices: dict) -> str:
    if not prices:
        return ""

    parts = []

    for hours, price in sorted(prices.items(), key=lambda x: int(x[0])):
        h = int(hours)
        if h == 0 and price != 0:
            parts.append(f"Free: {int(price)}min")
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


# Canonical display name + emoji
_CANONICAL = {
    "blue": ("Blue", "🔵"),
    "orange": ("Orange", "🟠"),
    "orange-dark": ("Orange (dark)", "🟠"),
    "orange-2": ("Orange (variant)", "🟠"),
    "pedestrian": ("Pedestrian", "🚶"),
    "pink": ("Pink", "🩷"),
    "red": ("Red", "🔴"),
    "resident": ("Resident", "🏠"),
    "yellow": ("Yellow", "🟡"),
    "yellow-dark": ("Yellow (dark)", "🟡"),
    "yellow-dotted": ("Yellow (dotted)", "🟡"),
    "yellow-dark-dotted": ("Yellow (dark, dotted)", "🟡"),
    "no-parking": ("No parking", "🚫"),
    "freeinv": ("Free", "🆓"),       # best-effort interpretation
    "disabled": ("Disabled", "♿"),
}

# Aliases mapped to canonical keys (add more aliases here as needed)
_ALIASES = {
    "blue": ["blue"],
    "freeinv": ["freeinv", "free-inv", "free_inv", "free", "inv"],
    "no-parking": ["noparking", "no-parking", "no_parking", "no parking"],
    "orange": ["orange", "oranged", "orange1"],
    "orange-dark": ["orangedark", "orange-dark", "orange_dark"],
    "orange-2": ["orange-2", "orange2", "orange variant"],
    "pedestrian": ["pedestrian", "pedestrain"],  # common misspelling included
    "pink": ["pink"],
    "red": ["red"],
    "resident": ["resident", "residents", "residentship"],
    "yellow": ["yellow"],
    "yellow-dark": ["yellowdark", "yellow-dark", "yellow_dark"],
    "yellow-dotted": ["yellowdotted", "yellow-dotted", "yellow_dotted"],
    "yellow-dark-dotted": [
        "yellowdarkdotted",
        "yellow-dark-dotted",
        "yellow_dark_dotted",
    ],
    "disabled": ["disabled", "disability", "wheelchair", "wheel-chair"],
}

# Build quick lookup dict from alias -> canonical
_ALIAS_LOOKUP = {}
for canonical_key, aliases in _ALIASES.items():
    for a in aliases:
        # store several normalized variants for each alias
        norm = a.lower()
        _ALIAS_LOOKUP[norm] = canonical_key
        _ALIAS_LOOKUP[re.sub(r"[^a-z0-9]", "", norm)] = canonical_key  # compact form
        _ALIAS_LOOKUP[norm.replace("-", " ")] = canonical_key


def _normalize_key(raw: str) -> str:
    """Normalize a raw input key into a canonical lookup form."""
    if raw is None:
        return ""
    s = str(raw).strip().lower()
    # remove surrounding quotes if any
    s = s.strip("\"'` ")
    # collapse whitespace and common separators to single hyphen
    s = re.sub(r"[ _]+", "-", s)
    s = re.sub(r"[^a-z0-9\-]", "", s)
    # special-case trailing 's' (plural) -> try singular
    if s.endswith("s") and (s[:-1] in _ALIAS_LOOKUP or s[:-1] in _CANONICAL):
        s = s[:-1]
    return s


def name_and_emoji(raw_name: str) -> Tuple[str, str]:
    """
    Return a tuple (clean_display_name, emoji) for a raw key like "blue" or "orange-2".
    Falls back to capitalized raw_name and a default emoji if unknown.
    """
    norm = _normalize_key(raw_name)
    # direct canonical match
    if norm in _CANONICAL:
        return _CANONICAL[norm]

    # alias lookup
    if norm in _ALIAS_LOOKUP:
        canon = _ALIAS_LOOKUP[norm]
        return _CANONICAL.get(canon, (canon.capitalize(), "🔖"))

    # try compact form (remove hyphens)
    compact = re.sub(r"[^a-z0-9]", "", norm)
    if compact in _ALIAS_LOOKUP:
        canon = _ALIAS_LOOKUP[compact]
        return _CANONICAL.get(canon, (canon.capitalize(), "🔖"))

    # try removing trailing digits (e.g., "orange2" -> "orange")
    no_digits = re.sub(r"\d+$", "", compact)
    if no_digits in _ALIAS_LOOKUP:
        canon = _ALIAS_LOOKUP[no_digits]
        return _CANONICAL.get(canon, (canon.capitalize(), "🔖"))

    # final fallback: pretty-print the raw string and use a neutral emoji
    pretty = raw_name.strip().replace("_", " ").replace("-", " ").title()
    return pretty, "🔖"

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