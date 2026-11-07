import pytest
from fastapi.testclient import TestClient

from app.domain.orcamento import Orcamento, OrcamentoStatus
from app.infrastructure.db import get_session_factory, save_orcamento
from app.main import app


@pytest.fixture
def client() -> TestClient:
    with TestClient(app) as c:
        yield c


def _seed_orcamento(os_id: int, valor: str = "150.00") -> None:
    session = get_session_factory()()
    try:
        o = Orcamento(os_id=os_id, valor_total=__import__("decimal").Decimal(valor))
        save_orcamento(session, o)
        session.commit()
    finally:
        session.close()


def test_health_and_ready(client: TestClient):
    assert client.get("/health").json()["status"] == "ok"
    assert client.get("/ready").json()["status"] == "ok"


def test_get_orcamento_404(client: TestClient):
    assert client.get("/orcamentos/os/9999").status_code == 404


def test_get_orcamento_ok(client: TestClient):
    _seed_orcamento(42)
    r = client.get("/orcamentos/os/42")
    assert r.status_code == 200
    assert r.json()["os_id"] == 42
    assert r.json()["status"] == OrcamentoStatus.RASCUNHO.value


def test_decisao_recusar(client: TestClient):
    _seed_orcamento(7)
    r = client.post("/orcamentos/os/7/decisao", json={"aprovado": False})
    assert r.status_code == 200
    assert r.json()["status"] == OrcamentoStatus.RECUSADO.value


def test_decisao_aprovar_mock_mp(client: TestClient):
    _seed_orcamento(8)
    r = client.post("/orcamentos/os/8/decisao", json={"aprovado": True})
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == OrcamentoStatus.APROVADO.value
    assert "checkout_url" in body


def test_simular_pagamento(client: TestClient):
    _seed_orcamento(9)
    client.post("/orcamentos/os/9/decisao", json={"aprovado": True})
    r = client.post("/orcamentos/os/9/pagamento/simular-aprovado")
    assert r.status_code == 200


def test_mp_webhook_sem_mongo(client: TestClient):
    r = client.post(
        "/webhooks/mercadopago",
        json={
            "data": {"id": "pay-1", "status": "approved"},
            "external_reference": "55",
        },
    )
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_mp_webhook_pagamento_recusado(client: TestClient):
    r = client.post(
        "/webhooks/mercadopago",
        json={
            "data": {"id": "pay-2", "status": "rejected"},
            "external_reference": "56",
        },
    )
    assert r.status_code == 200
