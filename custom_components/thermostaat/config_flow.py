import voluptuous as vol
from homeassistant.config_entries import ConfigEntry, OptionsFlow, ConfigFlow

from homeassistant import config_entries
from homeassistant.helpers import selector
from homeassistant.core import callback
from .const import DOMAIN


class ThermostaatConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(
                title="Thermostaat",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("climate_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="climate")
                ),
                vol.Required("window_sensor"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="binary_sensor",
                        device_class=["window", "opening", "door", "garage_door"],
                    )
                ),
                vol.Required("away_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(domain="input_boolean")
                ),
                vol.Required("away_temperature", default=16): selector.NumberSelector(
                    selector.NumberSelectorConfig(
                        min=5,
                        max=30,
                        step=0.5,
                        mode=selector.NumberSelectorMode.BOX,
                        unit_of_measurement="°C",
                    )
                ),
                vol.Required("schedule_temperature"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor", device_class="temperature"
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: ConfigEntry,
    ):

        return ThermostaatOptionsFlow()


class ThermostaatOptionsFlow(OptionsFlow):

    async def async_step_init(
        self,
        user_input=None,
    ):

        if user_input is not None:

            return self.async_create_entry(
                title="",
                data=user_input,
            )


        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        "schedule_json",
                        default=self.config_entry.options.get(
                            "schedule_json",
                            "[]",
                        ),
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(multiline=True)
                    )
                }
            ),
        )
