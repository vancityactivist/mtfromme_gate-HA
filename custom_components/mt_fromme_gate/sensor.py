"""Sensor platform for the Mt Fromme Gate integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MtFrommeGateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from a config entry."""
    coordinator: MtFrommeGateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([MtFrommeGateClosingSensor(coordinator, entry)])


class MtFrommeGateClosingSensor(CoordinatorEntity[MtFrommeGateCoordinator], SensorEntity):
    """Represents the next Mt Fromme gate closing time."""

    _attr_has_entity_name = True
    _attr_name = "Closing time"
    _attr_icon = "mdi:gate"
    _attr_device_class = SensorDeviceClass.TIMESTAMP

    def __init__(self, coordinator: MtFrommeGateCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_closing_time"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name="Mt Fromme Gate",
            manufacturer="District of North Vancouver",
            entry_type=DeviceEntryType.SERVICE,
            configuration_url="https://www.dnv.org/parks-trails-recreation/hiking-and-cycling-trails-parks",
        )

    @property
    def native_value(self):
        return self.coordinator.data["next_closing"]

    @property
    def extra_state_attributes(self):
        return {
            "today_closing_time": self.coordinator.data["today_closing_time"],
            "schedule": self.coordinator.data["schedule"],
        }
