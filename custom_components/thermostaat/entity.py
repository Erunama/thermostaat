from .const import DOMAIN


class ThermostaatEntityMixin:

    _attr_has_entity_name = True

    def __init__(self, manager):

        self.manager = manager

    @property
    def device_info(self):

        return {

            "identifiers": {
                (
                    DOMAIN,
                    self.manager.entry_id,
                )
            },

            "name":
                self.manager.device_name,

            "manufacturer":
                "Erunama",

            "model":
                "Thermostaat",
        }
    