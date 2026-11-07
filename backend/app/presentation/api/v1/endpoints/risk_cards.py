"""Endpoints de gestao dos cards de atencao e ponto focal do RH."""

from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO, RiskCardDTO
from app.application.use_cases.register_pgr_action_use_case import CardStateError
from app.presentation.compat import APIRouter, Depends, HTTPException, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("/active", response_model=list[RiskCardDTO], status_code=status.HTTP_200_OK)
def get_active_risk_cards(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> list[RiskCardDTO]:
    """Retorna os cards de risco ativos que demandam deliberacao humana do RH."""
    cards = container.risk_card_repo.list_active()
    return [RiskCardDTO.from_entity(c) for c in cards]


@router.post(
    "/{card_id}/resolve",
    response_model=PgrInventoryItemDTO,
    status_code=status.HTTP_200_OK,
)
def resolve_risk_card_and_register_pgr(
    card_id: str,
    payload: ResolveRiskCardRequestDTO,
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> PgrInventoryItemDTO:
    """Registra a deliberacao humana (aprovar/ajustar) e gera o item no PGR (NR-1)."""
    try:
        if container.context is not None:
            payload = payload.model_copy(
                update={"reviewer_name": str(container.context.usuario_id)}
            )
        result = container.register_pgr_uc.execute(card_id, payload)
        if container.context is not None:
            from uuid import uuid4

            from sqlalchemy import text

            container.session.execute(
                text(
                    "INSERT INTO auditoria(id,empresa_id,usuario_id,recurso_id,acao) "
                    "VALUES(:id,:empresa,:usuario,:recurso,:acao)"
                ),
                {
                    "id": uuid4(),
                    "empresa": container.context.empresa_id,
                    "usuario": container.context.usuario_id,
                    "recurso": card_id,
                    "acao": payload.action_type,
                },
            )
        return result
    except CardStateError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
