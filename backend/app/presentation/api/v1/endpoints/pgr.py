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
    """Retorna o inventario oficial de riscos psicossociais e planos de acao do PGR."""
    items = container.pgr_repo.list_all()
    return [
        PgrInventoryItemDTO(
            item_id=i.id,
            area_id=i.area_id,
            area_name=i.area_name,
            fator_psicossocial=i.factor.value,
            nivel_severidade=i.severity_level.value,
            descricao_plano_acao=i.action_plan_description,
            responsavel=i.responsible_person,
            prazo_limite=i.deadline_date,
            intervalo_reavaliacao_dias=i.reassessment_interval_days,
            data_registro=i.registered_at,
            is_reaberto=i.is_reopened,
            data_encerramento=i.closure_date,
            parecer_encerramento=i.closure_notes,
            rastro_auditoria=i.audit_log,
        )
        for i in items
    ]


@router.post(
    "/{item_id}/reassess",
    response_model=ReassessmentEvaluationDTO,
    status_code=status.HTTP_200_OK,
)
def reassess_pgr_item(
    item_id: str,
    container: PulsoAppContainer = Depends(get_container),
) -> ReassessmentEvaluationDTO:
    """Mede a eficacia da intervencao apos 60 dias e encerra o ciclo ou reabre o card."""
    try:
        return container.track_evolution_uc.execute(item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
