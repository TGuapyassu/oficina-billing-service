from __future__ import annotations

import json
from collections.abc import Callable
from decimal import Decimal

from sqlalchemy.orm import Session

from app.domain.orcamento import Orcamento
from app.infrastructure.db import get_orcamento_by_os, save_orcamento
from app.infrastructure.publisher import publish
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


def handle_event(
    session: Session,
    body: bytes,
    fetch_os_items: Callable[[int], dict],
) -> None:
    data = json.loads(body)
    os_id = data.get("os_id")
    if os_id is None:
        return
    if get_orcamento_by_os(session, os_id):
        return
    correlation_id = data.get("correlation_id")
    try:
        items = fetch_os_items(os_id)
        valor = Decimal(str(items["valor_total"]))
    except Exception:  # noqa: BLE001
        publish(
            RoutingKey.BUDGET_CREATION_FAILED.value,
            DomainEvent.create(
                RoutingKey.BUDGET_CREATION_FAILED,
                os_id=os_id,
                correlation_id=correlation_id,
                reason="os_items_unavailable",
            ).model_dump(mode="json"),
        )
        return
    orc = Orcamento(os_id=os_id, valor_total=valor, correlation_id=correlation_id)
    orc.marcar_enviado()
    save_orcamento(session, orc)
    publish(
        RoutingKey.BUDGET_CREATED.value,
        DomainEvent.create(
            RoutingKey.BUDGET_CREATED,
            os_id=os_id,
            correlation_id=correlation_id,
            orcamento_id=orc.id,
            valor_total=str(valor),
        ).model_dump(mode="json"),
    )
