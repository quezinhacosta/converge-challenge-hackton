"""Data transfer objects for payroll ingestion, auditing, and anomaly reporting."""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class PayrollEntryDTO(BaseModel):
    """Input DTO representing a single employee payroll record in a batch submission.

    Attributes:
        employee_id: Identifier of the employee.
        competence_period: Payroll month/year in YYYY-MM-DD format.
        salario_base: Monthly baseline salary in BRL.
        he_mes: Total overtime hours registered in current month.
        he_media_3m: Average overtime hours registered in preceding 3 months.
        desvio_setor: Overtime hours deviation relative to department average.
    """

    employee_id: str
    competence_period: date
    salario_base: float = Field(..., gt=0, description="Base monthly compensation")
    he_mes: float = Field(..., ge=0, description="Current month overtime hours")
    he_media_3m: float = Field(..., ge=0, description="Three-month moving average of overtime hours")
    desvio_setor: float = Field(..., description="Departmental overtime deviation")


class PayrollBatchAuditRequestDTO(BaseModel):
    """Batch payload submitted by DP/ERP for pre-payment audit.

    Attributes:
        batch_id: Unique batch identification code.
        entries: Collection of employee payroll entries to evaluate.
    """

    batch_id: str
    entries: List[PayrollEntryDTO]


class AnomalyReportDTO(BaseModel):
    """DTO representing a flagged anomaly detected during batch evaluation.

    Attributes:
        anomaly_id: Unique ID of the finding.
        employee_id: Associated employee.
        paytrust_score: Calculated risk score (0 to 100).
        risk_severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL).
        explanation: LLM-generated explanation detailing why the entry was flagged.
        action_recommended: Human-in-the-loop action proposed to the DP.
    """

    anomaly_id: str
    employee_id: str
    paytrust_score: float
    risk_severity: str
    explanation: str
    action_recommended: str


class PayrollBatchAuditResponseDTO(BaseModel):
    """Summary result returned after auditing a payroll batch.

    Attributes:
        batch_id: Processed batch identifier.
        total_records_analyzed: Count of evaluated payroll entries.
        total_anomalies_detected: Count of suspicious items requiring intervention.
        total_blocked_amount_brl: Estimated monetary value held pending validation.
        anomalies: Detailed list of detected anomalies.
    """

    batch_id: str
    total_records_analyzed: int
    total_anomalies_detected: int
    total_blocked_amount_brl: float
    anomalies: List[AnomalyReportDTO]
