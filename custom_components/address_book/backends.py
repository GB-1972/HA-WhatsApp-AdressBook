"""Storage backends: PostgreSQL, MariaDB and a JSON text file."""

from __future__ import annotations

import asyncio
import json
import os
from abc import ABC, abstractmethod
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    BACKEND_FILE, BACKEND_MARIADB, BACKEND_POSTGRES, CONF_DATABASE, CONF_FILE_PATH,
    CONF_HOST, CONF_PASSWORD, CONF_PORT, CONF_SSL, CONF_USERNAME,
)

TABLE = "address_book_contacts"
FIELDS = ("name", "first_name", "group_name", "mobile", "whatsapp_id")
_COLUMNS = "id, name, first_name, group_name, mobile, whatsapp_id"
_ORDER = "ORDER BY lower(name), lower(first_name), lower(group_name)"
_SEARCH_EXPR = "concat_ws(' ', name, first_name, group_name, mobile, whatsapp_id)"


class AddressBookBackend(ABC):
    """Common interface used by services and the sensor."""

    @abstractmethod
    async def add(self, c: dict[str, Any]) -> dict[str, Any]: ...

    @abstractmethod
    async def get(self, contact_id: int) -> dict[str, Any] | None: ...

    @abstractmethod
    async def replace(self, contact_id: int, c: dict[str, Any]) -> dict[str, Any] | None: ...

    @abstractmethod
    async def delete(self, contact_id: int) -> bool: ...

    @abstractmethod
    async def search(self, query: str | None = None) -> list[dict[str, Any]]: ...

    @abstractmethod
    async def count(self) -> int: ...

    async def close(self) -> None:
        """Release resources."""


