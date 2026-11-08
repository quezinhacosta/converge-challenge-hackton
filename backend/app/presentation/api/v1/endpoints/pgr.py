"""Endpoints do Inventario de Riscos e Plano de Acao do PGR (NR-1)."""

from app.application.dtos.pgr_dto import PgrInventoryItemDTO, ReassessmentEvaluationDTO
from app.presentation.compat import APIRouter, Depends, HTTPException, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("/inventory", response_model=list[PgrInventoryItemDTO], status_code=status.HTTP_200_OK)
def get_pgr_inventory(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> list[PgrInventoryItemDTO]:
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
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> ReassessmentEvaluationDTO:
    """Simula a reavaliacao formal de 60 dias da acao mitigadora do PGR (Caso 7)."""
    if container.context is not None:
        raise HTTPException(
            status_code=501,
            detail="Reavaliacao real ainda indisponivel; nao executar simulacao em producao.",
        )
    try:
        return container.track_evolution_uc.execute(pgr_item_id)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
    "/{pgr_item_id}/reassess",
    response_model=ReassessmentEvaluationDTO,
    status_code=status.HTTP_200_OK,
)
@router.get(
    "/{pgr_item_id}/reassess",
    response_model=ReassessmentEvaluationDTO,
    status_code=status.HTTP_200_OK,
)
def reassess_pgr_item_action(
    pgr_item_id: str,
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> ReassessmentEvaluationDTO:
    """Rota usada pelo frontend; mesma protecao da rota /reassessment (sem simulacao em producao)."""
    return evaluate_risk_reassessment(pgr_item_id, container)
