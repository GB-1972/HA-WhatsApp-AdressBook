"""Standalone tests for validation rules (no Home Assistant needed)."""

import importlib.util
import pathlib

import pytest

_p = pathlib.Path(__file__).parents[2] / "custom_components/address_book/validation.py"
_s = importlib.util.spec_from_file_location("validation", _p)
v = importlib.util.module_from_spec(_s)
_s.loader.exec_module(v)


def test_first_name_only():
    assert v.validate_contact({"first_name": "Anna"})["first_name"] == "Anna"


def test_group_only():
    assert v.validate_contact({"group_name": "Familie"})["group_name"] == "Familie"


def test_neither_first_nor_group():
    with pytest.raises(v.ContactValidationError, match="first_name_or_group_required"):
        v.validate_contact({"name": "Müller", "mobile": "+491701234567"})


def test_empty_strings_count_as_missing():
    with pytest.raises(v.ContactValidationError):
        v.validate_contact({"first_name": "  ", "group_name": ""})


@pytest.mark.parametrize("m", ["+491701234567", "0170123456"])
def test_mobile_ok(m):
    assert v.validate_contact({"first_name": "A", "mobile": m})["mobile"] == m


@pytest.mark.parametrize("m", ["+49 170", "49+170", "abc", "++49"])
def test_mobile_bad(m):
    with pytest.raises(v.ContactValidationError, match="invalid_mobile"):
        v.validate_contact({"first_name": "A", "mobile": m})


def test_whatsapp_digits_only():
    with pytest.raises(v.ContactValidationError, match="invalid_whatsapp_id"):
        v.validate_contact({"first_name": "A", "whatsapp_id": "+49170"})


@pytest.mark.parametrize("n", ["Müller", "Anna-Lena", "O'Brien", "Meier 2"])
def test_names_ok(n):
    assert v.validate_contact({"first_name": n})["first_name"] == n


@pytest.mark.parametrize("n", ["a@b", "x_y", "<b>", "-a"])
def test_names_bad(n):
    with pytest.raises(v.ContactValidationError):
        v.validate_contact({"name": n, "first_name": "A"})
