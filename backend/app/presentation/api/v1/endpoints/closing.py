"""Endpoint do fechamento: roda o Pulso em todas as areas (gatilho do Slack, agenda ou MCP)."""

from typing import Any

from app.presentation.compat import APIRouter, Depends, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.post("", response_model=list[dict[str, Any]], status_code=status.HTTP_200_OK)
def run_closing_cycle(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> list[dict[str, Any]]:
    """Analisa todas as areas e devolve o resultado de cada uma (sem duplicar cards)."""
    return container.run_analysis_uc.execute_all()
