from __future__ import annotations

import threading
from contextlib import asynccontextmanager
from decimal import Decimal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from app.domain.orcamento import OrcamentoStatus
from app.infrastructure.db import PagamentoOrm, get_orcamento_by_os, get_session_factory, init_db, save_orcamento
from app.infrastructure.mercado_pago import MercadoPagoClient
from app.infrastructure.messaging import start_consumer
from app.infrastructure.publisher import publish
from app.infrastructure.mongo_webhooks import WebhookStore
from app.settings import get_settings
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey

_stop: threading.Event | None = None


class DecisaoIn(BaseModel):
    aprovado: bool


@asynccontextmanager
async def lifespan(_: FastAPI):
    global _stop
    init_db()
    _stop = threading.Event()
    start_consumer(_stop)
    yield
    if _stop:
        _stop.set()


app = FastAPI(title="Oficina Billing Service", version="0.1.0", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready() -> dict:
    s = get_settings()
    return {"status": "ok", "mongodb": WebhookStore(s.mongodb_url or None).ping()}


@app.get("/orcamentos/os/{os_id}")
def get_orcamento(os_id: int) -> dict:
    session = get_session_factory()()
    try:
        o = get_orcamento_by_os(session, os_id)
        if not o:
            raise HTTPException(404, "Orçamento não encontrado")
        return {
            "id": o.id,
            "os_id": o.os_id,
            "valor_total": str(o.valor_total),
            "status": o.status.value,
            "mp_preference_id": o.mp_preference_id,
        }
    finally:
        session.close()


@app.post("/orcamentos/os/{os_id}/decisao")
def decidir(os_id: int, body: DecisaoIn) -> dict:
    session = get_session_factory()()
    try:
        o = get_orcamento_by_os(session, os_id)
        if not o:
            raise HTTPException(404, "Orçamento não encontrado")
        if body.aprovado:
            o.aprovar()
            save_orcamento(session, o)
            mp = MercadoPagoClient().create_preference(os_id, o.id or 0, float(o.valor_total))
            o.mp_preference_id = mp.get("id")
            save_orcamento(session, o)
            session.commit()
            publish(
                RoutingKey.BUDGET_APPROVED.value,
                DomainEvent.create(RoutingKey.BUDGET_APPROVED, os_id=os_id, orcamento_id=o.id).model_dump(mode="json"),
            )
            publish(
                RoutingKey.PAYMENT_PENDING.value,
                DomainEvent.create(RoutingKey.PAYMENT_PENDING, os_id=os_id, preference_id=o.mp_preference_id).model_dump(mode="json"),
            )
            return {"status": o.status.value, "checkout_url": mp.get("init_point")}
        o.recusar()
        save_orcamento(session, o)
        session.commit()
        publish(
            RoutingKey.BUDGET_REJECTED.value,
            DomainEvent.create(RoutingKey.BUDGET_REJECTED, os_id=os_id).model_dump(mode="json"),
        )
        return {"status": o.status.value}
    finally:
        session.close()


@app.post("/orcamentos/os/{os_id}/pagamento/simular-aprovado")
def simular_pagamento(os_id: int) -> dict:
    """Ambiente de testes: confirma pagamento sem chamar o MP."""
    session = get_session_factory()()
    try:
        o = get_orcamento_by_os(session, os_id)
        if not o:
            raise HTTPException(404, "Orçamento não encontrado")
        payment_id = f"mock-pay-{os_id}"
        session.add(
            PagamentoOrm(
                os_id=os_id,
                orcamento_id=o.id or 0,
                mp_payment_id=payment_id,
                status="approved",
                created_at=__import__("datetime").datetime.now(__import__("datetime").UTC),
            )
        )
        session.commit()
        publish(
            RoutingKey.PAYMENT_CONFIRMED.value,
            DomainEvent.create(
                RoutingKey.PAYMENT_CONFIRMED,
                os_id=os_id,
                payment_id=payment_id,
            ).model_dump(mode="json"),
        )
        return {"ok": True, "payment_id": payment_id}
    finally:
        session.close()


@app.post("/webhooks/mercadopago")
async def mp_webhook(payload: dict) -> dict:
    store = WebhookStore(get_settings().mongodb_url or None)
    data = payload.get("data", {}) or payload
    payment_id = str(data.get("id") or payload.get("id") or "")
    if payment_id and store.seen(payment_id):
        return {"ok": True, "duplicate": True}
    store.store(payment_id or "unknown", payload)
    os_id = payload.get("external_reference") or (data.get("metadata") or {}).get("os_id")
    status = (data.get("status") or payload.get("action") or "").lower()
    if os_id and status in ("approved", "payment.created"):
        publish(
            RoutingKey.PAYMENT_CONFIRMED.value,
            DomainEvent.create(RoutingKey.PAYMENT_CONFIRMED, os_id=int(os_id), payment_id=payment_id).model_dump(mode="json"),
        )
    elif os_id and status in ("rejected", "cancelled"):
        publish(
            RoutingKey.PAYMENT_FAILED.value,
            DomainEvent.create(RoutingKey.PAYMENT_FAILED, os_id=int(os_id), payment_id=payment_id).model_dump(mode="json"),
        )
    return {"ok": True}
