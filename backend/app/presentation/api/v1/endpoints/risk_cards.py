"""Endpoints de gestao dos cards de atencao e ponto focal do RH."""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO, RiskCardDTO

router = APIRouter()


@router.get("/active", response_model=List[RiskCardDTO], status_code=status.HTTP_200_OK)
def get_active_risk_cards() -> List[RiskCardDTO]:
    """Retorna os cards de atencao em aberto aguardando apreciacao e deliberacao do RH."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )


@router.post("/{card_id}/resolve", response_model=PgrInventoryItemDTO, status_code=status.HTTP_200_OK)
def resolve_risk_card(card_id: str, payload: ResolveRiskCardRequestDTO) -> PgrInventoryItemDTO:
    """Deliberacao humana (1-clique) do RH: Aprovar no PGR, Ajustar Acao ou Descartar."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )
