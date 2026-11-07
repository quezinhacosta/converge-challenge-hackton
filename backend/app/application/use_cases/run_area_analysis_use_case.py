"""Caso de uso que roda o ciclo do Pulso numa area (ou em todas, no fechamento da folha).

Junta analise (etapas 1 a 5) e abertura do card (etapas 6 e 7), sem duplicar card:
se a area ja tem card aberto ou escalado, devolve esse card em vez de criar outro.
"""

from typing import Any

from app.application.use_cases.analyze_psychosocial_risks_use_case import (
    AnalyzePsychosocialRisksUseCase,
)
from app.application.use_cases.generate_risk_card_use_case import GenerateRiskCardUseCase
from app.domain.entities.risk_card import CardStatus
from app.domain.entities.risk_factor import RiskLevel
from app.domain.repositories.interfaces import AreaRepository, RiskCardRepository

_PENDING_STATUSES = {CardStatus.ABERTO, CardStatus.ESCALADO_COMPLIANCE}


def _value(item: Any) -> Any:
    return getattr(item, "value", item)


class RunAreaAnalysisUseCase:
    """Executa a analise de uma area e abre card quando o nivel for amarelo ou vermelho."""

    def __init__(
        self,
        area_repository: AreaRepository,
        risk_card_repository: RiskCardRepository,
        analyze_use_case: AnalyzePsychosocialRisksUseCase,
        generate_card_use_case: GenerateRiskCardUseCase,
    ) -> None:
        self.area_repository = area_repository
        self.risk_card_repository = risk_card_repository
        self.analyze_use_case = analyze_use_case
        self.generate_card_use_case = generate_card_use_case

    def execute(self, area_id: str) -> dict[str, Any]:
        """Analisa a area. Lanca ValueError se a area nao existir."""
        analysis = self.analyze_use_case.execute(area_id)
        level = _value(analysis["risk_level"])
        result: dict[str, Any] = {
            "areaId": analysis["area_id"],
            "areaName": analysis["area_name"],
            "riskLevel": level,
            "factor": _value(analysis["factor"]),
            "evidenceSummary": analysis.get("evidence_summary", ""),
            "suggestedAction": analysis.get("suggested_action", ""),
            "isAnonymized": bool(analysis.get("is_anonymized", False)),
            "aiExecution": analysis.get("ai_execution_metadata", {}),
            "cardStatus": "SEM_CARD",
            "cardId": None,
        }
        if result["isAnonymized"] or level == RiskLevel.VERDE.value:
            return result

        pending = [
            c
            for c in self.risk_card_repository.list_all()
            if c.area_id == area_id and c.status in _PENDING_STATUSES
        ]
        if pending:
            result["cardStatus"] = "CARD_JA_EXISTENTE"
            result["cardId"] = pending[0].id
            return result

        card = self.generate_card_use_case.execute(area_id, analysis)
        result["cardStatus"] = "CARD_ABERTO" if card.status == "ABERTO" else card.status
        result["cardId"] = card.card_id
        return result

    def execute_all(self) -> list[dict[str, Any]]:
        """Fechamento: analisa todas as areas ativas."""
        return [self.execute(area.id) for area in self.area_repository.list_all() if area.is_active]
