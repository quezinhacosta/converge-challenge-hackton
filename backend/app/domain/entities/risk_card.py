"""Entidade de dominio representando o Ponto Focal de Atencao (Card de Risco) emitido ao RH."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel


class CardStatus(str, Enum):
    """Estado de tramitacao e decisao humana sobre o ponto focal."""

    ABERTO = "ABERTO"                      # Gerado pelo Pulso, aguardando analise do RH
    APROVADO_PGR = "APROVADO_PGR"          # RH aprovou e enviou para o inventario do PGR
    AJUSTADO = "AJUSTADO"                  # RH ajustou a hipotese ou acao antes de registrar
    DESCARTADO = "DESCARTADO"              # RH descartou o apontamento com justificativa
    ESCALADO_COMPLIANCE = "ESCALADO"       # Casos sensiveis (ex.: assedio) escalados imediatamente


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
        consulted_sources: Lista de fontes de dados consultadas (ex.: ponto, folha, desligamentos, pesquisa pulso).
        status: Estado atual da revisao pelo RH.
        created_at: Data e hora em que o card foi emitido.
        resolved_at: Data e hora em que o RH tomou a decisao.
        reviewer_name: Nome da pessoa do RH que analisou o card.
        resolution_notes: Justificativa registrada caso a acao tenha sido ajustada ou descartada.
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
    consulted_sources: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    reviewer_name: Optional[str] = None
    resolution_notes: Optional[str] = None
