"""Caso de uso para redigir o Ponto Focal de Atencao e escalar para o RH (Etapas 6 e 7 do Pulso)."""

from datetime import datetime, timezone
from typing import Any, Dict, Protocol
from app.application.dtos.risk_card_dto import RiskCardDTO
from app.domain.entities.risk_card import CardStatus, RiskCard
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.domain.repositories.interfaces import AreaRepository, RiskCardRepository


class CardContentGenerator(Protocol):
    """Protocolo da LLM encarregada de redigir o card em linguagem clara e direta."""

    def draft_focus_card(
        self,
        area_name: str,
        headcount: int,
        metrics_summary: str,
        context_summary: str,
        factor: str,
    ) -> tuple[str, str]:
        """Escreve a hipotese explicativa e a proposta de acao sugerida ao RH."""
        ...


class GenerateRiskCardUseCase:
    """Executa as Etapas 6 e 7 do Ciclo do Pulso:

    Etapa 6 - Gerar o Ponto Focal:
        Escreve o card de atencao em linguagem simples, compilando evidencias quantitativas,
        contexto organizacional, explicabilidade SHAP, hipotese de fator de risco e proposta de acao.
    Etapa 7 - Escalar e Parar:
        Envia o card ao painel do RH responsavel e interrompe a automacao.
        Nada e registrado como decisao formal sem aprovacao previa humana.
    """

    def __init__(
        self,
        area_repository: AreaRepository,
        risk_card_repository: RiskCardRepository,
        content_generator: CardContentGenerator,
    ) -> None:
        """Inicializa o caso de uso."""
        self.area_repository = area_repository
        self.risk_card_repository = risk_card_repository
        self.content_generator = content_generator

    def execute(self, area_id: str, analysis_result: Dict[str, Any]) -> RiskCardDTO:
        """Gera o ponto focal e disponibiliza para apreciacao do RH.

        Argumentos:
            area_id: Identificador da area.
            analysis_result: Resultado das etapas de comparacao e classificacao com XGBoost/SHAP.

        Retorna:
            RiskCardDTO: Card estruturado aguardando deliberacao humana.
        """
        area = self.area_repository.get_by_id(area_id)
        if not area:
            raise ValueError(f"Area '{area_id}' nao encontrada.")

        risk_level = analysis_result["risk_level"]
        if isinstance(risk_level, str):
            risk_level = RiskLevel(risk_level)

        factor = analysis_result["factor"]
        if isinstance(factor, str):
            factor = PsychosocialRiskFactor(factor)

        context_events = analysis_result.get("context_events", [])
        context_desc = (
            context_events[0]["desc"]
            if context_events
            else "Sem eventos de contexto recentes registrados."
        )

        evidence = analysis_result.get("evidence_summary", "")
        action = analysis_result.get("suggested_action", "")

        status = CardStatus.ABERTO
        if factor == PsychosocialRiskFactor.ASSEDIO:
            status = CardStatus.ESCALADO_COMPLIANCE

        sources = [
            "ponto",
            "folha",
            "desligamentos",
            "pesquisa pulso",
            "eventos_contexto",
            "xgboost_shap",
        ]

        risk_score = float(analysis_result.get("risk_score", 0.0))
        shap_breakdown = analysis_result.get("shap_breakdown", [])
        ai_meta = analysis_result.get("ai_execution_metadata", {})
        provider_used = ai_meta.get("provider_used", "xgboost+gemini-1.5-pro")
        fallback_triggered = bool(ai_meta.get("fallback_triggered", False))

        card = RiskCard(
            id=f"card_{area.id}_{int(datetime.now().timestamp())}",
            area_id=area.id,
            area_name=area.name,
            area_headcount=area.headcount,
            risk_level=risk_level,
            probable_risk_factor=factor,
            evidence_summary=evidence,
            context_description=context_desc,
            suggested_action=action,
            status=status,
            consulted_sources=sources,
            created_at=datetime.now(timezone.utc),
            risk_score=risk_score,
            shap_breakdown=shap_breakdown,
            ai_provider_used=provider_used,
            ai_fallback_triggered=fallback_triggered,
        )

        self.risk_card_repository.save(card)

        return RiskCardDTO(
            card_id=card.id,
            area_id=card.area_id,
            area_name=card.area_name,
            area_headcount=card.area_headcount,
            risk_level=card.risk_level.value,
            fator_risco_provavel=card.probable_risk_factor.value,
            o_que_mudou_ultimos_meses=card.evidence_summary,
            contexto_organizacional=card.context_description,
            acao_sugerida=card.suggested_action,
            fontes_consultadas=card.consulted_sources,
            status=card.status.value,
            created_at=card.created_at,
            risk_score=card.risk_score,
            shap_breakdown=card.shap_breakdown,
            ai_provider_used=card.ai_provider_used,
            ai_fallback_triggered=card.ai_fallback_triggered,
        )
