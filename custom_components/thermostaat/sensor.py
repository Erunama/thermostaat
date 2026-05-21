from homeassistant.components.sensor import (
    SensorEntity,
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
)

from .const import DOMAIN


async def async_setup_entry(
    hass,
    entry,
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

    def __init__(self, manager, entry_id):
        self._attr_unique_id = f"{entry_id}_away_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager.entities.append(self)

    @property
    def is_on(self):
        return self.manager.is_away


class ManualModeSensor(BinarySensorEntity):
    """
    Sensor that indicates if the system is in manual override mode.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "manual_override"

    def __init__(self, manager, entry_id):
        self._attr_unique_id = f"{entry_id}_manual_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager.entities.append(self)

    @property
    def is_on(self):
        return self.manager.manual_override


class WindowModeSensor(BinarySensorEntity):
    """
    Sensor that indicates if the window is open.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "window_open"

    def __init__(self, manager, entry_id):
        self._attr_unique_id = f"{entry_id}_window_mode"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager.entities.append(self)

    @property
    def is_on(self):
        return self.manager.window_open


class EffectiveTemperatureSensor(SensorEntity):
    """
    Sensor that indicates the effective temperature.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "effective_temperature"

    def __init__(self, manager, entry_id):
        self._attr_unique_id = f"{entry_id}_effective_temperature"
        self._attr_unit_of_measurement = "°C"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager.entities.append(self)

    @property
    def native_value(self):
        return self.manager.effective_temp
