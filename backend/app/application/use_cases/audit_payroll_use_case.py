"""Use case for auditing a payroll batch, computing ML anomaly scores, and generating alerts."""

from typing import Protocol
import pandas as pd

from app.application.dtos.payroll_dto import (
    PayrollBatchAuditRequestDTO,
    PayrollBatchAuditResponseDTO,
)
from app.domain.repositories.interfaces import AnomalyRepository, PayrollRepository


class AnomalyDetectorService(Protocol):
    """Protocol for the Machine Learning anomaly inference service."""

    def predict_scores(self, features_df: pd.DataFrame) -> list[float]:
        """Compute the continuous PayTrust anomaly score (0 to 100) for payroll items."""
        ...


class ComplianceAgentService(Protocol):
    """Protocol for the generative LLM compliance explanation service."""

    def explain_anomaly(
        self, employee_id: str, score: float, metrics: dict
    ) -> str:
        """Generate a natural language explanation for an identified payroll deviation."""
        ...


class AuditPayrollUseCase:
    """Coordinates batch payroll audit using Layer 1 (ML) and Layer 2 (LLM Compliance).

    Workflow:
        1. Ingest batch payroll records submitted from ERP/DP.
        2. Extract ML feature vector: [salario_base, he_mes, he_media_3m, desvio_setor].
        3. Execute Isolation Forest inference to calculate PayTrust Score (0-100).
        4. Filter items exceeding the anomaly threshold (e.g., Score >= 80).
        5. Invoke Compliance Agent (LLM) to craft contextual Brazilian labor law explanations.
        6. Persist detected anomalies for 1-click Human-in-the-Loop review.
        7. Return consolidated audit report to DP dashboard.
    """

    def __init__(
        self,
        anomaly_detector: AnomalyDetectorService,
        compliance_agent: ComplianceAgentService,
        payroll_repository: PayrollRepository,
        anomaly_repository: AnomalyRepository,
    ) -> None:
        """Initialize the use case with required infrastructure adapters and repositories.

        Args:
            anomaly_detector: Service handling Isolation Forest anomaly inference.
            compliance_agent: LLM service explaining labor law violations and deviations.
            payroll_repository: Persistence layer for audited paystub batches.
            anomaly_repository: Persistence layer for flagged anomalies.
        """
        self.anomaly_detector = anomaly_detector
        self.compliance_agent = compliance_agent
        self.payroll_repository = payroll_repository
        self.anomaly_repository = anomaly_repository

    def execute(self, request: PayrollBatchAuditRequestDTO) -> PayrollBatchAuditResponseDTO:
        """Execute the payroll batch audit pipeline.

        Args:
            request: The batch payroll payload containing records to evaluate.

        Returns:
            PayrollBatchAuditResponseDTO: Consolidated audit findings and anomaly list.

        Raises:
            ValueError: If the batch payload is empty or malformed.
        """
        raise NotImplementedError("AuditPayrollUseCase.execute is a structural interface stub.")
