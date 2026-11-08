"""Rota /api/v1/worker/ciclo: o RH (ou o agendador) dispara o ciclo do digital worker."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException

from app.digital_worker.ciclo import canal_slack_configurado, executar_ciclo
from app.presentation.deps import PulsoAppContainer, get_container
from app.rh_actions.service import ActionService

router = APIRouter()


@router.post("/ciclo")
def executar_ciclo_do_worker(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> dict[str, Any]:
    """Fechamento, investigacao e propostas na fila do RH (todas aguardando aprovacao)."""
    ctx = container.context
    if ctx is None or container.session is None:
        raise HTTPException(401, "O ciclo do worker exige identidade autenticada e banco.")
    if "RH" not in ctx.papeis:
        raise HTTPException(403, "Ciclo restrito ao RH.")
    resultado = executar_ciclo(
        ctx,
        container,
        container.knowledge,
        ActionService(container.session, ctx),
        canal_slack=canal_slack_configurado(),
    )
    return resultado.como_dict()
