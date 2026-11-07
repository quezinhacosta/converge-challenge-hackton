"""Endpoints de gestao dos cards de atencao e ponto focal do RH."""


from fastapi import APIRouter, Depends, HTTPException, status

from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO, RiskCardDTO
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.get("/active", response_model=list[RiskCardDTO], status_code=status.HTTP_200_OK)
def get_active_risk_cards(
    container: PulsoAppContainer = Depends(get_container),
) -> list[RiskCardDTO]:
    """Retorna os cards de atencao em aberto aguardando apreciacao e deliberacao do RH."""
    active_cards = container.risk_card_repo.list_active()
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
            risk_score=getattr(c, "risk_score", 0.0),
            shap_breakdown=getattr(c, "shap_breakdown", []),
            ai_provider_used=getattr(c, "ai_provider_used", "xgboost+gemini-1.5-pro"),
            ai_fallback_triggered=getattr(c, "ai_fallback_triggered", False),
        )
        for c in active_cards
    ]


@router.post(
    "/{card_id}/resolve",
    response_model=PgrInventoryItemDTO,
    status_code=status.HTTP_200_OK,
)
def resolve_risk_card(
    card_id: str,
    payload: ResolveRiskCardRequestDTO,
    container: PulsoAppContainer = Depends(get_container),
) -> PgrInventoryItemDTO:
    """Deliberacao humana (1-clique) do RH: Aprovar no PGR, Ajustar Acao ou Descartar."""
    try:
        return container.register_pgr_uc.execute(card_id, payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
