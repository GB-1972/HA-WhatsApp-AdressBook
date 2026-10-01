"""Websocket API, CSV upload endpoint and sidebar panel for the address book."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any

import voluptuous as vol
from aiohttp import web

from homeassistant.components import frontend, panel_custom, websocket_api
from homeassistant.components.http import HomeAssistantView, StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.http import KEY_HASS

from .backends import AddressBookBackend
from .const import DOMAIN, SIGNAL_CONTACTS_CHANGED
from .csv_import import CsvImportError, duplicate_key, parse_csv
from .validation import FIELDS, ContactValidationError, validate_contact

_LOGGER = logging.getLogger(__name__)

STATIC_URL = f"/{DOMAIN}_static"
PANEL_ELEMENT = "address-book-panel"
MAX_UPLOAD_BYTES = 5 * 1024 * 1024
_API_KEY = f"{DOMAIN}_api_registered"
_STATIC_KEY = f"{DOMAIN}_static_registered"


def _backend(hass: HomeAssistant) -> AddressBookBackend | None:
    backends = hass.data.get(DOMAIN, {})
    return next(iter(backends.values()), None)


def _changed(hass: HomeAssistant) -> None:
    async_dispatcher_send(hass, SIGNAL_CONTACTS_CHANGED)


# --------------------------------------------------------------------------- websocket
_OPT = vol.Any(None, str)


@websocket_api.websocket_command({vol.Required("type"): f"{DOMAIN}/list"})
@websocket_api.require_admin
@websocket_api.async_response
async def ws_list(hass: HomeAssistant, connection, msg) -> None:
    db = _backend(hass)
    if db is None:
        connection.send_error(msg["id"], "not_loaded", "address_book_not_loaded")
        return
    try:
        connection.send_result(msg["id"], {"contacts": await db.search()})
    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Address book list failed: %s", err)
        connection.send_error(msg["id"], "db_error", "db_error")


@websocket_api.websocket_command(
    {
        vol.Required("type"): f"{DOMAIN}/save",
        vol.Optional("id"): int,
        **{vol.Optional(f): _OPT for f in FIELDS},
    }
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_save(hass: HomeAssistant, connection, msg) -> None:
    db = _backend(hass)
    if db is None:
        connection.send_error(msg["id"], "not_loaded", "address_book_not_loaded")
        return
    try:
        contact = validate_contact(msg)
    except ContactValidationError as err:
        connection.send_error(msg["id"], "invalid", str(err))
        return
    try:
        if "id" in msg:
            row = await db.replace(msg["id"], contact)
            if row is None:
                connection.send_error(msg["id"], "not_found", "contact_not_found")
                return
        else:
            row = await db.add(contact)
    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Address book save failed: %s", err)
        connection.send_error(msg["id"], "db_error", "db_error")
        return
    _changed(hass)
    connection.send_result(msg["id"], row)


@websocket_api.websocket_command(
    {vol.Required("type"): f"{DOMAIN}/delete", vol.Required("id"): int}
)
@websocket_api.require_admin
@websocket_api.async_response
async def ws_delete(hass: HomeAssistant, connection, msg) -> None:
    db = _backend(hass)
    if db is None:
        connection.send_error(msg["id"], "not_loaded", "address_book_not_loaded")
        return
    try:
        deleted = await db.delete(msg["id"])
    except Exception as err:  # noqa: BLE001
        _LOGGER.error("Address book delete failed: %s", err)
        connection.send_error(msg["id"], "db_error", "db_error")
        return
    if not deleted:
        connection.send_error(msg["id"], "not_found", "contact_not_found")
        return
    _changed(hass)
    connection.send_result(msg["id"], {})


# --------------------------------------------------------------------------- CSV upload
class ImportView(HomeAssistantView):
    """POST a CSV file; ``dry_run=1`` only previews, otherwise imports."""

    url = f"/api/{DOMAIN}/import"
    name = f"api:{DOMAIN}:import"
    requires_auth = True

    async def post(self, request: web.Request) -> web.Response:
        hass: HomeAssistant = request.app[KEY_HASS]
        if not request["hass_user"].is_admin:
            return self.json({"error": "admin_required"}, status_code=403)
        db = _backend(hass)
        if db is None:
            return self.json({"error": "address_book_not_loaded"}, status_code=503)

        dry_run = request.query.get("dry_run", "1") == "1"
        skip_duplicates = request.query.get("skip_duplicates", "1") == "1"

        form = await request.post()
        upload = form.get("file")
        if upload is None or not hasattr(upload, "file"):
            return self.json({"error": "no_file"}, status_code=400)
        raw = upload.file.read(MAX_UPLOAD_BYTES + 1)
        if len(raw) > MAX_UPLOAD_BYTES:
            return self.json({"error": "file_too_large"}, status_code=413)

        try:
            parsed = parse_csv(raw)
        except CsvImportError as err:
            return self.json({"error": str(err)}, status_code=400)

        try:
            seen = {duplicate_key(c) for c in await db.search()}
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Address book import failed: %s", err)
            return self.json({"error": "db_error"}, status_code=500)

        for row in parsed["rows"]:
            row["status"] = "error"
            if row["error"]:
                continue
            key = duplicate_key(row["data"])
            if skip_duplicates and key in seen:
                row["status"] = "duplicate"
            else:
                row["status"] = "new"
                seen.add(key)

        summary = {
            s: sum(1 for r in parsed["rows"] if r["status"] == s)
            for s in ("new", "duplicate", "error")
        }
        if dry_run:
            return self.json({**parsed, "summary": summary})

        imported = failed = 0
        for row in parsed["rows"]:
            if row["status"] != "new":
                continue
            try:
                await db.add(row["data"])
                imported += 1
            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Address book import row %s failed: %s", row["line"], err)
                row["status"], row["error"] = "error", "db_error"
                failed += 1
        if imported:
            _changed(hass)
        return self.json(
            {
                "imported": imported,
                "duplicates": summary["duplicate"],
                "errors": summary["error"] + failed,
                "rows": [r for r in parsed["rows"] if r["status"] == "error"],
            }
        )


# --------------------------------------------------------------------------- setup
async def async_setup_api(hass: HomeAssistant) -> None:
    """Register websocket commands, upload view, static files and the panel."""
    if not hass.data.get(_API_KEY):
        websocket_api.async_register_command(hass, ws_list)
        websocket_api.async_register_command(hass, ws_save)
        websocket_api.async_register_command(hass, ws_delete)
        hass.http.register_view(ImportView())
        hass.data[_API_KEY] = True

    www = Path(__file__).parent / "www"
    if not hass.data.get(_STATIC_KEY):
        await hass.http.async_register_static_paths(
            [StaticPathConfig(STATIC_URL, str(www), cache_headers=False)]
        )
        hass.data[_STATIC_KEY] = True

    if DOMAIN not in hass.data.get("frontend_panels", {}):
        version = int((www / f"{PANEL_ELEMENT}.js").stat().st_mtime)
        await panel_custom.async_register_panel(
            hass,
            webcomponent_name=PANEL_ELEMENT,
            frontend_url_path=DOMAIN,
            module_url=f"{STATIC_URL}/{PANEL_ELEMENT}.js?v={version}",
            sidebar_title="Adressbuch",
            sidebar_icon="mdi:contacts",
            require_admin=True,
        )


def async_remove_panel(hass: HomeAssistant) -> None:
    """Remove the sidebar panel."""
    frontend.async_remove_panel(hass, DOMAIN)
