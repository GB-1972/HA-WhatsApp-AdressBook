"""Config flow: choose PostgreSQL, MariaDB or a JSON file."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .backends import async_create_backend
from .const import (
    BACKEND_FILE, BACKEND_MARIADB, BACKEND_POSTGRES, CONF_BACKEND, CONF_DATABASE,
    CONF_FILE_PATH, CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME,
    DEFAULT_FILE_PATH, DEFAULT_PORT, DEFAULT_PORT_MARIADB, DOMAIN,
)


def _db_schema(port: int) -> vol.Schema:
    return vol.Schema({
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_PORT, default=port): int,
        vol.Required(CONF_DATABASE): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_SSL, default=False): bool,
    })


class AddressBookConfigFlow(ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        return self.async_show_menu(
            step_id="user", menu_options=[BACKEND_POSTGRES, BACKEND_MARIADB, BACKEND_FILE]
        )

    async def async_step_postgres(self, user_input=None) -> ConfigFlowResult:
        return await self._db_step(BACKEND_POSTGRES, DEFAULT_PORT, user_input)

    async def async_step_mariadb(self, user_input=None) -> ConfigFlowResult:
        return await self._db_step(BACKEND_MARIADB, DEFAULT_PORT_MARIADB, user_input)

    async def async_step_file(self, user_input=None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            path = user_input[CONF_FILE_PATH].strip()
            await self.async_set_unique_id(f"file:{path}")
            self._abort_if_unique_id_configured()
            if not self.hass.config.is_allowed_path(path):
                errors["base"] = "path_not_allowed"
            else:
                data = {CONF_BACKEND: BACKEND_FILE, CONF_FILE_PATH: path}
                try:
                    await async_create_backend(self.hass, data)
                except Exception:  # noqa: BLE001
                    errors["base"] = "cannot_open_file"
                else:
                    return self.async_create_entry(title="Adressbuch (Datei)", data=data)
        schema = vol.Schema({vol.Required(CONF_FILE_PATH, default=DEFAULT_FILE_PATH): str})
        return self.async_show_form(
            step_id="file",
            data_schema=self.add_suggested_values_to_schema(schema, user_input),
            errors=errors,
        )

    async def _db_step(self, backend: str, port: int, user_input) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            await self.async_set_unique_id(
                f"{backend}:{user_input[CONF_HOST]}:{user_input[CONF_PORT]}/{user_input[CONF_DATABASE]}"
            )
            self._abort_if_unique_id_configured()
            data = {CONF_BACKEND: backend, **user_input}
            try:
                await (await async_create_backend(self.hass, data)).close()
            except Exception:  # noqa: BLE001
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=f"Adressbuch ({backend}: {user_input[CONF_DATABASE]})", data=data
                )
        return self.async_show_form(
            step_id=backend,
            data_schema=self.add_suggested_values_to_schema(_db_schema(port), user_input),
            errors=errors,
        )
