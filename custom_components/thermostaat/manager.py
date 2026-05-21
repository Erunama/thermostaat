class ThermostaatManager:
    """
    Manages the thermostat logic.
    """

    def __init__(self, hass, climate_entity, entry_id, away_temp, schedule_temp):
        self.hass = hass
        self.climate_entity = climate_entity
        self.entry_id = entry_id
        self.away_temp = away_temp
        self.scheduled_temp = schedule_temp
        self.window_open = False
        self.is_away = False
        self.manual_override = False
        self.effective_temp = schedule_temp
        self.listeners = []
        self.entities = []

    async def async_window_state_changed(self, is_open):
        """
        Handles window state changes.
        """
        self.window_open = is_open

        await self.async_recalculate()

    async def async_away_state_changed(self, is_away):
        """
        Handles away state changes.
        """
        self.is_away = is_away

        await self.async_recalculate()

    async def async_climate_state_changed(self, temperature):
        """
        Handles climate state changes.
        """
        self.effective_temp = temperature
        if (self.effective_temp != self.scheduled_temp) and (not self.manual_override):
            self.manual_override = True
        else:
            self.manual_override = False

        await self.async_recalculate()

    async def async_schedule_changed(
        self,
        temperature,
    ):
        """
        Handles schedule changes.
        """
        self.scheduled_temp = temperature

        await self.async_recalculate()

    async def async_recalculate(self):
        """
        Recalculation logic
        """
        # TODO: Implement logic

        if self.window_open:
            await self.async_turn_off()
            return

        await self.async_turn_on()
        # TODO: This feels super verbose, i doubt this is the correct way

        if self.is_away:
            await self.async_set_temperature(self.away_temp)
            return

        if self.manual_override:
            await self.async_set_temperature(self.effective_temp)
            return

        await self.async_set_temperature(self.scheduled_temp)

    async def async_cleanup(self):
        """Called when integration is unloaded."""
        for unsub in self.listeners:
            unsub()

        self.listeners.clear()

    async def async_set_temperature(self, temperature):
        """Set the target temperature of the climate entity."""
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {
                "entity_id": self.climate_entity.entity_id,
                "temperature": temperature,
            },
        )

    async def async_turn_off(self):
        """Disable the thermostat"""
        await self.hass.services.async_call(
            "climate",
            "turn_off",
            {
                "entity_id": self.climate_entity.entity_id,
            },
        )

    async def async_turn_on(self):
        """Enable the thermostat."""
        await self.hass.services.async_call(
            "climate",
            "turn_on",
            {
                "entity_id": self.climate_entity.entity_id,
            },
        )
