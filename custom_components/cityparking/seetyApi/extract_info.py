
import logging
import re
from typing import List, Tuple, Union
from urllib.parse import unquote, urlparse

from datetime import datetime, time
from custom_components.cityparking.const import API_MODE_OFFICIAL
from custom_components.cityparking.seetyApi.models import CityParkingModel, ParkingSensorType
from homeassistant.util import dt as dt_util
from typing import List


_LOGGER = logging.getLogger(__name__)

def extract_readable_info(cityParkingInfo: CityParkingModel):
    if getattr(cityParkingInfo.externalRules, "status", None):
        extract_official_readable_info(cityParkingInfo)
        return

    rules = cityParkingInfo.rules.model_dump() if cityParkingInfo.rules else {}
    streetComplete = cityParkingInfo.streetComplete.model_dump() if cityParkingInfo.streetComplete else {}
    locationResults = cityParkingInfo.location.model_dump().get('results', [{}])[0] if cityParkingInfo.location else {}
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
        "url": f"https://map.seety.co/{address}/16?lang=en",
        ParkingSensorType.TYPE.value: type,
        ParkingSensorType.TIME.value: hours_array_to_string(rules.get('rules', {}).get('hours', [])),
        ParkingSensorType.DAYS.value: days_to_string(rules.get('rules', {}).get('days', [])),
        ParkingSensorType.PRICE.value: prices_to_string(rules.get('rules', {}).get('prices', {})),
        ParkingSensorType.REMARKS.value: " - ".join(rules_complete_zone.get('remarks', ""))[:254],
        ParkingSensorType.MAXSTAY.value: minutes_to_string(rules_complete_zone.get('maxStay', "")),
        ParkingSensorType.ZONE.value: f"{display} {emoji}",
        ParkingSensorType.ADDRESS.value: address,

        ParkingSensorType.TYPE.value + "_src": rules.get('rules', {}).get('type', ''),
        ParkingSensorType.TIME.value + "_src": rules.get('rules', {}).get('hours', []),
        ParkingSensorType.DAYS.value + "_src": rules.get('rules', {}).get('days', []),
        ParkingSensorType.PRICE.value + "_src": rules.get('rules', {}).get('prices', {}),
        ParkingSensorType.REMARKS.value + "_src": rules_complete_zone.get('remarks', ""),
        ParkingSensorType.MAXSTAY.value + "_src": rules_complete_zone.get('maxStay', ""),
        ParkingSensorType.ZONE.value + "_src": zone_type,
        ParkingSensorType.ADDRESS.value + "_src": f"{locationResults.get('formatted_address', '')}",
    }
    cityParkingInfo.extra_data = extra_data


def extract_official_readable_info(cityParkingInfo: CityParkingModel):
    external_rules = cityParkingInfo.externalRules
    rules = external_rules.rules if external_rules else None
    prices = rules.prices if rules else {}
    hours = rules.hours if rules else []
    days = rules.days if rules else []
    max_stay = rules.maxStay if rules else None
    zone_type = rules.type if rules else "unknown"
    display, emoji = name_and_emoji(zone_type or "unknown")
    url = external_rules.mapURL if external_rules else None
    address = address_from_map_url(url) or cityParkingInfo.origin or ""
    origin_coordinates = cityParkingInfo.origin_coordinates.model_dump() if cityParkingInfo.origin_coordinates else {}
    remarks = []
    if rules and rules.hasException:
        remarks.append("Exceptions may apply. Check the Seety map.")

    extra_data = {
        "origin": cityParkingInfo.origin,
        "latitude": origin_coordinates.get('lat', ''),
        "longitude": origin_coordinates.get('lon', ''),
        "url": url,
        "api_mode": API_MODE_OFFICIAL,
        "has_exception": rules.hasException if rules else False,
        ParkingSensorType.TYPE.value: zone_type,
        ParkingSensorType.TIME.value: hours_array_to_string(hours),
        ParkingSensorType.DAYS.value: days_to_string(days),
        ParkingSensorType.PRICE.value: official_prices_to_string(prices),
        ParkingSensorType.REMARKS.value: " - ".join(remarks)[:254],
        ParkingSensorType.MAXSTAY.value: minutes_to_string(max_stay),
        ParkingSensorType.ZONE.value: f"{display} {emoji}",
        ParkingSensorType.ADDRESS.value: address,

        ParkingSensorType.TYPE.value + "_src": zone_type,
        ParkingSensorType.TIME.value + "_src": hours,
        ParkingSensorType.DAYS.value + "_src": days,
        ParkingSensorType.PRICE.value + "_src": prices,
        ParkingSensorType.REMARKS.value + "_src": remarks,
        ParkingSensorType.MAXSTAY.value + "_src": max_stay,
        ParkingSensorType.ZONE.value + "_src": zone_type,
        ParkingSensorType.ADDRESS.value + "_src": address,
    }
    cityParkingInfo.extra_data = extra_data


