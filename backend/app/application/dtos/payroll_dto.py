"""Objetos de transferencia de dados para ingestao de folha, auditoria e reporte de anomalias."""

from datetime import date
from typing import List
from pydantic import BaseModel, Field


class PayrollEntryDTO(BaseModel):
    """Representa o lancamento de um colaborador em um lote submetido para auditoria.

    Atributos:
        employee_id: Identificador do colaborador.
        competence_period: Competencia da folha no formato YYYY-MM-DD.
        salario_base: Salario base mensal contratual em Reais (BRL).
        he_mes: Total de horas extras apuradas no mes corrente.
        he_media_3m: Media de horas extras realizadas nos ultimos 3 meses.
        desvio_setor: Desvio das horas extras em relacao a media dos pares do setor.
    """

    employee_id: str
    competence_period: date
    salario_base: float = Field(..., gt=0, description="Salario base mensal")
    he_mes: float = Field(..., ge=0, description="Horas extras no mes")
    he_media_3m: float = Field(..., ge=0, description="Media de horas extras ultimos 3 meses")
    desvio_setor: float = Field(..., description="Desvio em relacao ao setor")


class PayrollBatchAuditRequestDTO(BaseModel):
    """Payload de lote de folha submetido pelo DP ou ERP para auditoria preventiva.

    Atributos:
        batch_id: Codigo identificador unico do lote.
        entries: Colecao de lancamentos de colaboradores para avaliacao.
    """

    batch_id: str
    entries: List[PayrollEntryDTO]


class AnomalyReportDTO(BaseModel):
    """DTO representando um apontamento de anomalia identificado no lote da folha.

    Atributos:
        anomaly_id: Identificador unico da anomalia.
        employee_id: Colaborador envolvido.
        paytrust_score: Score de risco preditivo calculado (0 a 100).
        risk_severity: Nivel de severidade do risco (LOW, MEDIUM, HIGH, CRITICAL).
        explanation: Explicacao gerada pela IA contextualizando as regras trabalhistas violadas.
        action_recommended: Acao preventiva recomendada para o analista do DP.
    """

    anomaly_id: str
    employee_id: str
    paytrust_score: float
    risk_severity: str
    explanation: str
    action_recommended: str


class PayrollBatchAuditResponseDTO(BaseModel):
    """Resultado consolidado retornado apos a auditoria preditiva do lote de folha.

    Atributos:
        batch_id: Identificador do lote processado.
        total_records_analyzed: Quantidade total de registros avaliados.
        total_anomalies_detected: Quantidade de itens suspeitos que demandam revisao.
        total_blocked_amount_brl: Montante financeiro total retido preventivamente em Reais.
        anomalies: Lista detalhada de anomalias encontradas.
    """

    batch_id: str
    total_records_analyzed: int
    total_anomalies_detected: int
    total_blocked_amount_brl: float
    anomalies: List[AnomalyReportDTO]
