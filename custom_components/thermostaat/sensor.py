from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant

from decimal import Decimal
from .const import DOMAIN
from .manager import ThermostaatManager


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    manager = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AwayModeSensor(manager, entry.entry_id),
        ManualModeSensor(manager, entry.entry_id),
        WindowModeSensor(manager, entry.entry_id),
        EffectiveTemperatureSensor(manager, entry.entry_id),
    ]
    async_add_entities(entities)


class AwayModeSensor(BinarySensorEntity):
    """
    Sensor that indicates if the system is in away mode.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "away_mode"
    _attr_name = "Away Mode"
    _attr_device_class = BinarySensorDeviceClass.PRESENCE
    _attr_device_info = {
        "identifiers": {(DOMAIN, "away_mode")},
        "name": "Away Mode",
        "manufacturer": "Erunama",
        "model": "Away Mode Sensor",
    }

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_away_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        """Indicates if the system is in away mode."""
        return self.manager.is_away


class ManualModeSensor(BinarySensorEntity):
    """
    Sensor that indicates if the system is in manual override mode.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "manual_override"
    _attr_name = "Manual Override"
    _attr_device_info = {
        "identifiers": {(DOMAIN, "manual_override")},
        "name": "Manual Override",
        "manufacturer": "Erunama",
        "model": "Manual Override Sensor",
    }

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_manual_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        return self.manager.manual_override


class WindowModeSensor(BinarySensorEntity):
    """
    Sensor that indicates if the window is open.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "window_open"
    _attr_name = "Window Open"
    _attr_device_class = BinarySensorDeviceClass.WINDOW
    _attr_device_info = {
        "identifiers": {(DOMAIN, "window_open")},
        "name": "Window Open",
        "manufacturer": "Erunama",
        "model": "Window Open Sensor",
    }

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_window_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        return self.manager.window_open


class EffectiveTemperatureSensor(SensorEntity):
    """
    Sensor that indicates the effective temperature.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "effective_temperature"
    _attr_native_unit_of_measurement = "°C"
    _attr_name = "Effective Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_device_info = {
        "identifiers": {(DOMAIN, "effective_temperature")},
        "name": "Effective Temperature",
        "manufacturer": "Erunama",
        "model": "Effective Temperature Sensor",
    }

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_effective_temperature"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def native_value(self) -> Decimal:
        return self.manager.effective_temp
