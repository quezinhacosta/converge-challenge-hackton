"""Endpoints de consulta de areas e sinais operacionais agregados."""

from typing import Any, Dict, List
from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.signal_dto import AreaHistoryComparisonDTO
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("", response_model=List[Dict[str, Any]], status_code=status.HTTP_200_OK)
def list_company_areas(
    container: PulsoAppContainer = Depends(get_container),
) -> List[Dict[str, Any]]:
    """Lista todas as areas da empresa informando headcount e status de anonimizacao."""
    areas = container.area_repo.list_all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "headcount": a.headcount,
            "manager_name": a.manager_name,
            "is_anonymized": not a.is_eligible_for_analytics,
            "description": a.description,
        }
        for a in areas
    ]


@router.get(
    "/{area_id}/signals",
    response_model=AreaHistoryComparisonDTO,
    status_code=status.HTTP_200_OK,
)
def get_area_signals_and_context(
    area_id: str,
    container: PulsoAppContainer = Depends(get_container),
) -> AreaHistoryComparisonDTO:
    """Recupera a serie historica de metricas agregadas e eventos de contexto da area."""
    try:
        return container.collect_signals_uc.execute(area_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