def address_from_map_url(map_url: str) -> str:
    if not map_url:
        return ""

    try:
        path = urlparse(map_url).path.strip("/")
        if not path:
            return ""
        return unquote(path.split("/")[0])
    except ValueError:
        return ""

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


def is_days_active_today(days) -> bool:
    """
    Returns True if today is included in the given days restriction.

    Day indexing matches days_to_string:
        0 = Sun, 1 = Mon, ..., 6 = Sat
    """
    if not days:
        return False

    # Normalize & deduplicate
    try:
        normalized_days = {int(d) for d in days if 0 <= int(d) <= 6}
    except (TypeError, ValueError):
        return False

    # Current local date/time (HA timezone + DST safe)
    now = dt_util.now()

    # Python weekday(): Mon=0..Sun=6
    # Convert to Sun=0..Sat=6
    today = (now.weekday() + 1) % 7

    # Shortcut for 7d/7
    if len(normalized_days) == 7:
        return True

    return today in normalized_days

def hours_array_to_string(hours: List[str]) -> str:
    if not hours or len(hours) < 2 or len(hours) % 2 != 0:
        return ""

    ranges = []
    for i in range(0, len(hours), 2):
        start, end = hours[i], hours[i + 1]

        # Full-day special case
        if start == "00:00" and end == "24:00":
            ranges.append("24h/24")
        else:
            ranges.append(f"{start} - {end}")

    return ", ".join(ranges)

def is_hours_active_now(hours):
    if not hours or len(hours) < 2 or len(hours) % 2 != 0:
        return False

    for i in range(0, len(hours), 2):
        if is_hour_range_active_now(hours[i], hours[i + 1]):
            return True

    return False


def is_hour_range_active_now(start_str, end_str):

    # 24h/24
    if start_str == "00:00" and end_str == "24:00":
        return True

    try:
        sh, sm = map(int, start_str.split(":"))
        eh, em = map(int, end_str.split(":"))
    except (ValueError, AttributeError):
        return False

    now = dt_util.now().time()
    start = time(sh, sm)
    end = time(23, 59, 59) if end_str == "24:00" else time(eh, em)

    if start < end:
        return start <= now < end

    # overnight range
    return now >= start or now < end


def official_prices_to_string(prices: dict) -> str:
    if not prices:
        return ""

    parts = []
    free_time = prices.get("freeTime")
    if free_time:
        try:
            parts.append(f"Free: {int(float(free_time))}min")
        except (TypeError, ValueError):
            pass

    price_entries = []
    for duration, price in prices.items():
        if duration == "freeTime":
            continue
        try:
            price_entries.append((int(duration), price))
        except (TypeError, ValueError):
            continue

    for duration, price in sorted(price_entries, key=lambda item: item[0]):
        parts.append(f"{format_price(price)} EUR ({minutes_to_string(duration)})")

    return " - ".join(parts)


def format_price(price) -> str:
    try:
        price_float = float(price)
    except (TypeError, ValueError):
        return str(price)

    if price_float.is_integer():
        return str(int(price_float))
    return str(price_float)


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


def is_max_stay_passed(
    start_dt: Union[datetime, None],
    max_minutes: Union[int, str, None],
) -> Tuple[bool, int, int]:
    """
    Determine if a max-stay window has been exceeded.

    Args:
      start_dt: a datetime set by your integration (aware or naive). If naive,
                it's interpreted as local Home Assistant time.
      max_minutes: allowed max stay in minutes (int or string). Non-positive or None => no limit.

    Returns:
      (passed: bool, elapsed_seconds: int, remaining_seconds: int)

    Behavior notes:
    - Uses Home Assistant local time (dt_util.now()).
    - If start_dt is None -> (False, 0, 0).
    - If max_minutes is invalid/non-positive -> treated as "no limit" -> (False, 0, 0).
    - If start is in future -> elapsed_seconds = 0, remaining_seconds = max_minutes*60.
    """
    # Validate max_minutes
    try:
        max_min = int(max_minutes) if max_minutes is not None else 0
    except (ValueError, TypeError):
        max_min = 0

    if max_min <= 0:
        return False, 0, 0

    if start_dt is None:
        return False, 0, 0

    # Ensure start_dt is a datetime and convert to HA-local timezone
    if not isinstance(start_dt, datetime):
        return False, 0, 0

    # If naive, assume it's local (since integration sets it); convert to local aware
    if start_dt.tzinfo is None:
        # treat naive as local HA time
        start_local = dt_util.as_local(start_dt)
    else:
        # make sure it's in local timezone
        start_local = dt_util.as_local(start_dt)

    now_local = dt_util.now()  # HA local aware datetime

    elapsed_td = now_local - start_local
    elapsed_seconds = int(elapsed_td.total_seconds())

    # If start in future -> not started yet
    if elapsed_seconds < 0:
        return False, 0, max_min * 60

    limit_seconds = max_min * 60
    remaining_seconds = max(0, limit_seconds - elapsed_seconds)
    passed = elapsed_seconds > limit_seconds

    return passed, elapsed_seconds // 60, remaining_seconds // 60


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
