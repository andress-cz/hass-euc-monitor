"""Sensor platform for EUC Monitor integration."""
from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL, SENSOR_TYPES
from .coordinator import EUCDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up EUC Monitor sensors from a config entry."""
    coordinator: EUCDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for sensor_key, sensor_config in SENSOR_TYPES.items():
        entities.append(EUCSensor(coordinator, entry, sensor_key, sensor_config))

    async_add_entities(entities)


class EUCSensor(CoordinatorEntity, SensorEntity):
    """Representation of an EUC sensor."""

    def __init__(
        self,
        coordinator: EUCDataUpdateCoordinator,
        entry: ConfigEntry,
        sensor_key: str,
        sensor_config: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_key = sensor_key
        self._attr_name = f"EUC {sensor_config['name']}"
        self._attr_unique_id = f"{entry.entry_id}_{sensor_key}"
        self._attr_native_unit_of_measurement = sensor_config.get("unit")
        self._attr_icon = sensor_config.get("icon")
        self._attr_device_class = sensor_config.get("device_class")
        self._attr_state_class = sensor_config.get("state_class")
        self._attr_entity_registry_enabled_default = sensor_config.get(
            "enabled_default", True
        )

        # Set display precision for voltage sensors
        if "cell" in sensor_key or "voltage" in sensor_key:
            self._attr_suggested_display_precision = 2

        # Device info
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=coordinator.device_name,
            manufacturer=MANUFACTURER,
            model=MODEL,
        )

    @property
    def native_value(self):
        """Return the state of the sensor."""
        if self.coordinator.data:
            return self.coordinator.data.get(self._sensor_key)
        return None

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        # Entity is available only if we have data from the device
        return self.coordinator.data is not None and len(self.coordinator.data) > 0
