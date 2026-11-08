"""DTOs para manipulacao dos cards de atencao do RH e aprovacao de acoes."""

from datetime import datetime
from typing import Any, Literal

from app.application.dtos.compat import ApiModel, Field, model_validator

MIN_DEADLINE_DAYS = 15


class RiskCardDTO(ApiModel):
    """Representacao de um ponto focal emitido pelo Pulso para decisao do RH.

    Atributos:
        card_id: Identificador unico do card.
        area_id: Identificador da area.
        area_name: Nome do setor (ex.: Atendimento ao Cliente).
        area_headcount: Total de colaboradores no setor.
        risk_level: Nivel de atencao (VERDE, AMARELO, VERMELHO).
        fator_risco_provavel: Fator de risco psicossocial da NR-1 associado.
        o_que_mudou_ultimos_meses: Evidencias quantitativas comparadas.
        contexto_organizacional: Correlacao com metas, mudanca de gestor, etc.
        acao_sugerida: Recomendacao elaborada pelo agente.
        fontes_consultadas: Origem dos dados utilizados.
        status: Estado de tramitacao (ABERTO, APROVADO_PGR, AJUSTADO, DESCARTADO).
        created_at: Data e hora de emissao.
        risk_score: Pontuacao quantitativa continua (0 a 100) do XGBoost.
        shap_breakdown: Decomposicao percentual legalmente auditavel (SHAP) por variavel.
        ai_provider_used: Provedor de IA que gerou a correlacao.
        ai_fallback_triggered: Booleano indicando se houve chaveamento para fallback.
    """

    card_id: str
    area_id: str
    area_name: str
    area_headcount: int
    risk_level: str
    fator_risco_provavel: str
    o_que_mudou_ultimos_meses: str
    contexto_organizacional: str
    acao_sugerida: str
    fontes_consultadas: list[str]
    status: str
    created_at: datetime
    risk_score: float = 0.0
    shap_breakdown: list[dict[str, Any]] = Field(default_factory=list)
    ai_provider_used: str = "xgboost+gemini-1.5-pro"
    ai_fallback_triggered: bool = False


class ResolveRiskCardRequestDTO(ApiModel):
    """Payload de decisao humana (1-clique) do analista de RH sobre o card de risco.

    Atributos:
        action_type: Decisao tomada: 'APROVAR_PGR', 'AJUSTAR_ACAO', 'DESCARTAR'.
        reviewer_name: Nome do profissional do RH responsavel pela decisao.
        adjusted_action_text: Descricao ajustada da acao (obrigatorio se action_type == 'AJUSTAR_ACAO').
        responsible_person: Pessoa designada para liderar a acao no plano do PGR.
        deadline_days: Prazo em dias para conclusao/reavaliacao (ex.: 60 dias).
        justification_notes: Justificativa registrada em caso de descarte.
    """

    action_type: Literal["APROVAR_PGR", "AJUSTAR_ACAO", "DESCARTAR"]
    reviewer_name: str = Field(..., min_length=2)
    adjusted_action_text: str | None = None
    responsible_person: str | None = None
    deadline_days: int = Field(default=60, ge=0, le=180)
    justification_notes: str | None = None

    @model_validator(mode="after")
    def _check_decision_requirements(self) -> "ResolveRiskCardRequestDTO":
        """Ajuste exige o texto novo; descarte exige justificativa; aprovacao exige prazo."""
        if self.action_type not in ("APROVAR_PGR", "AJUSTAR_ACAO", "DESCARTAR"):
            raise ValueError(
                f"action_type '{self.action_type}' invalido. Esperado APROVAR_PGR, AJUSTAR_ACAO ou DESCARTAR."
            )
        if self.action_type == "AJUSTAR_ACAO" and not (self.adjusted_action_text or "").strip():
            raise ValueError("AJUSTAR_ACAO exige adjusted_action_text com a acao ajustada.")
        if self.action_type == "DESCARTAR" and len((self.justification_notes or "").strip()) < 5:
            raise ValueError("DESCARTAR exige justification_notes (minimo de 5 caracteres).")
        if self.action_type != "DESCARTAR" and self.deadline_days < MIN_DEADLINE_DAYS:
            raise ValueError(f"deadline_days deve ser de pelo menos {MIN_DEADLINE_DAYS} dias.")
        return self
