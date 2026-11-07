from __future__ import annotations

import logging
import uuid

from app.settings import get_settings

log = logging.getLogger(__name__)


class MercadoPagoClient:
    """Integração Mercado Pago; em dev sem token retorna preferência simulada."""

    def create_preference(self, os_id: int, orcamento_id: int, amount: float) -> dict:
        token = get_settings().mp_access_token
        if not token:
            pref_id = f"mock-pref-{os_id}-{uuid.uuid4().hex[:8]}"
            return {
                "id": pref_id,
                "init_point": f"{get_settings().public_base_url}/mock-checkout/{pref_id}",
                "sandbox_init_point": f"{get_settings().public_base_url}/mock-checkout/{pref_id}",
            }
        try:
            import mercadopago

            sdk = mercadopago.SDK(token)
            body = {
                "items": [
                    {
                        "title": f"OS #{os_id}",
                        "quantity": 1,
                        "unit_price": amount,
                    }
                ],
                "external_reference": str(os_id),
                "metadata": {"orcamento_id": orcamento_id, "os_id": os_id},
            }
            result = sdk.preference().create(body)
            response = result.get("response", {})
            return {"id": response.get("id"), "init_point": response.get("init_point")}
        except Exception:  # noqa: BLE001
            log.exception("falha mercado pago")
            raise
