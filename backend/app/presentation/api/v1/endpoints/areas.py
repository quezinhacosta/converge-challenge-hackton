"""Endpoints de consulta de areas e sinais operacionais agregados."""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.application.dtos.signal_dto import AreaHistoryComparisonDTO

router = APIRouter()


@router.get("", response_model=List[dict], status_code=status.HTTP_200_OK)
def list_company_areas() -> List[dict]:
    """Lista todas as areas da empresa informando headcount e status de anonimizacao."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )


@router.get("/{area_id}/signals", response_model=AreaHistoryComparisonDTO, status_code=status.HTTP_200_OK)
def get_area_signals_and_context(area_id: str) -> AreaHistoryComparisonDTO:
    """Recupera a serie historica de metricas agregadas e eventos de contexto da area."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )
