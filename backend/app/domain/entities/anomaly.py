"""Entidade de dominio representando anomalias preditivas e riscos de fraude na folha."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class RiskSeverity(str, Enum):
    """Classificacao do nivel de severidade do risco financeiro e operacional."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AnomalyCategory(str, Enum):
    """Categoria de inconsistencia identificada na folha de pagamento pelo motor de ML."""

    OVERTIME_SPIKE = "OVERTIME_SPIKE"
    GHOST_EMPLOYEE = "GHOST_EMPLOYEE"
    DUPLICATE_PAYMENT = "DUPLICATE_PAYMENT"
    SUBSTITUTION_MISMATCH = "SUBSTITUTION_MISMATCH"
    VACATION_OVERLAP = "VACATION_OVERLAP"
    SUSPICIOUS_ADDITIONAL = "SUSPICIOUS_ADDITIONAL"


@dataclass
class Anomaly:
    """Representa um apontamento de risco gerado pelo motor de Machine Learning do PayTrust.

    Atributos:
        id: Identificador unico do achado de auditoria.
        paystub_id: Identificador do holerite sob analise.
        employee_id: Identificador do colaborador envolvido.
        category: Categoria classificada da inconsistencia.
        severity: Classificacao do nivel de risco (LOW, MEDIUM, HIGH, CRITICAL).
        paytrust_score: Score de risco preditivo entre 0 e 100, onde 100 indica maxima suspeita.
        explanation: Justificativa em linguagem natural gerada pelo agente de compliance para o DP.
        suggested_action: Acao preventiva recomendada (ex.: Reter pagamento, Auditar espelho de ponto).
        is_resolved: Indica se a anomalia ja foi analisada e decidida por um analista humano.
        resolution_notes: Justificativa registrada pelo analista do DP ao aprovar ou rejeitar.
    """

    id: str
    paystub_id: str
    employee_id: str
    category: AnomalyCategory
    severity: RiskSeverity
    paytrust_score: float
    explanation: str
    suggested_action: str
    is_resolved: bool = False
    resolution_notes: Optional[str] = None
