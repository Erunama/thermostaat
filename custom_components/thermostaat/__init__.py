from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_state_change_event

from .const import DOMAIN
from .manager import ThermostaatManager
import logging

_LOGGER = logging.getLogger(__name__)
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
        away_temp = entry.data["away_temperature"]
        scheduler_entity = entry.data["schedule_temperature"]
        manager = ThermostaatManager(
            hass=hass,
            climate_entity=climate_entity,
            entry_id=entry.entry_id,
            away_temp=away_temp,
            scheduler_entity=scheduler_entity,
        )
        hass.data.setdefault(DOMAIN, {})
        hass.data[DOMAIN][entry.entry_id] = manager
        hass.data[DOMAIN][entry.entry_id] = manager

    async def window_listener(event):
        _LOGGER.debug(
            "Window state change event: %s",
            event,
        )
        new_state = event.data["new_state"]
        _LOGGER.debug(
            "Window state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        await manager.async_window_state_changed(new_state.state == "on")
        await manager.async_window_state_changed(new_state.state == "on")

    async def away_listener(event):
        """Listener for away state changes."""
        _LOGGER.debug(
            "Away state change event: %s",
            event,
        )
        new_state = event.data["new_state"]
        """Listener for away state changes."""
        _LOGGER.debug(
            "Away state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        state = new_state.state

        is_away = state in (
            "off",
            "not_home",
            "away",
        )

        await manager.async_away_state_changed(is_away)
        await manager.async_away_state_changed(is_away)

    async def climate_listener(event):
        _LOGGER.debug(
            "Climate state change event: %s",
            event,
        )
        new_state = event.data["new_state"]
        _LOGGER.debug(
            "Climate state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        temp = new_state.attributes.get("temperature")
        temp = new_state.attributes.get("temperature")

        if temp is None:
            return

        await manager.async_climate_state_changed(temp)
        await manager.async_climate_state_changed(temp)

    async def schedule_listener(event):
        _LOGGER.debug(
            "Schedule state change event: %s",
            event,
        )
        new_state = event.data["new_state"]
        _LOGGER.debug(
            "Schedule state change event: %s",
            event,
        )
        new_state = event.data["new_state"]

        if new_state is None:
            return

        temp = new_state.state

        if temp is None:
            return

        await manager.async_schedule_changed(temp)
        await manager.async_schedule_changed(temp)

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
            async_track_state_change_event(
                hass,
                [scheduler_entity],
                schedule_listener,
            ),
        ]
    )

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor"],
    )

    return True


async def async_unload_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
):
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])

    if unload_ok:
        manager = hass.data[DOMAIN].pop(entry.entry_id, None)

        if manager:
            await manager.async_cleanup()

    return unload_ok

