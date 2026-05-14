"""Config flow for integration."""

from __future__ import annotations

from asyncio import CancelledError
from typing import Any


import voluptuous as vol
from aiohttp.client_exceptions import ClientError
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.location import find_coordinates
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    SelectSelector,
    SelectSelectorConfig,
)
from .seetyApi import SeetyApi, EmptyResponseError, ValidationError, RateLimitHitError
from .seetyApi.models import Coords
# from .location import LocationSession
from pywaze.route_calculator import WazeRouteCalculator

from .const import (
    API_MODE_LEGACY,
    API_MODE_OFFICIAL,
    CONF_API_KEY,
    CONF_API_MODE,
    CONF_GEOAPIFY_API_KEY,
    CONF_ORIGIN,
    DEFAULT_SEETY_API_KEY,
    DOMAIN,
)
import logging

_LOGGER = logging.getLogger(__name__)

CITYPARKING_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ORIGIN): str,
        vol.Optional(CONF_API_MODE, default=API_MODE_OFFICIAL): SelectSelector(
            SelectSelectorConfig(options=[API_MODE_LEGACY, API_MODE_OFFICIAL])
        ),
        vol.Required(CONF_GEOAPIFY_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)

def config_entry_data(config_entry: config_entries.ConfigEntry) -> dict[str, Any]:
    """Return current config values with options taking precedence."""
    return {**config_entry.data, **config_entry.options}


