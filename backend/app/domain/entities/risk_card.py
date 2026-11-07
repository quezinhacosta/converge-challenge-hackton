"""Entidade de dominio representando o Ponto Focal de Atencao (Card de Risco) emitido ao RH."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel


class CardStatus(StrEnum):
    """Estado de tramitacao e decisao humana sobre o ponto focal."""

    ABERTO = "ABERTO"  # Gerado pelo Pulso, aguardando analise do RH
    APROVADO_PGR = "APROVADO_PGR"  # RH aprovou e enviou para o inventario do PGR
    AJUSTADO = "AJUSTADO"  # RH ajustou a hipotese ou acao antes de registrar
    DESCARTADO = "DESCARTADO"  # RH descartou o apontamento com justificativa
    ESCALADO_COMPLIANCE = "ESCALADO"  # Casos sensiveis (ex.: assedio) escalados imediatamente


@dataclass
class RiskCard:
    """Representa o Card do Ponto Focal de Atencao gerado pelo agente Pulso para o RH.

    Principio Human-in-the-Loop:
        - O agente escreve o card com evidencias, contexto e hipotese em linguagem simples.
        - O agente para na etapa 7: nada e registrado no PGR sem aprovacao previa do RH.

    Atributos:
        id: Identificador unico do card.
        area_id: Identificador da area em atencao.
        area_name: Nome do setor para apresentacao.
        area_headcount: Total de colaboradores no setor.
        risk_level: Nivel de atencao (VERDE, AMARELO, VERMELHO).
        probable_risk_factor: Fator de risco psicossocial mais provavel sob a NR-1.
        evidence_summary: Resumo em linguagem clara do que mudou no setor nos ultimos 3 a 6 meses.
        context_description: Correlacao temporal com eventos organizacionais (ex.: nova meta, troca de gestor).
        suggested_action: Proposta inicial de acao corretiva/preventiva formulada pelo agente.
        status: Estado atual da revisao pelo RH.
        consulted_sources: Lista de fontes de dados consultadas (ex.: ponto, folha, desligamentos, pesquisa pulso).
        created_at: Data e hora em que o card foi emitido.
        resolved_at: Data e hora em que o RH tomou a decisao.
        reviewer_name: Nome da pessoa do RH que analisou o card.
        resolution_notes: Justificativa registrada caso a acao tenha sido ajustada ou descartada.
        risk_score: Score matematico continuo (0.0 a 100.0) gerado pelo modelo tabular XGBoost.
        shap_breakdown: Decomposicao legalmente auditavel das contribuicoes percentuais de cada variavel (SHAP).
        ai_provider_used: Nome do provedor de IA que gerou a hipotese (primario ou substituto).
        ai_fallback_triggered: Booleano indicando se a IA primária falhou e acionou o plano de contingencia.
    """

    id: str
    area_id: str
    area_name: str
    area_headcount: int
    risk_level: RiskLevel
    probable_risk_factor: PsychosocialRiskFactor
    evidence_summary: str
    context_description: str
    suggested_action: str
    status: CardStatus = CardStatus.ABERTO
    consulted_sources: list[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    resolved_at: datetime | None = None
    reviewer_name: str | None = None
    resolution_notes: str | None = None
    risk_score: float = 0.0
    shap_breakdown: list[dict[str, Any]] = field(default_factory=list)
    ai_provider_used: str = "xgboost+gemini-1.5-pro"
    ai_fallback_triggered: bool = False

    fontes_documentais: list[dict[str, Any]] = field(default_factory=list)
    evidencia_documental_suficiente: bool | None = None
