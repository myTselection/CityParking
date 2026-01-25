"""Config flow for integration."""

from __future__ import annotations

from asyncio import CancelledError
from typing import Any


import voluptuous as vol
from aiohttp.client_exceptions import ClientError
from homeassistant import config_entries
from homeassistant.data_entry_flow import section
from homeassistant.helpers.location import find_coordinates
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.selector import (
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    selector, SelectSelector, SelectSelectorConfig
)
from .seetyApi import SeetyApi, EmptyResponseError, ValidationError
# from .location import LocationSession
from pywaze.route_calculator import WazeRouteCalculator

from .const import DOMAIN, CONF_ORIGIN
import logging

_LOGGER = logging.getLogger(__name__)

CITYPARKING_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_ORIGIN): str
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
                unique_id = origin
                resolved_origin = find_coordinates(self.hass, user_input.get(CONF_ORIGIN))
                seetyApi = SeetyApi(websession=async_get_clientsession(self.hass))
                httpx_client = get_async_client(self.hass)
                # session = LocationSession()
                self.routeCalculatorClient = WazeRouteCalculator(region="EU", client=httpx_client)
                _LOGGER.debug(f"resolved origin: {resolved_origin}, {user_input.get(CONF_ORIGIN)}")
                origin_coordinates = await self.routeCalculatorClient._ensure_coords(resolved_origin)
                _LOGGER.debug(f"resolved origin: {resolved_origin}, {user_input.get(CONF_ORIGIN)}, origin_coordinates: {origin_coordinates}")
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
