from decimal import Decimal

from app.application.billing_handlers import handle_event
from app.infrastructure.db import get_orcamento_by_os, get_session_factory, init_db
from oficina_contracts.events import DomainEvent
from oficina_contracts.routing import RoutingKey


def test_cria_orcamento_via_evento():
    init_db()
    session = get_session_factory()()

    def fetch(_os_id: int) -> dict:
        return {"valor_total": "200.00"}

    ev = DomainEvent.create(RoutingKey.EXECUTION_DIAGNOSIS_COMPLETED, os_id=7)
    handle_event(session, ev.model_dump_json().encode(), fetch)
    session.commit()
    o = get_orcamento_by_os(session, 7)
    assert o is not None
    assert o.valor_total == Decimal("200.00")
    session.close()
