"""Endpoints do Inventario de Riscos e Plano de Acao do PGR (NR-1)."""

from typing import List
from app.presentation.compat import APIRouter, Depends, HTTPException, status

from app.application.dtos.pgr_dto import PgrInventoryItemDTO, ReassessmentEvaluationDTO
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("/inventory", response_model=List[PgrInventoryItemDTO], status_code=status.HTTP_200_OK)
def get_pgr_inventory(
    container: PulsoAppContainer = Depends(get_container),
) -> List[PgrInventoryItemDTO]:
    """Retorna a lista completa de riscos psicossociais ativos registrados no PGR."""
    items = container.pgr_repo.list_all()
    return [
        PgrInventoryItemDTO(
            item_id=item.id,
            area_id=item.area_id,
            area_name=item.area_name,
            fator_psicossocial=item.factor.value,
            nivel_severidade=item.severity_level.value,
            descricao_plano_acao=item.action_plan_description,
            responsavel=item.responsible_person,
            prazo_limite=item.deadline_date,
            intervalo_reavaliacao_dias=item.reassessment_interval_days,
            data_registro=item.registered_at,
            is_reaberto=item.is_reopened,
            data_encerramento=item.closure_date,
            parecer_encerramento=item.closure_notes,
            rastro_auditoria=item.audit_log,
        )
        for item in items
    ]


@router.get(
    "/reassessment/{pgr_item_id}",
    response_model=ReassessmentEvaluationDTO,
    status_code=status.HTTP_200_OK,
)
def evaluate_risk_reassessment(
    pgr_item_id: str,
    container: PulsoAppContainer = Depends(get_container),
) -> ReassessmentEvaluationDTO:
    """Simula a reavaliacao formal de 60 dias da acao mitigadora do PGR (Caso 7)."""
    try:
        return container.track_evolution_uc.execute(pgr_item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
