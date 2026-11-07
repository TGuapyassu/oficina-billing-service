from __future__ import annotations

import json

import pika

from app.settings import get_settings
from oficina_contracts.routing import EXCHANGE_EVENTS


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
