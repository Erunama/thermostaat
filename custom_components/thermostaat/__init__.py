from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from homeassistant.helpers.event import (
    async_track_state_change_event
)


from .const import DOMAIN
from .manager import ThermostaatManager


async def async_setup_entry(hass,entry,):
    manager = hass.data.get(DOMAIN, {}).get(entry.entry_id)

    if manager is None:


        climate_entity = (
            entry.data["climate_entity"]
        )

        window_sensor = (
            entry.data["window_sensor"]
        )

        away_entity = (
            entry.data["away_entity"]
        )

        away_temp = (
            entry.data["away_temperature"]
        )

        schedule_temp = (
            entry.data["schedule_temperature"]
        )

        manager = ThermostaatManager(
            hass=hass,
            climate_entity=climate_entity,
            entry_id=entry.entry_id,
            away_temp=away_temp,
            schedule_temp=schedule_temp,
        )
        hass.data.setdefault(DOMAIN, {})

        hass.data[DOMAIN][entry.entry_id] = (
            manager
        )

    async def window_listener(event):

        new_state = (
            event.data["new_state"]
        )

        if new_state is None:
            return

        await manager.async_window_state_changed(
            new_state.state == "on"
        )

    async def away_listener(event):

        new_state = (
            event.data["new_state"]
        )

        if new_state is None:
            return

        state = new_state.state

        is_away = state in (
            "off",
            "not_home",
            "away",
        )

        await manager.async_away_state_changed(
            is_away
        )

    async def climate_listener(event):

        new_state = (
            event.data["new_state"]
        )

        if new_state is None:
            return

        temp = (
            new_state.attributes.get(
                "temperature"
            )
        )

        if temp is None:
            return

        await manager.async_climate_state_changed(
            temp
        )

    async def schedule_listener(event):
        
        new_state = (
            event.data["new_state"]
        )

        if new_state is None:
            return

        temp = (
            new_state.attributes.get(
                "temperature"
            )
        )

        if temp is None:
            return

        await manager.async_schedule_changed(
            temp
        )

    unsub_window = async_track_state_change_event(
        hass,
        [window_sensor],
        window_listener,
    )

    unsub_away = async_track_state_change_event(
        hass,
        [away_entity],
        away_listener,
    )

    unsub_climate = async_track_state_change_event(
        hass,
        [climate_entity],
        climate_listener,
    )

    unsub_schedule = async_track_state_change_event(
        hass,
        [schedule_temp],
        schedule_listener,
    )

    manager.listeners.append(unsub_window)
    manager.listeners.append(unsub_away)
    manager.listeners.append(unsub_climate)
    manager.listeners.append(unsub_schedule)

    await hass.config_entries.async_forward_entry_setups(
        entry,
        ["sensor"],
    )

    return True

async def async_unload_entry(hass, entry,):
    unload_ok = await hass.config_entries.async_unload_platforms(entry,["sensor"])

    if unload_ok:
        manager = hass.data[DOMAIN].pop(entry.entry_id, None)

        if manager:
            await manager.async_cleanup()


    return unload_ok