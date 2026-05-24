from homeassistant.config_entries import ConfigEntry
from homeassistant.components.sensor import SensorEntity, SensorDeviceClass

from homeassistant.core import HomeAssistant
from homeassistant.const import UnitOfTemperature

from decimal import Decimal
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
        EffectiveTemperatureSensor(manager, entry.entry_id),
    ]
    async_add_entities(entities)


class EffectiveTemperatureSensor(ThermostaatEntityMixin, SensorEntity):
    """
    Sensor that indicates the effective temperature.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "effective_temperature"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Effective Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE

    def __init__(self, manager: ThermostaatManager, entry_id: str):
        self._attr_unique_id = f"{entry_id}_effective_temperature"
        self.manager = manager

    async def async_added_to_hass(self):
        self.manager._entities.append(self)

    @property
    def native_value(self) -> Decimal:
        return self.manager.effective_temp