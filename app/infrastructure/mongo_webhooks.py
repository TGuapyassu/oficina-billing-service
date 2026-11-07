from __future__ import annotations

import logging
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

log = logging.getLogger(__name__)


class WebhookStore:
    def __init__(self, mongo_url: str | None) -> None:
        self._col: Collection | None = None
        if mongo_url:
            client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
            self._col = client.get_database("oficina_billing").get_collection("mp_webhooks")

    def seen(self, payment_id: str) -> bool:
        if self._col is None:
            return False
        return self._col.find_one({"payment_id": payment_id}) is not None

    def store(self, payment_id: str, payload: dict[str, Any]) -> None:
        if self._col is None:
            return
        try:
            self._col.insert_one({"payment_id": payment_id, "payload": payload})
        except Exception:  # noqa: BLE001
            log.warning("mongo webhook store falhou")

    def ping(self) -> bool:
        if self._col is None:
            return True
        try:
            self._col.database.client.admin.command("ping")
            return True
        except Exception:  # noqa: BLE001
            return False
