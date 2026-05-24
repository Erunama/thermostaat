import logging

from decimal import Decimal
from homeassistant.components.climate import ClimateEntity
from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant

_LOGGER = logging.getLogger(__name__)


class ThermostaatManager:
    """
    Manages the thermostat logic.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        climate_entity: ClimateEntity,
        entry_id: str,
        away_temp: Decimal,
        scheduler_entity: SensorEntity,
        device_name: str,
    ):
        self.hass = hass
        self.climate_entity = climate_entity
        self.entry_id = entry_id
        self.away_temp = away_temp
        self._schedule_entity = scheduler_entity
        self.window_open = False
        self.is_away = False
        self.manual_override = False
        self.effective_temp = Decimal(18.0)
        self.scheduled_temp = Decimal(18.0)
        self._listeners = []
        self._entities = []
        self.device_name = device_name

    async def async_window_state_changed(self, is_open: bool):
        """
        Handles window state changes.
        """
        self.window_open = is_open
        _LOGGER.debug(
            "Window state changed: %s",
            is_open,
        )

        await self.async_recalculate()

    async def async_away_state_changed(self, is_away: bool):
        """
        Handles away state changes.
        """
        self.is_away = is_away
        _LOGGER.debug(
            "Away state changed: %s",
            is_away,
        )

        await self.async_recalculate()

    async def async_climate_state_changed(self, temperature: Decimal):
        """
        Handles climate state changes.
        """
        self.effective_temp = temperature
        if (self.effective_temp != self.scheduled_temp) and (not self.manual_override):
            self.manual_override = True
            _LOGGER.debug(
                "Manual override enabled: %s",
                self.manual_override,
            )
        else:
            _LOGGER.debug(
                "Manual override disabled: %s",
                self.manual_override,
            )
            self.manual_override = False

        await self.async_recalculate()

    async def async_schedule_changed(
        self,
        temperature: Decimal,
    ):
        """
        Handles schedule changes.
        """

        self.scheduled_temp = temperature
        _LOGGER.debug(
            "Schedule changed: %s",
            temperature,
        )

        await self.async_recalculate()

    async def async_recalculate(self):
        """
        Recalculation logic
        """
        # TODO: Implement logic

        _LOGGER.debug(
            "Starting recalculation with states: away=%s, manual_override=%s, window_open=%s",
            self.is_away,
            self.manual_override,
            self.window_open,
        )
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
        for unsub in self._listeners:
            unsub()

        self._listeners.clear()

    async def async_set_temperature(self, temperature: Decimal):
        """Set the target temperature of the climate entity."""
        await self.hass.services.async_call(
            "climate",
            "set_temperature",
            {
                "entity_id": self.climate_entity,
                "temperature": temperature,
            },
        )

    async def async_turn_off(self):
        """Disable the thermostat"""
        await self.hass.services.async_call(
            "climate",
            "turn_off",
            {
                "entity_id": self.climate_entity,
            },
        )

    async def async_turn_on(self):
        """Enable the thermostat."""
        await self.hass.services.async_call(
            "climate",
            "turn_on",
            {
                "entity_id": self.climate_entity,
            },
        )
