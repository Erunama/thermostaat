from homeassistant.config_entries import ConfigEntry

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorDeviceClass,
)
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .manager import ThermostaatManager
from .entity import ThermostaatEntityMixin

async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    manager = hass.data[DOMAIN][entry.entry_id]
    entities = [
        AwayModeSensor(manager, entry.entry_id),
        ManualModeSensor(manager, entry.entry_id),
        WindowModeSensor(manager, entry.entry_id)
    ]
    async_add_entities(entities)


class AwayModeSensor(ThermostaatEntityMixin, BinarySensorEntity):
    """
    Sensor that indicates if the system is in away mode.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "away_mode"
    _attr_name = "Away Mode"
    _attr_device_class = BinarySensorDeviceClass.PRESENCE

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_away_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        """Indicates if the system is in away mode."""
        return not self.manager.is_away


class ManualModeSensor(ThermostaatEntityMixin, BinarySensorEntity):
    """
    Sensor that indicates if the system is in manual override mode.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "manual_override"
    _attr_name = "Manual Override"

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_manual_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        return self.manager.manual_override


class WindowModeSensor(ThermostaatEntityMixin, BinarySensorEntity):
    """
    Sensor that indicates if the window is open.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "window_open"
    _attr_name = "Window Open"
    _attr_device_class = BinarySensorDeviceClass.WINDOW

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_window_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def is_on(self) -> bool:
        return self.manager.window_open
    
