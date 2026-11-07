"""Endpoints do Inventario de Riscos e Plano de Acao do PGR (NR-1)."""

from typing import List
from fastapi import APIRouter, HTTPException, status

from app.application.dtos.pgr_dto import PgrInventoryItemDTO, ReassessmentEvaluationDTO

router = APIRouter()


@router.get("/inventory", response_model=List[PgrInventoryItemDTO], status_code=status.HTTP_200_OK)
def get_pgr_inventory() -> List[PgrInventoryItemDTO]:
    """Retorna o inventario oficial de riscos psicossociais e planos de acao do PGR."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )


@router.post("/{item_id}/reassess", response_model=ReassessmentEvaluationDTO, status_code=status.HTTP_200_OK)
def reassess_pgr_item(item_id: str) -> ReassessmentEvaluationDTO:
    """Mede a eficacia da intervencao apos 60 dias e encerra o ciclo ou reabre o card."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )
