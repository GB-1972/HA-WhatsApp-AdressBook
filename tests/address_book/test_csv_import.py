"""CSV import parsing tests (no Home Assistant needed)."""

import importlib.util
import pathlib
import sys
import types

import pytest

_pkg = pathlib.Path(__file__).parents[2] / "custom_components/address_book"


def _load():
    pkg = types.ModuleType("abcsv")
    pkg.__path__ = [str(_pkg)]
    sys.modules["abcsv"] = pkg
    for name in ("validation", "csv_import"):
        spec = importlib.util.spec_from_file_location(f"abcsv.{name}", _pkg / f"{name}.py")
        mod = importlib.util.module_from_spec(spec)
        sys.modules[f"abcsv.{name}"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["abcsv.csv_import"]


c = _load()


def test_semicolon_german_headers_and_normalisation():
    raw = ("Nachname;Vorname;Gruppe;Handy;WhatsApp\n"
           "Müller;Anna;;0049 170 123-4567;+49 170 1234567\n").encode()
    r = c.parse_csv(raw)
    assert r["delimiter"] == ";"
    d = r["rows"][0]["data"]
    assert r["rows"][0]["error"] is None
    assert (d["name"], d["first_name"], d["mobile"], d["whatsapp_id"]) == (
        "Müller", "Anna", "+491701234567", "491701234567")


def test_comma_english_headers_bom():
    raw = "﻿first_name,name,group_name\nBob,Smith,\n,,Family\n".encode("utf-8")
    r = c.parse_csv(raw)
    assert [x["error"] for x in r["rows"]] == [None, None]
    assert r["rows"][1]["data"]["group_name"] == "Family"


def test_windows_1252_fallback():
    r = c.parse_csv("Name;Vorname\nMüller;Jürgen\n".encode("cp1252"))
    assert r["rows"][0]["data"]["name"] == "Müller"


def test_row_errors_do_not_abort():
    raw = b"Name;Vorname;Mobil\nA;;123\nB;Bea;abc\nC;Cy;+49\n"
    errs = [x["error"] for x in c.parse_csv(raw)["rows"]]
    assert errs == ["first_name_or_group_required", "invalid_mobile", None]


def test_blank_rows_skipped_and_line_numbers():
    r = c.parse_csv(b"Vorname;Name\nAnna;\n\n;\nBen;\n")
    assert [x["line"] for x in r["rows"]] == [2, 5]


def test_ignored_columns_and_unknown_file():
    r = c.parse_csv(b"Vorname;Geburtstag\nAnna;1.1.\n")
    assert r["ignored_columns"] == ["Geburtstag"]
    with pytest.raises(c.CsvImportError, match="no_known_columns"):
        c.parse_csv(b"foo;bar\n1;2\n")
    with pytest.raises(c.CsvImportError, match="empty_file"):
        c.parse_csv(b"  \n")


def test_duplicate_key_case_insensitive():
    a = {"name": "Müller", "first_name": "Anna", "group_name": None, "mobile": "+49"}
    b = {"name": "MÜLLER", "first_name": "anna", "group_name": None, "mobile": "+49"}
    assert c.duplicate_key(a) == c.duplicate_key(b)
