"""DTOs para manipulacao dos cards de atencao do RH e aprovacao de acoes."""

from datetime import datetime
from typing import Any

from app.application.dtos.compat import BaseModel, Field


class RiskCardDTO(BaseModel):
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


class ResolveRiskCardRequestDTO(BaseModel):
    """Payload de decisao humana (1-clique) do analista de RH sobre o card de risco.

    Atributos:
        action_type: Decisao tomada: 'APROVAR_PGR', 'AJUSTAR_ACAO', 'DESCARTAR'.
        reviewer_name: Nome do profissional do RH responsavel pela decisao.
        adjusted_action_text: Descricao ajustada da acao (obrigatorio se action_type == 'AJUSTAR_ACAO').
        responsible_person: Pessoa designada para liderar a acao no plano do PGR.
        deadline_days: Prazo em dias para conclusao/reavaliacao (ex.: 60 dias).
        justification_notes: Justificativa registrada em caso de descarte.
    """

    action_type: str = Field(..., description="APROVAR_PGR | AJUSTAR_ACAO | DESCARTAR")
    reviewer_name: str
    adjusted_action_text: str | None = None
    responsible_person: str | None = None
    deadline_days: int = Field(default=60, ge=15, le=180)
    justification_notes: str | None = None
