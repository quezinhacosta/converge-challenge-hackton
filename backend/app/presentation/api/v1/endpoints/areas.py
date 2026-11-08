"""Endpoints de consulta de areas e sinais operacionais agregados."""

from typing import Any

from app.application.dtos.signal_dto import AreaHistoryComparisonDTO
from app.presentation.compat import APIRouter, Depends, HTTPException, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("", response_model=list[dict[str, Any]], status_code=status.HTTP_200_OK)
def list_company_areas(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> list[dict[str, Any]]:
    """Lista todas as areas da empresa informando headcount e status de anonimizacao."""
    areas = container.area_repo.list_all()
    return [
        {
            "id": a.id,
            "name": a.name,
            "headcount": a.headcount,
            "managerName": a.manager_name,
            "isAnonymized": not a.is_eligible_for_analytics,
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
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> AreaHistoryComparisonDTO:
    """Recupera a serie historica de metricas agregadas e eventos de contexto da area."""
    try:
        return container.collect_signals_uc.execute(area_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/{area_id}/analyze", response_model=dict[str, Any], status_code=status.HTTP_200_OK)
def analyze_area(
    area_id: str,
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> dict[str, Any]:
    """Roda o ciclo do Pulso na area e abre card se o nivel for amarelo ou vermelho."""
    try:
        return container.run_analysis_uc.execute(area_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
