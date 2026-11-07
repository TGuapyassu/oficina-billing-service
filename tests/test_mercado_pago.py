import sys
import types

import pytest

from app.infrastructure.mercado_pago import MercadoPagoClient
from app.settings import get_settings


def test_mock_preference_without_token():
    pref = MercadoPagoClient().create_preference(1, 10, 99.9)
    assert pref["id"].startswith("mock-pref-")
    assert "init_point" in pref


def test_preference_com_token_sdk(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("MP_ACCESS_TOKEN", "test-token")
    get_settings.cache_clear()

    class _Pref:
        def create(self, body: dict) -> dict:
            assert body["external_reference"] == "3"
            return {"response": {"id": "pref-real", "init_point": "https://mp/checkout"}}

    class _Sdk:
        def preference(self) -> _Pref:
            return _Pref()

    mp_mod = types.ModuleType("mercadopago")
    mp_mod.SDK = lambda token: _Sdk()  # noqa: E731
    monkeypatch.setitem(sys.modules, "mercadopago", mp_mod)

    pref = MercadoPagoClient().create_preference(3, 9, 120.0)
    assert pref["id"] == "pref-real"
    assert pref["init_point"].startswith("https://")
    get_settings.cache_clear()
