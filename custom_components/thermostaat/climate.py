from homeassistant.components.climate import ClimateEntity

from homeassistant.const import (
    UnitOfTemperature,
)


from .entity import ThermostaatEntityMixin

async def async_setup_entry(
    hass,
    entry,
    async_add_entities,
):

    manager = hass.data[DOMAIN][
        entry.entry_id
    ]

    async_add_entities([
        ThermostaatClimate(
            manager,
            entry.entry_id,
        )
    ])

class ThermostaatClimate(
    ThermostaatEntityMixin,
    ClimateEntity,
):
    """
    Climate entity for the thermostaat.
    """
    _attr_has_entity_name = True
    _attr_translation_key = "Thermostat"
    _attr_name = "Thermostat"
    _attr_unit_of_measurement = UnitOfTemperature.CELSIUS

    def __init__(self, manager, entry_id):
        super().__init__(manager)
        self._attr_unique_id = f"{entry_id}_climate"

    @property
    def current_temperature(self):
        return self.manager.current_temperature
    
    @property
    def target_temperature(self):

        return (
            self.manager.effective_temp
        )

    async def async_set_temperature(
        self,
        **kwargs,
    ):

        temperature = kwargs.get(
            "temperature"
        )

        await self.manager.async_manual_set_temperature(
            temperature
    )