# --------------------------------------------------------------------------- PostgreSQL
_PG_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    id          SERIAL PRIMARY KEY,
    name        VARCHAR(100),
    first_name  VARCHAR(100),
    group_name  VARCHAR(100),
    mobile      VARCHAR(20),
    whatsapp_id VARCHAR(30),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT {TABLE}_first_or_group CHECK (first_name IS NOT NULL OR group_name IS NOT NULL),
    CONSTRAINT {TABLE}_mobile_fmt CHECK (mobile IS NULL OR mobile ~ '^[+]?[0-9]+$'),
    CONSTRAINT {TABLE}_whatsapp_fmt CHECK (whatsapp_id IS NULL OR whatsapp_id ~ '^[0-9]+$')
);
CREATE INDEX IF NOT EXISTS {TABLE}_lower_name_idx ON {TABLE} (lower(name));
"""


class PostgresBackend(AddressBookBackend):
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    @classmethod
    async def connect(cls, host, port, database, user, password, ssl=False):
        import asyncpg  # imported lazily: only needed for this backend

        pool = await asyncpg.create_pool(
            host=host, port=port, database=database, user=user, password=password,
            ssl=ssl or None, min_size=1, max_size=3, timeout=10,
        )
        async with pool.acquire() as conn:
            await conn.execute(_PG_SCHEMA)
        return cls(pool)

    async def close(self) -> None:
        await self._pool.close()

    async def add(self, c):
        row = await self._pool.fetchrow(
            f"INSERT INTO {TABLE} (name, first_name, group_name, mobile, whatsapp_id) "
            f"VALUES ($1,$2,$3,$4,$5) RETURNING {_COLUMNS}",
            *(c[f] for f in FIELDS),
        )
        return dict(row)

    async def get(self, contact_id):
        row = await self._pool.fetchrow(f"SELECT {_COLUMNS} FROM {TABLE} WHERE id=$1", contact_id)
        return dict(row) if row else None

    async def replace(self, contact_id, c):
        row = await self._pool.fetchrow(
            f"UPDATE {TABLE} SET name=$2, first_name=$3, group_name=$4, mobile=$5, "
            f"whatsapp_id=$6, updated_at=now() WHERE id=$1 RETURNING {_COLUMNS}",
            contact_id, *(c[f] for f in FIELDS),
        )
        return dict(row) if row else None

    async def delete(self, contact_id):
        return (await self._pool.execute(f"DELETE FROM {TABLE} WHERE id=$1", contact_id)).endswith(" 1")

    async def search(self, query=None):
        if query:
            rows = await self._pool.fetch(
                f"SELECT {_COLUMNS} FROM {TABLE} WHERE {_SEARCH_EXPR} ILIKE $1 {_ORDER}",
                f"%{query}%",
            )
        else:
            rows = await self._pool.fetch(f"SELECT {_COLUMNS} FROM {TABLE} {_ORDER}")
        return [dict(r) for r in rows]

    async def count(self):
        return await self._pool.fetchval(f"SELECT count(*) FROM {TABLE}")


# --------------------------------------------------------------------------- MariaDB
_MARIA_SCHEMA = f"""
CREATE TABLE IF NOT EXISTS {TABLE} (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(100) NULL,
    first_name  VARCHAR(100) NULL,
    group_name  VARCHAR(100) NULL,
    mobile      VARCHAR(20) NULL,
    whatsapp_id VARCHAR(30) NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at  TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT {TABLE}_first_or_group CHECK (first_name IS NOT NULL OR group_name IS NOT NULL),
    CONSTRAINT {TABLE}_mobile_fmt CHECK (mobile IS NULL OR mobile REGEXP '^[+]?[0-9]+$'),
    CONSTRAINT {TABLE}_whatsapp_fmt CHECK (whatsapp_id IS NULL OR whatsapp_id REGEXP '^[0-9]+$'),
    INDEX {TABLE}_name_idx (name)
) CHARACTER SET utf8mb4
"""


class MariaDBBackend(AddressBookBackend):
    def __init__(self, pool: Any) -> None:
        self._pool = pool

    @classmethod
    async def connect(cls, host, port, database, user, password, ssl=False):
        import aiomysql

        pool = await aiomysql.create_pool(
            host=host, port=port, db=database, user=user, password=password,
            ssl=True if ssl else None, minsize=1, maxsize=3, autocommit=True,
            charset="utf8mb4", connect_timeout=10,
        )
        backend = cls(pool)
        await backend._exec(_MARIA_SCHEMA)
        return backend

    async def _exec(self, sql: str, args: tuple = (), fetch: str | None = None):
        import aiomysql

        async with self._pool.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql, args)
                if fetch == "one":
                    return await cur.fetchone()
                if fetch == "all":
                    return await cur.fetchall()
                if fetch == "insert":
                    return cur.lastrowid
                return cur.rowcount

    async def close(self) -> None:
        self._pool.close()
        await self._pool.wait_closed()

    async def add(self, c):
        new_id = await self._exec(
            f"INSERT INTO {TABLE} (name, first_name, group_name, mobile, whatsapp_id) "
            "VALUES (%s,%s,%s,%s,%s)",
            tuple(c[f] for f in FIELDS), "insert",
        )
        return await self.get(new_id)

    async def get(self, contact_id):
        return await self._exec(
            f"SELECT {_COLUMNS} FROM {TABLE} WHERE id=%s", (contact_id,), "one"
        )

    async def replace(self, contact_id, c):
        await self._exec(
            f"UPDATE {TABLE} SET name=%s, first_name=%s, group_name=%s, mobile=%s, "
            "whatsapp_id=%s WHERE id=%s",
            (*(c[f] for f in FIELDS), contact_id),
        )
        return await self.get(contact_id)

    async def delete(self, contact_id):
        return await self._exec(f"DELETE FROM {TABLE} WHERE id=%s", (contact_id,)) > 0

    async def search(self, query=None):
        if query:
            escaped = query.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            return list(await self._exec(
                f"SELECT {_COLUMNS} FROM {TABLE} WHERE {_SEARCH_EXPR} LIKE %s {_ORDER}",
                (f"%{escaped}%",), "all",
            ))
        return list(await self._exec(f"SELECT {_COLUMNS} FROM {TABLE} {_ORDER}", (), "all"))

    async def count(self):
        row = await self._exec(f"SELECT count(*) AS n FROM {TABLE}", (), "one")
        return row["n"]


# --------------------------------------------------------------------------- JSON file
class FileBackend(AddressBookBackend):
    """Contacts in a single JSON text file (atomic writes)."""

    def __init__(self, hass: HomeAssistant, path: str) -> None:
        self._hass = hass
        self._path = path
        self._lock = asyncio.Lock()
        self._next_id = 1
        self._contacts: list[dict[str, Any]] = []

    @classmethod
    async def connect(cls, hass: HomeAssistant, path: str) -> FileBackend:
        if not hass.config.is_allowed_path(path):
            raise ValueError("path_not_allowed")
        self = cls(hass, path)
        await hass.async_add_executor_job(self._load)
        return self

    def _load(self) -> None:
        directory = os.path.dirname(self._path) or "."
        os.makedirs(directory, exist_ok=True)
        if os.path.exists(self._path):
            with open(self._path, encoding="utf-8") as fh:
                data = json.load(fh)
            self._contacts = data.get("contacts", [])
            self._next_id = data.get("next_id", 1 + max((c["id"] for c in self._contacts), default=0))
        else:
            self._save()  # also proves the location is writable

    def _save(self) -> None:
        tmp = f"{self._path}.tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump({"next_id": self._next_id, "contacts": self._contacts},
                      fh, ensure_ascii=False, indent=2)
        os.replace(tmp, self._path)

    async def _persist(self) -> None:
        await self._hass.async_add_executor_job(self._save)

    async def add(self, c):
        async with self._lock:
            row = {"id": self._next_id, **{f: c[f] for f in FIELDS}}
            self._next_id += 1
            self._contacts.append(row)
            await self._persist()
            return dict(row)

    async def get(self, contact_id):
        row = next((r for r in self._contacts if r["id"] == contact_id), None)
        return dict(row) if row else None

    async def replace(self, contact_id, c):
        async with self._lock:
            row = next((r for r in self._contacts if r["id"] == contact_id), None)
            if row is None:
                return None
            row.update({f: c[f] for f in FIELDS})
            await self._persist()
            return dict(row)

    async def delete(self, contact_id):
        async with self._lock:
            before = len(self._contacts)
            self._contacts = [r for r in self._contacts if r["id"] != contact_id]
            if len(self._contacts) == before:
                return False
            await self._persist()
            return True

    async def search(self, query=None):
        rows = self._contacts
        if query:
            q = query.lower()
            rows = [r for r in rows
                    if q in " ".join(str(r[f]) for f in FIELDS if r.get(f)).lower()]
        key = lambda r: tuple((r.get(f) or "").lower() for f in ("name", "first_name", "group_name"))
        return [dict(r) for r in sorted(rows, key=key)]

    async def count(self):
        return len(self._contacts)


async def async_create_backend(hass: HomeAssistant, conf: dict[str, Any]) -> AddressBookBackend:
    """Build a backend from config-entry data (old entries default to PostgreSQL)."""
    kind = conf.get("backend", BACKEND_POSTGRES)
    if kind == BACKEND_FILE:
        return await FileBackend.connect(hass, conf[CONF_FILE_PATH])
    cls = MariaDBBackend if kind == BACKEND_MARIADB else PostgresBackend
    return await cls.connect(
        conf[CONF_HOST], conf[CONF_PORT], conf[CONF_DATABASE],
        conf[CONF_USERNAME], conf[CONF_PASSWORD], conf.get(CONF_SSL, False),
    )
