"""Endpoints de gestao dos cards de atencao e ponto focal do RH."""

from typing import List
from app.presentation.compat import APIRouter, Depends, HTTPException, status

from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO, RiskCardDTO
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("/active", response_model=List[RiskCardDTO], status_code=status.HTTP_200_OK)
def get_active_risk_cards(
    container: PulsoAppContainer = Depends(get_container),
) -> List[RiskCardDTO]:
    """Retorna os cards de risco ativos que demandam deliberacao humana do RH."""
    cards = container.risk_card_repo.list_active()
    return [
        RiskCardDTO(
            card_id=c.id,
            area_id=c.area_id,
            area_name=c.area_name,
            area_headcount=c.area_headcount,
            risk_level=c.risk_level.value,
            fator_risco_provavel=c.probable_risk_factor.value,
            o_que_mudou_ultimos_meses=c.evidence_summary,
            contexto_organizacional=c.context_description,
            acao_sugerida=c.suggested_action,
            fontes_consultadas=c.consulted_sources,
            status=c.status.value,
            created_at=c.created_at,
            risk_score=c.risk_score,
            shap_breakdown=c.shap_breakdown,
            ai_provider_used=c.ai_provider_used,
            ai_fallback_triggered=c.ai_fallback_triggered,
        )
        for c in cards
    ]


@router.post(
    "/{card_id}/resolve",
    response_model=PgrInventoryItemDTO,
    status_code=status.HTTP_201_CREATED,
)
def resolve_risk_card_and_register_pgr(
    card_id: str,
    payload: ResolveRiskCardRequestDTO,
    container: PulsoAppContainer = Depends(get_container),
) -> PgrInventoryItemDTO:
    """Registra a deliberacao humana (aprovar/ajustar) e gera o item no PGR (NR-1)."""
    try:
        return container.register_pgr_uc.execute(card_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
