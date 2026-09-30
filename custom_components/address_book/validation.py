"""Validation rules for address book entries (no Home Assistant imports)."""

from __future__ import annotations

import re
from typing import Any

# Alphanumeric incl. umlauts/accents; space, hyphen, apostrophe and dot are
# allowed inside because real names contain them ("Anna-Lena", "O'Brien").
_ALNUM_RE = re.compile(r"^[^\W_]+(?:[ .'\-][^\W_]+)*\.?$")
_MOBILE_RE = re.compile(r"^\+?[0-9]+$")
_WHATSAPP_RE = re.compile(r"^[0-9]+$")

FIELDS = ("name", "first_name", "group_name", "mobile", "whatsapp_id")
MAX_LENGTH = 100


class ContactValidationError(ValueError):
    """Raised when a contact violates the rules."""


def _clean(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def validate_contact(data: dict[str, Any]) -> dict[str, str | None]:
    """Return a normalised contact dict or raise ContactValidationError."""
    result: dict[str, str | None] = {f: _clean(data.get(f)) for f in FIELDS}

    for field in ("name", "first_name", "group_name"):
        value = result[field]
        if value is None:
            continue
        if len(value) > MAX_LENGTH or not _ALNUM_RE.match(value):
            raise ContactValidationError(f"invalid_{field}")
    mobile = result["mobile"]
    if mobile is not None and (len(mobile) > 20 or not _MOBILE_RE.match(mobile)):
        raise ContactValidationError("invalid_mobile")
    wa = result["whatsapp_id"]
    if wa is not None and (len(wa) > 30 or not _WHATSAPP_RE.match(wa)):
        raise ContactValidationError("invalid_whatsapp_id")

    if result["first_name"] is None and result["group_name"] is None:
        raise ContactValidationError("first_name_or_group_required")
    return result
