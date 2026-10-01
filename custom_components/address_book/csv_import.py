"""CSV parsing for the address book import (no Home Assistant imports)."""

from __future__ import annotations

import csv
import io
import re
from typing import Any

from .validation import ContactValidationError, validate_contact

MAX_ROWS = 5000

# Header aliases, compared after lower-casing and dropping spaces, "-" and "_".
_ALIASES: dict[str, set[str]] = {
    "name": {"name", "nachname", "lastname", "surname", "familienname"},
    "first_name": {"firstname", "vorname", "givenname"},
    "group_name": {"groupname", "gruppenname", "gruppe", "group"},
    "mobile": {"mobile", "mobil", "mobilnummer", "handy", "telefon", "phone", "mobilephone"},
    "whatsapp_id": {"whatsappid", "whatsapp"},
}
_HEADER_TO_FIELD = {a: f for f, names in _ALIASES.items() for a in names}


class CsvImportError(ValueError):
    """The file as a whole cannot be imported (message is a translation key)."""


def _norm_header(text: str) -> str:
    return re.sub(r"[\s_\-]", "", text.lower().lstrip("﻿"))


def decode(raw: bytes) -> str:
    """UTF-8 (with/without BOM), falling back to Windows-1252 (Excel on Windows)."""
    try:
        return raw.decode("utf-8-sig")
    except UnicodeDecodeError:
        return raw.decode("cp1252", errors="replace")


def _clean_mobile(value: str) -> str:
    value = re.sub(r"[\s()/.\-]", "", value)
    return "+" + value[2:] if value.startswith("00") else value


def _clean_whatsapp(value: str) -> str:
    return re.sub(r"[\s()/.\-+]", "", value)


def parse_csv(raw: bytes) -> dict[str, Any]:
    """Parse and validate CSV bytes.

    Returns {"rows": [{"line", "data", "error"}], "ignored_columns": [...],
    "delimiter": str}. ``error`` is None for valid rows, else a translation key.
    """
    text = decode(raw).lstrip("\r\n")
    if not text.strip():
        raise CsvImportError("empty_file")
    first_line = text.splitlines()[0]
    delimiter = max(",;\t|", key=first_line.count)
    if first_line.count(delimiter) == 0:
        delimiter = ","

    reader = csv.reader(io.StringIO(text, newline=""), delimiter=delimiter)
    header = next(reader)
    columns: dict[int, str] = {}
    ignored: list[str] = []
    for idx, title in enumerate(header):
        field = _HEADER_TO_FIELD.get(_norm_header(title))
        if field and field not in columns.values():
            columns[idx] = field
        elif title.strip():
            ignored.append(title.strip())
    if not columns:
        raise CsvImportError("no_known_columns")

    rows: list[dict[str, Any]] = []
    for line, record in enumerate(reader, start=2):
        if not any(cell.strip() for cell in record):
            continue
        if len(rows) >= MAX_ROWS:
            raise CsvImportError("too_many_rows")
        raw_data = {f: (record[i].strip() if i < len(record) else "") for i, f in columns.items()}
        if raw_data.get("mobile"):
            raw_data["mobile"] = _clean_mobile(raw_data["mobile"])
        if raw_data.get("whatsapp_id"):
            raw_data["whatsapp_id"] = _clean_whatsapp(raw_data["whatsapp_id"])
        try:
            data, error = validate_contact(raw_data), None
        except ContactValidationError as err:
            data, error = {f: raw_data.get(f) or None for f in columns.values()}, str(err)
        rows.append({"line": line, "data": data, "error": error})
    return {"rows": rows, "ignored_columns": ignored, "delimiter": delimiter}


def duplicate_key(contact: dict[str, Any]) -> tuple[str, ...]:
    """Identity used to skip duplicates (case-insensitive)."""
    return tuple(
        (contact.get(f) or "").lower()
        for f in ("name", "first_name", "group_name", "mobile")
    )
