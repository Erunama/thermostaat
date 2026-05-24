from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import ClimateEntityFeature

from homeassistant.const import (
    UnitOfTemperature,
)

from homeassistant.components.climate.const import (
    HVACMode,
)

from .const import DOMAIN
from .entity import ThermostaatEntityMixin


async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    manager = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        [
            ThermostaatClimate(
                manager,
                entry.entry_id,
            )
        ]
    )

class ThermostaatClimate(
    ThermostaatEntityMixin,
    ClimateEntity,
):
    """
    Climate entity for the thermostaat.
    """

    _attr_has_entity_name = True
    _attr_translation_key = "thermostat"
    _attr_name = "Thermostat"
    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_supported_features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF

    def __init__(self, manager, entry_id):
        super().__init__(manager)
        self._attr_unique_id = f"{entry_id}_climate"

    @property
    def hvac_modes(self):
        return [
            HVACMode.HEAT,
            HVACMode.OFF,
        ]
    
    @property
    def hvac_mode(self):
        if self.manager.window_open:
            return HVACMode.OFF

        return HVACMode.HEAT

    @property
    def current_temperature(self):
        return float(self.manager.current_temp)

    @property
    def target_temperature(self):
        return float(self.manager.current_set_temp)

    async def async_set_temperature(self,**kwargs,):
        temperature = kwargs.get("temperature")

        await self.manager.async_climate_state_changed(temperature)
