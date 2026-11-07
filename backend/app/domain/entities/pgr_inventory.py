"""Entidades de dominio para o Inventario de Riscos e Plano de Acao do PGR (NR-1)."""

from dataclasses import dataclass, field
from datetime import UTC, date, datetime

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel


@dataclass
class PgrRiskItem:
    """Registro formal no Inventario de Riscos do PGR (Programa de Gerenciamento de Riscos).

    Exigencia Legal (NR-1 / GRO):
        - Documento exigivel pela fiscalizacao do MTE a partir de 26/05/2026.
        - Registra os perigos psicossociais identificados, niveis, medidas preventivas,
          responsaveis, prazos e ciclo de reavaliacao.

    Atributos:
        id: Identificador unico do item de risco no PGR.
        risk_card_id: Identificador do card de atencao que originou este registro.
        area_id: Identificador da area envolvida.
        area_name: Nome do setor.
        factor: Fator de risco psicossocial enquadrado.
        severity_level: Nivel de risco atribuido (VERDE, AMARELO, VERMELHO).
        action_plan_description: Acao formalizada pelo RH para mitigacao ou controle do risco.
        responsible_person: Pessoa responsavel pela execucao do plano de acao no RH/lideranca.
        deadline_date: Prazo maximo acordado para conclusao da acao.
        reassessment_interval_days: Intervalo para medicao de eficacia (ex.: 60 dias).
        registered_at: Data de inclusao no inventario do PGR.
        is_reopened: Indicador se o caso foi reaberto por ausencia de melhora nos indicadores.
        closure_date: Data de encerramento do ciclo caso os indicadores tenham melhorado.
        closure_notes: Parecer final de eficacia das medidas adotadas.
        audit_log: Rastro de auditoria contendo decisoes, alteracoes e fontes consultadas.
    """

    id: str
    risk_card_id: str
    area_id: str
    area_name: str
    factor: PsychosocialRiskFactor
    severity_level: RiskLevel
    action_plan_description: str
    responsible_person: str
    deadline_date: date
    reassessment_interval_days: int = 60
    registered_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    is_reopened: bool = False
    closure_date: date | None = None
    closure_notes: str | None = None
    audit_log: list[str] = field(default_factory=list)
