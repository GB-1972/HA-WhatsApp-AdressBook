"""Personal address book (PostgreSQL, MariaDB or JSON file)."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall, SupportsResponse
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError, ServiceValidationError
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.dispatcher import async_dispatcher_send

from .const import (
    ATTR_FIRST_NAME, ATTR_GROUP_NAME, ATTR_ID, ATTR_MOBILE, ATTR_NAME, ATTR_QUERY,
    ATTR_WHATSAPP_ID, DOMAIN, SERVICE_ADD_CONTACT, SERVICE_DELETE_CONTACT,
    SERVICE_SEARCH_CONTACTS, SERVICE_UPDATE_CONTACT, SIGNAL_CONTACTS_CHANGED,
)
from .api import async_remove_panel, async_setup_api
from .backends import AddressBookBackend, async_create_backend
from .validation import ContactValidationError, validate_contact

_LOGGER = logging.getLogger(__name__)
PLATFORMS = ["sensor"]

_OPT = vol.Any(None, cv.string)
_CONTACT_FIELDS = {
    vol.Optional(ATTR_NAME): _OPT,
    vol.Optional(ATTR_FIRST_NAME): _OPT,
    vol.Optional(ATTR_GROUP_NAME): _OPT,
    vol.Optional(ATTR_MOBILE): _OPT,
    vol.Optional(ATTR_WHATSAPP_ID): _OPT,
}
ADD_SCHEMA = vol.Schema(_CONTACT_FIELDS)
UPDATE_SCHEMA = vol.Schema({vol.Required(ATTR_ID): vol.Coerce(int), **_CONTACT_FIELDS})
DELETE_SCHEMA = vol.Schema({vol.Required(ATTR_ID): vol.Coerce(int)})
SEARCH_SCHEMA = vol.Schema({vol.Optional(ATTR_QUERY): cv.string})


def _validated(data: dict[str, Any]) -> dict[str, str | None]:
    try:
        return validate_contact(data)
    except ContactValidationError as err:
        raise ServiceValidationError(
            translation_domain=DOMAIN, translation_key=str(err)
        ) from err


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Connect to PostgreSQL and register services."""
    try:
        db = await async_create_backend(hass, dict(entry.data))
    except Exception as err:  # driver/OS/file errors
        raise ConfigEntryNotReady(f"Cannot open address book storage: {err}") from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = db

    def _changed() -> None:
        async_dispatcher_send(hass, SIGNAL_CONTACTS_CHANGED)

    async def add_contact(call: ServiceCall) -> dict[str, Any]:
        contact = _validated(dict(call.data))
        row = await db.add(contact)
        _changed()
        return row

    async def update_contact(call: ServiceCall) -> dict[str, Any]:
        """Replace the contact; omitted fields are cleared (full replace)."""
        data = dict(call.data)
        contact_id = data.pop(ATTR_ID)
        existing = await db.get(contact_id)
        if existing is None:
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="contact_not_found"
            )
        # Merge: only provided keys override, explicit null clears.
        merged = {**existing, **data}
        row = await db.replace(contact_id, _validated(merged))
        _changed()
        return row

    async def delete_contact(call: ServiceCall) -> None:
        if not await db.delete(call.data[ATTR_ID]):
            raise ServiceValidationError(
                translation_domain=DOMAIN, translation_key="contact_not_found"
            )
        _changed()

    async def search_contacts(call: ServiceCall) -> dict[str, Any]:
        return {"contacts": await db.search(call.data.get(ATTR_QUERY))}

    async def _guard(func, call):
        try:
            return await func(call)
        except (ServiceValidationError, HomeAssistantError):
            raise
        except Exception as err:
            _LOGGER.error("Address book database error: %s", err)
            raise HomeAssistantError(f"Database error: {err}") from err

    def _wrap(func):
        async def handler(call: ServiceCall):
            return await _guard(func, call)
        return handler

    hass.services.async_register(
        DOMAIN, SERVICE_ADD_CONTACT, _wrap(add_contact), ADD_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(
        DOMAIN, SERVICE_UPDATE_CONTACT, _wrap(update_contact), UPDATE_SCHEMA,
        supports_response=SupportsResponse.OPTIONAL)
    hass.services.async_register(
        DOMAIN, SERVICE_DELETE_CONTACT, _wrap(delete_contact), DELETE_SCHEMA)
    hass.services.async_register(
        DOMAIN, SERVICE_SEARCH_CONTACTS, _wrap(search_contacts), SEARCH_SCHEMA,
        supports_response=SupportsResponse.ONLY)

    await async_setup_api(hass)
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the entry."""
    if not await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        return False
    db: AddressBookBackend = hass.data[DOMAIN].pop(entry.entry_id)
    await db.close()
    if not hass.data[DOMAIN]:
        async_remove_panel(hass)
    for service in (SERVICE_ADD_CONTACT, SERVICE_UPDATE_CONTACT,
                    SERVICE_DELETE_CONTACT, SERVICE_SEARCH_CONTACTS):
        hass.services.async_remove(DOMAIN, service)
    return True
