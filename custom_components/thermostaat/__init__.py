from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN, PLATFORMS
from .manager import ThermostaatManager
from decimal import Decimal

import logging

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    manager = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if manager is None:
        climate_entity = entry.data["climate_entity"]
        window_sensor = entry.data["window_sensor"]
        away_entity = entry.data["away_entity"]
        manager = ThermostaatManager(
            hass=hass,
            entry=entry,
        )
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = manager

    async def window_listener(event):
        _LOGGER.debug(
            "Window state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        await manager.async_window_state_changed(new_state.state == "on")

    async def away_listener(event):
        """Listener for away state changes."""
        _LOGGER.debug(
            "Away state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        state = new_state.state

        await manager.async_away_state_changed(state == "on")

    async def climate_listener(event):
        _LOGGER.debug(
            "Climate state change event: %s",
            event,
        )

        new_state = event.data.get("new_state")

        if new_state is None:
            return

        await manager.async_climate_current_temperature_changed(
            Decimal(new_state.attributes.get("current_temperature"))
        )

        old_temp = _get_target_temperature(event.data.get("old_state"))
        new_temp = _get_target_temperature(new_state)

        if old_temp == new_temp or new_temp is None:
            return

        await manager.async_climate_state_changed(new_temp)

    def _get_target_temperature(
        state,
    ) -> Decimal | None:
        if state is None:
            return None

        return Decimal(state.attributes.get("temperature"))

    await manager.async_initialize()

    manager._listeners.extend(
        [
            async_track_state_change_event(
                hass,
                [window_sensor],
                window_listener,
            ),
            async_track_state_change_event(
                hass,
                [away_entity],
                away_listener,
            ),
            async_track_state_change_event(
                hass,
                [climate_entity],
                climate_listener,
            ),
        ]
    )

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        manager = hass.data[DOMAIN].pop(entry.entry_id, None)

        if manager:
            await manager.async_cleanup()

    return unload_ok

async def async_reload_entry(
    hass,
    entry,
):

    await hass.config_entries.async_reload(
        entry.entry_id
    )