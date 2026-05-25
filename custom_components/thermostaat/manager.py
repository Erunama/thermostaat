import logging

from decimal import Decimal
from homeassistant.config_entries import ConfigEntry
from homeassistant.components.climate import ClimateEntity
from homeassistant.core import HomeAssistant
from datetime import timedelta

from homeassistant.helpers.event import (
    async_track_time_interval,
)
import json

from datetime import time
from homeassistant.util import dt

_LOGGER = logging.getLogger(__name__)


class ThermostaatManager:
    """
    Manages the thermostat logic.
    """

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ):
        self.hass = hass

        self.climate_entity = entry.data["climate_entity"]
        self.away_temp = entry.data["away_temperature"]
        self.entry = entry
        self.device_name = entry.title

        self.window_open = False
        self.is_away = False
        self._manual_thermostat_temp = Decimal(18.0)

        window_state = hass.states.get(entry.data["window_sensor"])
        if window_state is not None:
            self.window_open = window_state.state == "on"

        away_state = hass.states.get(entry.data["away_entity"])
        if away_state is not None:
            self.is_away = away_state.state == "on"

        climate_state = hass.states.get(entry.data["climate_entity"])

        if climate_state is not None:
            temp = climate_state.attributes.get("current_temperature")
            if temp is not None:
                self._manual_thermostat_temp = Decimal(temp)

        self.current_temp = Decimal(18.0)
        self.current_set_temp = Decimal(18.0)
        self.manual_override = False
        self._manual_thermostat_temp = Decimal(18.0)
        self._scheduled_temp = Decimal(18.0)
        self._listeners = []
        self._entities = []

        raw_schedule = entry.options.get(
            "schedule_json",
            "[]",
        )

        try:
            self.schedule = json.loads(raw_schedule)
        except Exception:
            _LOGGER.exception("Invalid schedule JSON")
            self.schedule = []

        self.schedule.sort(key=lambda x: x["time"])

        self.unsub_schedule = async_track_time_interval(
            hass,
            self.async_schedule_tick,
            timedelta(minutes=1),
        )

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
        if (self._manual_thermostat_temp != self._scheduled_temp) and (
            not self.is_away
        ):
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
            self.away_temp,
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

    def resolve_scheduled_temperature(
        self,
    ):
        """Resolves the scheduled temperature based on the current time and the schedule."""
        now = dt.now().time()
        current_temp = self._scheduled_temp
        for entry in self.schedule:
            entry_time = time.fromisoformat(entry["time"])
            if now >= entry_time:
                current_temp = entry["temperature"]
        return current_temp

    async def async_schedule_tick(self,now,):
        new_temp = self.resolve_scheduled_temperature()
        if new_temp != self._scheduled_temp:
            self._scheduled_temp = new_temp
            await self.async_recalculate()
