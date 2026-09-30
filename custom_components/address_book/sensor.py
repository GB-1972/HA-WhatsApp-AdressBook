"""Sensor showing the number of contacts."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, SIGNAL_CONTACTS_CHANGED
from .backends import AddressBookBackend


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    async_add_entities([ContactCountSensor(entry, hass.data[DOMAIN][entry.entry_id])], True)


class ContactCountSensor(SensorEntity):
    _attr_has_entity_name = True
    _attr_translation_key = "contact_count"
    _attr_icon = "mdi:contacts"
    _attr_should_poll = False

    def __init__(self, entry: ConfigEntry, db: AddressBookBackend) -> None:
        self._db = db
        self._attr_unique_id = f"{entry.entry_id}_contact_count"

    async def async_added_to_hass(self) -> None:
        @callback
        def _refresh() -> None:
            self.hass.async_create_task(self._async_refresh())

        self.async_on_remove(
            async_dispatcher_connect(self.hass, SIGNAL_CONTACTS_CHANGED, _refresh)
        )

    async def _async_refresh(self) -> None:
        await self.async_update()
        self.async_write_ha_state()

    async def async_update(self) -> None:
        try:
            self._attr_native_value = await self._db.count()
            self._attr_available = True
        except Exception:  # noqa: BLE001
            self._attr_available = False
