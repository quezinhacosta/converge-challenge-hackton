"""Testes unitarios validando as entidades de dominio do Pulso."""

from app.domain.entities.area import Area
from app.domain.entities.risk_card import CardStatus, RiskCard
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel


def test_area_entity_anonymization_property() -> None:
    """Valida que areas com menos de 5 pessoas sao marcadas como inelegiveis para analise aberta."""
    area_normal = Area(id="area_01", name="Atendimento", headcount=32, manager_name="Juliana")
    area_pequena = Area(id="area_02", name="Design", headcount=3, manager_name="Luciana")

    assert area_normal.is_eligible_for_analytics is True
    assert area_pequena.is_eligible_for_analytics is False


def test_signals_and_risk_card_entities() -> None:
    """Valida a composicao do ponto focal de atencao do RH."""
    card = RiskCard(
        id="card_01",
        area_id="area_01",
        area_name="Atendimento ao Cliente",
        area_headcount=32,
        risk_level=RiskLevel.VERMELHO,
        probable_risk_factor=PsychosocialRiskFactor.SOBRECARGA_METAS,
        evidence_summary="Dias de atestado +45%, horas extras +60%, 4 pedidos de demissao.",
        context_description="Alta comecou 2 semanas apos nova meta de atendimentos por hora.",
        suggested_action="Revisar meta com lideranca e incluir no PGR com reavaliacao em 60 dias.",
        consulted_sources=["ponto", "folha", "desligamentos", "pesquisa pulso"],
    )

    assert card.risk_level == RiskLevel.VERMELHO
    assert card.status == CardStatus.ABERTO
    assert len(card.consulted_sources) == 4
