"""Rotas /api/v1/worker: ciclo do digital worker e relatorio PDF (somente RH)."""

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Response

from app.digital_worker.ciclo import canal_slack_configurado, executar_ciclo
from app.digital_worker.relatorio import gerar_relatorio_pdf
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


@router.get("/relatorio.pdf")
def baixar_relatorio_pdf(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> Response:
    """Relatorio NR-1 em PDF: sinais por area, focos, PGR, fila do RH e base de conhecimento."""
    ctx = container.context
    if ctx is None or container.session is None:
        raise HTTPException(401, "O relatorio exige identidade autenticada e banco.")
    if "RH" not in ctx.papeis:
        raise HTTPException(403, "Relatorio restrito ao RH.")
    agora = datetime.now(UTC)
    conteudo = gerar_relatorio_pdf(
        ctx, container, container.knowledge, ActionService(container.session, ctx), agora
    )
    nome = f"vytai-relatorio-nr1-{agora:%Y-%m-%d}.pdf"
    return Response(
        content=conteudo,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="{nome}"',
            "Cache-Control": "no-store",
        },
    )
