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
        device_name: str,
    ):
        self.hass = hass
        self.device_name = device_name
        self.climate_entity = climate_entity
        self.entry_id = entry_id
        self.away_temp = away_temp
        
        self.current_temp = Decimal(18.0)
        self.current_set_temp = Decimal(18.0)
        self.window_open = False
        self.is_away = False
        self.manual_override = False

        self._manual_thermostat_temp = Decimal(18.0)
        self._scheduled_temp = Decimal(18.0)
        self._listeners = []
        self._entities = []

    async def async_window_state_changed(self, is_open: bool):
        """
        Handles window state changes.
        """
        _LOGGER.debug("Window state changed to %s", is_open)
        self.window_open = is_open

        await self.async_recalculate()

    async def async_away_state_changed(self, is_away: bool):
        """
        Handles away state changes.
        """
        _LOGGER.debug("Away state changed to %s", is_away)
        self.is_away = is_away

        await self.async_recalculate()

    async def async_climate_state_changed(self, temperature: Decimal):
        """
        Handles climate state changes.
        """
        self._manual_thermostat_temp = temperature
        if (self._manual_thermostat_temp != self._scheduled_temp) and (not self.is_away):
            _LOGGER.debug("Manual override detected, setting manual override flag")
            self.manual_override = True
        else:
            _LOGGER.debug("No manual override detected, resetting manual override flag")
            self.manual_override = False

        await self.async_recalculate()

    async def async_climate_current_temperature_changed(self, temperature: Decimal):
        """
        Handles climate state changes.
        """
        _LOGGER.debug("Current temperature changed to %s", temperature)
        self.current_temp = temperature

    async def async_reset_override(self):
        """
        Resets the manual override.
        """
        _LOGGER.debug("Resetting manual override")
        self.manual_override = False
        await self.async_recalculate()

    async def async_schedule_changed(
        self,
        temperature: Decimal,
    ):
        """
        Handles schedule changes.
        """
        # TODO: This will someday be some internal thingy
        _LOGGER.debug("Schedule temperature changed to %s", temperature)
        self._scheduled_temp = temperature
 
        await self.async_recalculate()

    async def async_recalculate(self):
        """
        Recalculation logic
        """

        _LOGGER.debug(
            "Starting recalculation with states: away=%s, manual_override=%s, window_open=%s scheduled_temp=%s, manual_thermostat_temp=%s, away_temp=%s",
            self.is_away,
            self.manual_override,
            self.window_open,
            self._scheduled_temp,
            self._manual_thermostat_temp,
            self.away_temp
        )
        if self.window_open:
            _LOGGER.debug("Window is open, turning off thermostat")
            await self.async_turn_off()
        else:
            _LOGGER.debug("Window is closed, turning on thermostat")
            await self.async_turn_on()
        # TODO: This part feels a tad wonky


        if self.is_away:
            _LOGGER.debug("Away mode is active, setting away temperature")
            await self.async_set_temperature(self.away_temp)
            return

        if self.manual_override:
            _LOGGER.debug("Manual override is active, setting manual temperature")
            await self.async_set_temperature(self._manual_thermostat_temp)
            return

        # Continue to follow schedule
        # TODO: Something to take in mind when to follow schedule
        _LOGGER.debug("Following schedule, setting scheduled temperature")
        await self.async_set_temperature(self._scheduled_temp)

    async def async_cleanup(self):
        """Called when integration is unloaded."""
        for unsub in self._listeners:
            unsub()

        self._listeners.clear()

    async def async_set_temperature(self, temperature: Decimal):
        """Set the target temperature of the climate entity."""
        self.current_set_temp = temperature
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
