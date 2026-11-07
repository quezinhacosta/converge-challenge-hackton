"""Endpoints para auditoria de lotes de folha de pagamento e deteccao de anomalias."""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.application.dtos.payroll_dto import (
    AnomalyReportDTO,
    PayrollBatchAuditRequestDTO,
    PayrollBatchAuditResponseDTO,
)

router = APIRouter()


@router.post(
    "/audit-batch",
    response_model=PayrollBatchAuditResponseDTO,
    status_code=status.HTTP_200_OK,
)
def audit_payroll_batch(
    payload: PayrollBatchAuditRequestDTO,
) -> PayrollBatchAuditResponseDTO:
    """Ingere e audita um lote da folha de pagamento via modelo de Machine Learning.

    Parametros:
        payload: PayrollBatchAuditRequestDTO contendo os lancamentos e metricas dos colaboradores.

    Retorna:
        PayrollBatchAuditResponseDTO: Relatorio consolidado de auditoria e valores retidos.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando implementacao do caso de uso.",
    )


@router.get(
    "/anomalies/pending",
    response_model=List[AnomalyReportDTO],
    status_code=status.HTTP_200_OK,
)
def get_pending_anomalies() -> List[AnomalyReportDTO]:
    """Retorna todas as inconsistencias da folha aguardando revisao humana em 1 clique pelo DP.

    Retorna:
        List[AnomalyReportDTO]: Apontamentos de risco pendentes com PayTrust Score elevado.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando implementacao do caso de uso.",
    )
