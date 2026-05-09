"""Config flow for integration."""

from __future__ import annotations

from asyncio import CancelledError
from typing import Any


import voluptuous as vol
from aiohttp.client_exceptions import ClientError
from homeassistant import config_entries
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
from .seetyApi import SeetyApi, EmptyResponseError, ValidationError
from .seetyApi.models import Coords
# from .location import LocationSession
from pywaze.route_calculator import WazeRouteCalculator

from .const import (
    API_MODE_LEGACY,
    API_MODE_OFFICIAL,
    CONF_API_KEY,
    CONF_API_MODE,
    CONF_ORIGIN,
    DOMAIN,
)
import logging

_LOGGER = logging.getLogger(DOMAIN)

CITYPARKING_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ORIGIN): str,
        vol.Optional(CONF_API_MODE, default=API_MODE_LEGACY): SelectSelector(
            SelectSelectorConfig(options=[API_MODE_LEGACY, API_MODE_OFFICIAL])
        ),
        vol.Optional(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)


class CityParkingFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV charging stations."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=CITYPARKING_SCHEMA)

        try:
            if user_input.get(CONF_ORIGIN):
                origin = user_input[CONF_ORIGIN]
                api_mode = user_input.get(CONF_API_MODE, API_MODE_LEGACY)
                api_key = user_input.get(CONF_API_KEY)
                unique_id = origin if api_mode == API_MODE_LEGACY else f"{origin}_{api_mode}"
                if api_mode == API_MODE_OFFICIAL and not api_key:
                    errors["base"] = "missing_api_key"
                    return self.async_show_form(
                        step_id="user", data_schema=CITYPARKING_SCHEMA, errors=errors
                    )

                resolved_origin = find_coordinates(self.hass, user_input.get(CONF_ORIGIN))
                seetyApi = SeetyApi(
                    websession=async_get_clientsession(self.hass),
                    api_mode=api_mode,
                    api_key=api_key,
                )
                httpx_client = get_async_client(self.hass)
                # session = LocationSession()
                self.routeCalculatorClient = WazeRouteCalculator(region="EU", client=httpx_client)
                _LOGGER.debug(f"resolved origin: {resolved_origin}, {user_input.get(CONF_ORIGIN)}")
                origin_coordinates = await self.routeCalculatorClient._ensure_coords(resolved_origin)
                _LOGGER.debug(f"resolved origin: {resolved_origin}, {user_input.get(CONF_ORIGIN)}, origin_coordinates: {origin_coordinates}")
                if api_mode == API_MODE_OFFICIAL:
                    await seetyApi.getOfficialRulesForCoordinate(Coords(**origin_coordinates))
                else:
                    await seetyApi.getSeetyToken()
            else:
                errors["base"] = "missing_data"
                return self.async_show_form(
                    step_id="user", data_schema=CITYPARKING_SCHEMA, errors=errors
                )
        except EmptyResponseError:
            errors["base"] = "empty_response"
        except ValidationError:
            errors["base"] = "validation"
        except (ClientError, TimeoutError, CancelledError):
            errors["base"] = "cannot_connect"

        if not errors:
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured(updates=user_input)
            return self.async_create_entry(
                title=f"CityParking {unique_id}",
                data=user_input,
            )

        return self.async_show_form(
            step_id="user", data_schema=CITYPARKING_SCHEMA, errors=errors
        )
