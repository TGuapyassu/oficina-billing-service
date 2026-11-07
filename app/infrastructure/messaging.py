from __future__ import annotations

import json
import logging
import threading
import time

import httpx
import pika

from app.application.billing_handlers import handle_event
from app.infrastructure.db import get_session_factory, init_db
from app.settings import get_settings
from oficina_contracts.routing import EXCHANGE_EVENTS

log = logging.getLogger(__name__)


def publish(routing_key: str, body: dict) -> None:
    url = get_settings().rabbitmq_url
    if not url:
        return
    conn = pika.BlockingConnection(pika.URLParameters(url))
    ch = conn.channel()
    ch.exchange_declare(exchange=EXCHANGE_EVENTS, exchange_type="topic", durable=True)
    ch.basic_publish(
        exchange=EXCHANGE_EVENTS,
        routing_key=routing_key,
        body=json.dumps(body, default=str),
        properties=pika.BasicProperties(delivery_mode=2, content_type="application/json"),
    )
    conn.close()


def fetch_os_items(os_id: int):
    s = get_settings()
    url = f"{s.os_service_url.rstrip('/')}/internal/os/{os_id}/items"
    headers = {"X-Internal-Service-Key": s.internal_service_key}
    r = httpx.get(url, headers=headers, timeout=10.0)
    r.raise_for_status()
    return r.json()


def _loop(stop: threading.Event) -> None:
    url = get_settings().rabbitmq_url
    if not url:
        return
    init_db()
    while not stop.is_set():
        try:
            conn = pika.BlockingConnection(pika.URLParameters(url))
            ch = conn.channel()
            ch.exchange_declare(exchange=EXCHANGE_EVENTS, exchange_type="topic", durable=True)
            q = ch.queue_declare(queue="billing-service.saga", durable=True)
            ch.queue_bind(
                exchange=EXCHANGE_EVENTS,
                queue=q.method.queue,
                routing_key="execution.diagnosis_completed",
            )

            def _on(_ch, method, _props, body: bytes) -> None:
                session = get_session_factory()()
                try:
                    handle_event(session, body, fetch_os_items)
                    session.commit()
                    _ch.basic_ack(delivery_tag=method.delivery_tag)
                except Exception:  # noqa: BLE001
                    log.exception("billing handler")
                    session.rollback()
                    _ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
                finally:
                    session.close()

            ch.basic_consume(queue=q.method.queue, on_message_callback=_on)
            while not stop.is_set():
                conn.process_data_events(time_limit=1)
            conn.close()
        except Exception:  # noqa: BLE001
            time.sleep(3)


def start_consumer(stop: threading.Event) -> threading.Thread:
    t = threading.Thread(target=_loop, args=(stop,), daemon=True, name="billing-rmq")
    t.start()
    return t
