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

            session = container.session
            if session is None:
                raise HTTPException(503, "Transacao autenticada indisponivel.")
            session.execute(
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
            _registrar_decisao_como_memoria(container, card_id, payload)
        return result
    except CardStateError as e:
        raise HTTPException(status_code=409, detail=str(e)) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))


_DECISAO_MEMORIA = {
    "APROVAR_PGR": "APROVADA",
    "AJUSTAR_ACAO": "AJUSTADA",
    "DESCARTAR": "DESCARTADA",
}


def _registrar_decisao_como_memoria(
    container: PulsoAppContainer, card_id: str, payload: ResolveRiskCardRequestDTO
) -> None:
    """A decisao do RH vira documento citavel (PLANO_ACAO_ANTERIOR) para os proximos ciclos.

    Roda num savepoint: se a memoria falhar (ex.: texto com dado pessoal bloqueado na triagem),
    a decisao e a auditoria continuam valendo. Nao inclui o nome do responsavel.
    """
    import logging
    from datetime import date

    assistente = getattr(container.knowledge, "assistente", None)
    card = container.risk_card_repo.get_by_id(card_id)
    if assistente is None or card is None or container.session is None:
        return
    fator = getattr(card.probable_risk_factor, "value", card.probable_risk_factor)
    if fator == "ASSEDIO":
        return
    try:
        with container.session.begin_nested():
            assistente.registrar_decisao(
                container.context,
                area_nome=card.area_name,
                fator=str(fator),
                periodo=f"{date.today():%m/%Y}",
                decisao=_DECISAO_MEMORIA[payload.action_type],
                acao=payload.adjusted_action_text or card.suggested_action,
                justificativa=payload.justification_notes,
            )
    except Exception:  # noqa: BLE001 - memoria e acessoria; nunca derruba a decisao do RH
        logging.getLogger(__name__).warning("Decisao %s nao virou memoria.", card_id, exc_info=True)
