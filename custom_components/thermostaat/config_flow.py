import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN

class ThermostaatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None: 
            return self.async_create_entry(
                title="Thermostaat",
                data=user_input,
            )

# TODO: Add errors
        schema = vol.Schema({
            vol.Required("climate_entity"):
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="climate"
                    )
                ),

            vol.Required("window_sensor"):
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class="window"
                    )
                ),

            vol.Required("away_entity"):
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="zone"
                        )
                    ),

            vol.Required("away_temperature", default=16):
                selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=5,
                        max=30,
                        step=0.5,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="°C"
                    )
                ),

            vol.Required("schedule_temperature"):
                selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                        device_class="temperature"
                    )
                ),
        })

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )