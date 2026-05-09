"""The shell_recharge integration."""

from __future__ import annotations

import logging

# import evrecharge
from .seetyApi import SeetyApi
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import (
    HomeAssistant,
    ServiceCall,
    ServiceResponse,
    SupportsResponse,
)
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.httpx_client import get_async_client
from homeassistant.helpers.location import find_coordinates

from .const import (
    API_MODE_LEGACY,
    API_MODE_OFFICIAL,
    CONF_API_KEY,
    CONF_API_MODE,
    CONF_ORIGIN,
    DOMAIN,
)
from .coordinator import (
    CityParkingUserDataUpdateCoordinator,
    async_find_city_parking_info
)
from pywaze.route_calculator import WazeRouteCalculator
import voluptuous as vol
from homeassistant.helpers.selector import (
    BooleanSelector,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
    NumberSelector,
)

_LOGGER = logging.getLogger(DOMAIN)
PLATFORMS: list[Platform] = [Platform.SENSOR]

SERVICE_CITY_PARKING_INFO = "city_parking_info"
SERVICE_CITY_PARKING_INFO_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ORIGIN): TextSelector(),
        vol.Optional(CONF_API_MODE): SelectSelector(
            SelectSelectorConfig(options=[API_MODE_LEGACY, API_MODE_OFFICIAL])
        ),
        vol.Optional(CONF_API_KEY): TextSelector(
            TextSelectorConfig(type=TextSelectorType.PASSWORD)
        ),
    }
)

async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate old entry."""
    _LOGGER.debug("Migrating configuration from %s", entry.version)

    if entry.version == 2:
        new_data = dict(entry.data)
        new_data["single"] = {"serial_number": new_data.pop("serial_number")}
    else:
        return True

    hass.config_entries.async_update_entry(entry, data=new_data, version=3)

    _LOGGER.debug("Migration to configuration version %s successful", entry.version)

    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up from a config entry."""

    hass.data.setdefault(DOMAIN, {})

    seetyApi = SeetyApi(
        websession=async_get_clientsession(hass),
        api_mode=entry.data.get(CONF_API_MODE, API_MODE_LEGACY),
        api_key=entry.data.get(CONF_API_KEY),
    )

    coordinator: CityParkingUserDataUpdateCoordinator
    httpx_client = get_async_client(hass)
    routeCalculatorClient = WazeRouteCalculator(region="EU", client=httpx_client)
    coordinator = CityParkingUserDataUpdateCoordinator(hass, seetyApi, entry, routeCalculatorClient)

    hass.data[DOMAIN][entry.entry_id] = coordinator
    await coordinator.async_config_entry_first_refresh()
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


    async def async_find_city_parking_info_service(service: ServiceCall) -> ServiceResponse:
        httpx_client = get_async_client(hass)
        routeCalculatorClient = WazeRouteCalculator(region="EU", client=httpx_client)

        origin = service.data[CONF_ORIGIN]
        service_api_mode = service.data.get(
            CONF_API_MODE, entry.data.get(CONF_API_MODE, API_MODE_LEGACY)
        )
        service_api_key = service.data.get(CONF_API_KEY, entry.data.get(CONF_API_KEY))
        service_seety_api = seetyApi
        if service_api_mode != seetyApi.api_mode or service_api_key != seetyApi.api_key:
            service_seety_api = SeetyApi(
                websession=async_get_clientsession(hass),
                api_mode=service_api_mode,
                api_key=service_api_key,
            )


        response = await async_find_city_parking_info(
            hass=hass,
            seetyApi=service_seety_api,
            origin=origin,
            routeCalculatorClient=routeCalculatorClient
        )
        return {"city_parking_info": response}

    hass.services.async_register(
        DOMAIN,
        SERVICE_CITY_PARKING_INFO,
        async_find_city_parking_info_service,
        SERVICE_CITY_PARKING_INFO_SCHEMA,
        supports_response=SupportsResponse.ONLY,
    )
    return True


async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    try:
        for platform in PLATFORMS:
            await hass.config_entries.async_forward_entry_unload(entry, platform)
            _LOGGER.info("Successfully removed sensor from the integration")
    except ValueError:
        pass

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    # Flag that a reload is in progress
    _LOGGER.info("async_remove_entry " + entry.entry_id)
    hass.data[DOMAIN]["reloading"] = True

    unload_ok: bool = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    hass.data[DOMAIN].pop("reloading", None)

    for entry in hass.config_entries.async_entries(DOMAIN):
        _LOGGER.info("async_unload_entry still set: " + entry.entry_id)
    for entry in hass.data[DOMAIN].keys():
        _LOGGER.info("async_unload_entry still set: " + entry)
    return unload_ok
