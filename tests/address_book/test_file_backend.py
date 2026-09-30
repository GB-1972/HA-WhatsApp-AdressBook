"""File backend test with a minimal stand-in for Home Assistant."""

import asyncio
import importlib.util
import pathlib
import sys
import types

_pkg = pathlib.Path(__file__).parents[2] / "custom_components/address_book"


def _load():
    ha = types.ModuleType("homeassistant"); core = types.ModuleType("homeassistant.core")
    core.HomeAssistant = object
    sys.modules.update({"homeassistant": ha, "homeassistant.core": core})
    pkg = types.ModuleType("ab"); pkg.__path__ = [str(_pkg)]; sys.modules["ab"] = pkg
    for name in ("const", "backends"):
        spec = importlib.util.spec_from_file_location(f"ab.{name}", _pkg / f"{name}.py")
        mod = importlib.util.module_from_spec(spec); sys.modules[f"ab.{name}"] = mod
        spec.loader.exec_module(mod)
    return sys.modules["ab.backends"]


class _Hass:
    class config:
        @staticmethod
        def is_allowed_path(_):
            return True

    async def async_add_executor_job(self, fn, *a):
        return fn(*a)


def _c(**kw):
    base = dict.fromkeys(("name", "first_name", "group_name", "mobile", "whatsapp_id"))
    return {**base, **kw}


def test_crud_and_persistence(tmp_path):
    b = _load()
    path = str(tmp_path / "sub" / "ab.json")

    async def run():
        db = await b.FileBackend.connect(_Hass(), path)
        a = await db.add(_c(first_name="Anna", name="Müller"))
        g = await db.add(_c(group_name="Familie"))
        assert (a["id"], g["id"]) == (1, 2)
        assert [r["id"] for r in await db.search("müll")] == [1]
        assert (await db.replace(1, _c(first_name="Anna", mobile="+49170")))["mobile"] == "+49170"
        assert await db.delete(2) and not await db.delete(2)
        db2 = await b.FileBackend.connect(_Hass(), path)  # reload from disk
        assert await db2.count() == 1
        assert (await db2.add(_c(first_name="Neu")))["id"] == 3  # ids never reused

    asyncio.run(run())