def options_schema(config_entry: config_entries.ConfigEntry) -> vol.Schema:
    """Build options schema with current values as defaults."""
    current = config_entry_data(config_entry)
    return vol.Schema(
        {
            vol.Required(CONF_ORIGIN, default=current.get(CONF_ORIGIN, "")): str,
            vol.Required(
                CONF_API_MODE,
                default=current.get(CONF_API_MODE) or API_MODE_OFFICIAL,
            ): SelectSelector(
                SelectSelectorConfig(options=[API_MODE_LEGACY, API_MODE_OFFICIAL])
            ),
            vol.Required(
                CONF_API_KEY,
                default=current.get(CONF_API_KEY) or DEFAULT_SEETY_API_KEY,
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
            vol.Required(
                CONF_GEOAPIFY_API_KEY,
                default=current.get(CONF_GEOAPIFY_API_KEY) or "",
            ): TextSelector(TextSelectorConfig(type=TextSelectorType.PASSWORD)),
        }
    )


async def validate_config(
    hass,
    user_input: dict[str, Any],
    validate_legacy_token: bool = False,
) -> tuple[str, dict[str, Any]]:
    """Validate config values and return the unique id plus normalized data."""
    if not user_input.get(CONF_ORIGIN):
        raise MissingDataError()

    entry_data = dict(user_input)
    entry_data[CONF_API_MODE] = entry_data.get(CONF_API_MODE, API_MODE_LEGACY)
    entry_data[CONF_API_KEY] = (
        entry_data.get(CONF_API_KEY) or DEFAULT_SEETY_API_KEY
    ).strip()
    entry_data[CONF_GEOAPIFY_API_KEY] = (
        entry_data.get(CONF_GEOAPIFY_API_KEY) or ""
    ).strip()

    if not entry_data[CONF_GEOAPIFY_API_KEY]:
        raise MissingGeoapifyApiKeyError()
    if entry_data[CONF_API_MODE] == API_MODE_OFFICIAL and not entry_data[CONF_API_KEY]:
        raise MissingApiKeyError()

    resolved_origin = find_coordinates(hass, entry_data[CONF_ORIGIN])
    seetyApi = SeetyApi(
        websession=async_get_clientsession(hass),
        api_mode=entry_data[CONF_API_MODE],
        api_key=entry_data[CONF_API_KEY],
        geoapify_api_key=entry_data[CONF_GEOAPIFY_API_KEY],
    )
    httpx_client = get_async_client(hass)
    route_calculator_client = WazeRouteCalculator(region="EU", client=httpx_client)
    _LOGGER.debug("resolved origin: %s, %s", resolved_origin, entry_data[CONF_ORIGIN])
    origin_coordinates = await route_calculator_client._ensure_coords(resolved_origin)
    _LOGGER.debug(
        "resolved origin: %s, %s, origin_coordinates: %s",
        resolved_origin,
        entry_data[CONF_ORIGIN],
        origin_coordinates,
    )
    if entry_data[CONF_API_MODE] == API_MODE_OFFICIAL:
        await seetyApi.getOfficialRulesForCoordinate(Coords(**origin_coordinates))
        _LOGGER.debug(
            "API_MODE_OFFICIAL coordinates validation successful: %s, %s, origin_coordinates: %s",
            resolved_origin,
            entry_data[CONF_ORIGIN],
            origin_coordinates,
        )
    elif validate_legacy_token:
        await seetyApi.getSeetyToken()
        _LOGGER.debug(
            "MODE_LEGACY coordinates validation successful: %s, %s, origin_coordinates: %s",
            resolved_origin,
            entry_data[CONF_ORIGIN],
            origin_coordinates,
        )

    unique_id = (
        entry_data[CONF_ORIGIN]
        if entry_data[CONF_API_MODE] == API_MODE_LEGACY
        else f"{entry_data[CONF_ORIGIN]}_{entry_data[CONF_API_MODE]}"
    )
    return unique_id, entry_data


class CityParkingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV charging stations."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> CityParkingOptionsFlowHandler:
        """Create the options flow."""
        return CityParkingOptionsFlowHandler(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=CITYPARKING_SCHEMA)

        try:
            unique_id, entry_data = await validate_config(
                self.hass,
                user_input,
                validate_legacy_token=True,
            )
        except RateLimitHitError:
            errors["base"] = "rate_limit_hit"
        except MissingDataError:
            errors["base"] = "missing_data"
        except MissingGeoapifyApiKeyError:
            errors["base"] = "missing_geoapify_api_key"
        except MissingApiKeyError:
            errors["base"] = "missing_api_key"
        except EmptyResponseError:
            errors["base"] = "empty_response"
        except ValidationError:
            errors["base"] = "validation"
        except (ClientError, TimeoutError, CancelledError):
            errors["base"] = "cannot_connect"

        if not errors:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(updates=entry_data)
            return self.async_create_entry(
                title=f"CityParking {unique_id}",
                data=entry_data,
            )

        return self.async_show_form(
            step_id="user", data_schema=CITYPARKING_SCHEMA, errors=errors
        )


class CityParkingOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle City Parking options."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Manage City Parking options."""
        errors: dict[str, str] = {}

        if user_input is None:
            return self.async_show_form(
                step_id="init",
                data_schema=options_schema(self.config_entry),
            )

        try:
            _, entry_data = await validate_config(
                self.hass,
                user_input,
                validate_legacy_token=True,
            )
        except MissingDataError:
            errors["base"] = "missing_data"
        except MissingGeoapifyApiKeyError:
            errors["base"] = "missing_geoapify_api_key"
        except MissingApiKeyError:
            errors["base"] = "missing_api_key"
        except EmptyResponseError:
            errors["base"] = "empty_response"
        except ValidationError:
            errors["base"] = "validation"
        except (ClientError, TimeoutError, CancelledError):
            errors["base"] = "cannot_connect"

        if not errors:
            return self.async_create_entry(title="", data=entry_data)

        return self.async_show_form(
            step_id="init",
            data_schema=options_schema(self.config_entry),
            errors=errors,
        )


class MissingDataError(Exception):
    """Raised when required config data is missing."""


class MissingApiKeyError(Exception):
    """Raised when Seety API key is missing."""


class MissingGeoapifyApiKeyError(Exception):
    """Raised when Geoapify API key is missing."""
