from decimal import Decimal

from app.domain.orcamento import Orcamento, OrcamentoStatus


def test_orcamento_aprovar_recusar():
    o = Orcamento(os_id=1, valor_total=Decimal("150.00"))
    o.marcar_enviado()
    assert o.status == OrcamentoStatus.ENVIADO
    o.aprovar()
    assert o.status == OrcamentoStatus.APROVADO
