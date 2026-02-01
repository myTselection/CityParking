"""Sensors for the shell_recharge integration."""

from __future__ import annotations

import logging
import typing
from typing import Any

# import evrecharge
import voluptuous as vol
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
# from homeassistant.helpers.entity import RestoreEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, callback
from homeassistant.exceptions import HomeAssistantError, ServiceValidationError
from homeassistant.helpers import entity_platform
from homeassistant.helpers.entity import DeviceInfo, Entity
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .seetyApi.models import *
from homeassistant.util import dt as dt_util
# from copy import deepcopy

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
            for parkingSensorType in ParkingSensorType:
                sensor: SensorEntity = CityParkingSensor(coordinator=coordinator, parkingSensorType=parkingSensorType)
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
    SensorEntity #, RestoreEntity
):
    """Main feature of this integration. This sensor represents an EVSE and shows its realtime availability status."""

    def __init__(
        self,
        coordinator: CityParkingUserDataUpdateCoordinator,
        parkingSensorType : ParkingSensorType = ParkingSensorType.ZONE
    ) -> None:
        """Initialize the Sensor."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.parkingSensorType = parkingSensorType
        self.parkingSensorType_snake = " ".join(word.capitalize() for word in self.parkingSensorType.value.split("_"))  #snake_to_title(self.type.value)
        self.cityParkingInfo: CityParkingModel = self.coordinator.data
        self.origin = self.cityParkingInfo.origin
        # self._start_ts_iso: Optional[str] = None  # persisted ISO string for restoration
        
        # self._attr_name = f"{operator} {self.station.address.streetAndNumber} {self.station.address.city}{' ' + self.station.address.country if hasattr(self.station.address, "country") else ''}"
        # self._attr_name = self.station.name
        self._attr_name = f"Parking {self.origin} {self.parkingSensorType_snake}"
        self._attr_has_entity_name = False
        self._device_unique_id =  f"Parking {self.origin}"
        self._attr_unique_id = f"{self._device_unique_id}_{parkingSensorType.value}"
        # store device_unique_id for device_info
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
            name=self._device_unique_id,
            identifiers={(DOMAIN, self._device_unique_id)},
            entry_type=None,
            manufacturer=operator,
        )
        self._read_coordinator_data()

    
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + self.entity_id)

    # async def async_added_to_hass(self):
    #     await super().async_added_to_hass()

    #     last_state = await self.async_get_last_state()
    #     restored = last_state.attributes.get("stay_start") if last_state and last_state.attributes else None
    #     if restored:
    #         # Update coordinator data so other sensors see the restored start
    #         await self._push_start_to_coordinator(self.unique_id, restored, last_state)
        
    #     # after restoring, refresh your coordinator info into attributes/value
    #     # and write state so restored attributes are re-exposed/persisted
    #     self._read_coordinator_data()
    #     # Ensure HA writes the state with restored attributes
    #     self.async_write_ha_state()

    # async def _push_start_to_coordinator(self, unique_id: str, start_iso: str) -> None:
    #     """Make a copy of coordinator.data, inject the restored value, and set it."""
    #     # Make a shallow/deep copy depending on your data structure
    #     new_data = deepcopy(self.coordinator.data)

    #     # Example: coordinator.data is a dict mapping unique_id -> CityParkingModel-like dict
    #     # If your data is a custom model, convert to serializable dict or construct a new model instance
    #     if isinstance(new_data, dict):
    #         item = dict(new_data.get(unique_id, {}))
    #         item_extra = dict(item.get("extra_data", {}))
    #         item_extra["stay_start"] = start_iso
    #         item["extra_data"] = item_extra
    #         new_data[unique_id] = item

    #     else:
    #         # If it's a model object, create a new model instance or set an attribute.
    #         # Example pseudo-code:
    #         # cloned_model = new_data.clone()
    #         # cloned_model.set_stay_start_for(unique_id, start_iso)
    #         # new_data = cloned_model
    #         raise NotImplementedError("Adapt to your coordinator.data structure")

    #     # Use coordinator API to update data and notify listeners
    #     await self.coordinator.async_set_updated_data(new_data)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._read_coordinator_data()
        # self._attr_name = f"{self.station.name}"
        self.async_write_ha_state()

    def _read_coordinator_data(self) -> None:
        """Read data from ev station."""
        self.cityParkingInfo: CityParkingModel = self.coordinator.data
        self._attr_extra_state_attributes = self.cityParkingInfo.extra_data if self.cityParkingInfo else {}
         # expose the stay start timestamp (ISO) so RestoreEntity can persist it
        self._attr_native_value = self._attr_extra_state_attributes.get(self.parkingSensorType.value, "unknown")

        if self.parkingSensorType.value == ParkingSensorType.TIME.value:
            self._attr_icon = "mdi:clock-outline"
            is_hours_active_now = self._attr_extra_state_attributes.get(TIME_RESTRICTION_ACTIVE_NOW, None)
            if is_hours_active_now is True:
                self._attr_icon = "mdi:clock-alert"
        elif self.parkingSensorType.value == ParkingSensorType.PRICE.value:
            self._attr_icon = "mdi:currency-usd"
        elif self.parkingSensorType.value == ParkingSensorType.DAYS.value:
            self._attr_icon = "mdi:calendar"
            is_days_active_now = self._attr_extra_state_attributes.get(DAY_RESTRICTION_ACTIVE_NOW, None)
            if is_days_active_now is True:
                self._attr_icon = "mdi:calendar-alert"
        elif self.parkingSensorType.value == ParkingSensorType.MAXSTAY.value:
            self._attr_icon = "mdi:timer-outline"
            is_max_stay_passed = self._attr_extra_state_attributes.get(MAXSTAY_PASSED_NOW, None)
            if is_max_stay_passed is True:
                self._attr_icon = "mdi:timer-alert"
        elif self.parkingSensorType.value == ParkingSensorType.ZONE.value:
            self._attr_icon = "mdi:map-marker"
        elif self.parkingSensorType.value == ParkingSensorType.ADDRESS.value:
            self._attr_icon = "mdi:home-map-marker"
        elif self.parkingSensorType.value == ParkingSensorType.REMARKS.value:
            self._attr_icon = "mdi:note-text"
        elif self.parkingSensorType.value == ParkingSensorType.TYPE.value:
            self._attr_icon = "mdi:information-outline"
        elif self.parkingSensorType.value == ParkingSensorType.RESTRICTION_ACTIVE.value:
            self._attr_icon = "mdi:alert-circle-check-outline"
            is_restriction_active = self._attr_extra_state_attributes.get(RESTRICTION_ACTIVE, None)
            if is_restriction_active is True:
                self._attr_icon = "mdi:alert-circle-outline"
        else:
            self._attr_icon = "mdi:parking"
