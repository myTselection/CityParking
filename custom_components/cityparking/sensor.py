"""Sensors for the shell_recharge integration."""

from __future__ import annotations

import logging
import typing
from typing import Any

# import evrecharge
import voluptuous as vol
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.components.text import TextEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .seetyApi.models import CityParkingModel

from . import (
    CityParkingUserDataUpdateCoordinator
)
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up a sensor entry."""

    if not hass.data[DOMAIN].get("_service_registered"):
        platform = entity_platform.async_get_current_platform()
        platform.async_register_entity_service(
            name="toggle_session",
            schema={
                vol.Required("card"): str,
                vol.Required("toggle"): str,
            },
            func="toggle_session",
        )
        hass.data[DOMAIN]["_service_registered"] = True

    coordinator = hass.data[DOMAIN][entry.entry_id]
    entities: list[Entity] = []

    if coordinator.data:
        if isinstance(coordinator, CityParkingUserDataUpdateCoordinator):
            sensor: SensorEntity = CityParkingSensor(coordinator=coordinator)
            entities.append(sensor)

        async_add_entities(entities, True)

async def async_remove_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("sensor async_remove_entry " + entry.entry_id)
    try:
        await hass.config_entries.async_forward_entry_unload(entry, Platform.SENSOR)
        _LOGGER.info("Successfully removed sensor from the integration")
    except ValueError:
        pass


class CityParkingSensor(
    CoordinatorEntity[CityParkingUserDataUpdateCoordinator],
    SensorEntity,
):
    """Main feature of this integration. This sensor represents an EVSE and shows its realtime availability status."""

    def __init__(
        self,
        # evse_id: EvseId,
        coordinator: CityParkingUserDataUpdateCoordinator
    ) -> None:
        """Initialize the Sensor."""
        super().__init__(coordinator)
        # self.evse_id = evse_id
        self.coordinator = coordinator
        self.cityParkingInfo: CityParkingModel = self.coordinator.data
        self.origin = self.cityParkingInfo.origin
        
        # self._attr_name = f"{operator} {self.station.address.streetAndNumber} {self.station.address.city}{' ' + self.station.address.country if hasattr(self.station.address, "country") else ''}"
        # self._attr_name = self.station.name
        self._attr_name = f"Parking {self.origin}"
        self._attr_has_entity_name = False
        self._attr_unique_id = f"Parking {self.origin}"
        self._attr_attribution = "seety.co"
        self._attr_device_class = SensorDeviceClass.ENUM
        self._attr_native_unit_of_measurement = None
        self._attr_state_class = None
        # if hasattr(self.station, "ownerName") and self.station.ownerName:
        #     operator = self.station.ownerName
        # else:
        #     operator = self.station.owner.name
        operator = "seety.co"
        self._attr_device_info = DeviceInfo(
            name=self._attr_name,
            identifiers={(DOMAIN, self._attr_unique_id)},
            entry_type=None,
            manufacturer=operator,
        )
        self._read_coordinator_data()


    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._read_coordinator_data()
        # self._attr_name = f"{self.station.name}"
        self.async_write_ha_state()

    
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + self.entity_id)

    def _read_coordinator_data(self) -> None:
        """Read data from ev station."""
        self.cityParkingInfo: CityParkingModel = self.coordinator.data
        self._attr_extra_state_attributes = self.cityParkingInfo.extra_data if self.cityParkingInfo else {}
        self._attr_native_value = self._attr_extra_state_attributes.get('zone', "unknown")
        self._attr_icon = "mdi:parking"
