from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from decimal import Decimal
from enum import Enum


class OrcamentoStatus(str, Enum):
    RASCUNHO = "RASCUNHO"
    ENVIADO = "ENVIADO"
    APROVADO = "APROVADO"
    RECUSADO = "RECUSADO"


@dataclass
class Orcamento:
    os_id: int
    valor_total: Decimal
    status: OrcamentoStatus = OrcamentoStatus.RASCUNHO
    id: int | None = None
    correlation_id: str | None = None
    mp_preference_id: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def marcar_enviado(self) -> None:
        self.status = OrcamentoStatus.ENVIADO

    def aprovar(self) -> None:
        if self.status not in (OrcamentoStatus.ENVIADO, OrcamentoStatus.RASCUNHO):
            raise ValueError("orçamento não pode ser aprovado")
        self.status = OrcamentoStatus.APROVADO

    def recusar(self) -> None:
        self.status = OrcamentoStatus.RECUSADO
