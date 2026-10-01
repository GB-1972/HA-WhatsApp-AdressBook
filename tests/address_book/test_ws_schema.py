"""Regression: websocket messages already carry "id" (the message number),
so contact commands must never use "id" as their own field."""

import pathlib
import re

_base = pathlib.Path(__file__).parents[2] / "custom_components/address_book"


def test_api_does_not_use_id_as_contact_field():
    src = (_base / "api.py").read_text()
    assert not re.search(r'vol\.(Optional|Required)\("id"\)', src)
    assert 'in msg' not in src.replace('"contact_id" in msg', "")


def test_frontend_sends_contact_id():
    js = (_base / "www/address-book-panel.js").read_text()
    assert "msg.contact_id = contact.id" in js
    assert "contact_id: c.id" in js
    assert "msg.id =" not in js
