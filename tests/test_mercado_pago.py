from app.infrastructure.mercado_pago import MercadoPagoClient


def test_mock_preference_without_token():
    pref = MercadoPagoClient().create_preference(1, 10, 99.9)
    assert pref["id"].startswith("mock-pref-")
    assert "init_point" in pref
