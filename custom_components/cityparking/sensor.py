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
    evse_id = ""

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

    def _read_coordinator_data(self) -> None:
        """Read data from ev station."""
        self.cityParkingInfo: CityParkingModel = self.coordinator.data

        try:
            if self.cityParkingInfo:
                # self._attr_name = self.station.name
                # self._attr_native_value = evse.status
                # self._attr_icon = self._choose_icon(evse.connectors)
                extra_data = {
                    "TODO": "TODO"
                    # "name": self.station.name,
                    # "type": self.type.value,
                    # "origin": self.origin,
                    # "address": self.station.address.streetAndHouseNumber,
                    # "city": self.station.address.city,
                    # "postal_code": self.station.address.postcode,
                    # "country": self.station.address.country,
                    # "latitude": self.station.coordinates.lat,
                    # "longitude": self.station.coordinates.lng,
                    # "straight_line_distance": self.station.straight_line_distance,
                    # "route_distance": self.station.route_distance,
                    # "route_duration": self.station.route_duration,
                    # "route_name": self.station.route_name,
                    # "operator_name": self.station.ownerName,
                    # # "suboperator_name": self.station.owner.name,
                    # "url": self.station.url,
                    # "facilities": ", ".join(self.station.facilities),
                    # "available_connectors": self.station.evseSummary.available,
                    # "number_of_connectors": self.station.evseSummary.total,
                    # "max_speed_kWh": self.station.evseSummary.maxSpeed/1000 if self.station.evseSummary.maxSpeed else None,
                    # "min_speed_kWh": self.station.evseSummary.minSpeed/1000 if self.station.evseSummary.minSpeed else None,
                    # "is_unlimited": self.station.evseSummary.isUnlimited,
                    # "is_limited": self.station.evseSummary.isLimited,
                    # "is_unkown": self.station.evseSummary.isUnknown,
                    # "allowed": self.station.isAllowed,
                    # "external_id": str(self.station.id),
                    # "evse_id": str(evse.evseId),
                    # "status": evse.status,
                    # "last_updated": evse.lastUpdated,
                    # "physical_reference": evse.physicalReference,
                    # "connector_standard": connector.standard,
                    # "connector_type": connector.powerType,
                    # "connector_format": connector.format,
                    # "connector_max_power": connector.maxPower/1000 if connector.maxPower else None,
                    # "opentwentyfourseven": self.station.isTwentyFourSeven,
                    # "charging_costs": evse.prices.chargingCosts if evse.prices else None,
                    # "charging_time_costs": evse.prices.chargingTimeCosts if evse.prices else None,
                    # "start_tariff": evse.prices.startTariff if evse.prices else None,
                    # "parking_time_costs": evse.prices.parkingTimeCosts if evse.prices else None,
                    # "price_description": evse.prices.description if evse.prices else None,
                    # "map_label": f"{self.station.evseSummary.available}/{self.station.evseSummary.total}{' ' + str(int(connector.maxPower/1000)) + 'kWh' if connector.maxPower else ''}",
                }
                
                self._attr_extra_state_attributes = extra_data
        except AttributeError as err:
            _LOGGER.error(err)

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        self._read_coordinator_data()
        # self._attr_name = f"{self.station.name}"
        self.async_write_ha_state()

    
    async def async_will_remove_from_hass(self):
        """Clean up after entity before removal."""
        _LOGGER.info("async_will_remove_from_hass " + self.entity_id)

