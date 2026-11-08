"""Endpoints da API v1 para integracao e sincronizacao com a Tako (customer-api.8arm.io)."""

import os
from datetime import date
from typing import Any

from fastapi import Depends

from app.infrastructure.integrations.tako import TakoApiClient, TakoSyncService
from app.presentation.compat import APIRouter, HTTPException, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


def _modo_demo() -> bool:
    return os.getenv("VYTAI_MODE", "production") == "demo"


def _exigir_rh_ou_demo(container: PulsoAppContainer) -> None:
    """Sincronizar altera dados da empresa: so RH autenticado (ou o modo demo sintetico)."""
    ctx = container.context
    if ctx is None and not _modo_demo():
        raise HTTPException(status_code=401, detail="Sincronizacao exige identidade autenticada.")
    if ctx is not None and "RH" not in ctx.papeis:
        raise HTTPException(status_code=403, detail="Sincronizacao restrita ao RH.")


@router.get("/status")
def get_tako_status() -> dict[str, Any]:
    """Retorna o status da integracao com a Tako API (sem expor credenciais)."""
    client = TakoApiClient()
    return {
        "service": "Tako Customer API Integration",
        "base_url": client.base_url,
        "has_credentials": client.has_credentials,
        "status": "connected" if client.has_credentials else "configured_local_fallback",
        "supported_endpoints": [
            "POST /api/v1/auth/token",
            "POST /api/v1/organization/contracts",
            "GET  /api/v1/organization/contracts/",
            "GET  /api/v2/contracts/{contractId}/payslips",
            "GET  /api/v2/contracts/{contractId}/vacations/{vacationId}",
            "GET  /api/v1/webhook/public-keys",
        ],
    }


@router.post("/sync")
def sync_tako_data(
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> dict[str, Any]:
    """Executa a sincronizacao de dados da Tako para alimentacao do motor NR-1."""
    _exigir_rh_ou_demo(container)
    sync_service = TakoSyncService(
        area_repository=container.area_repo,
        signal_repository=container.signal_repo,
    )
    try:
        areas = sync_service.sync_areas_and_headcount()
        metrics = sync_service.sync_monthly_metrics(competence_period=date.today().replace(day=1))
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Falha ao sincronizar com a Tako API. Confira credenciais e limites de uso.",
        ) from exc
    return {
        "status": "success",
        "message": "Sincronização com Tako concluída com sucesso.",
        "areas_synchronized": len(areas),
        "metrics_calculated": len(metrics),
        "areas": [{"id": a.id, "name": a.name, "headcount": a.headcount} for a in areas],
    }


@router.post("/webhook")
def receive_tako_webhook(
    payload: dict[str, Any],
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> dict[str, Any]:
    """Receptor de webhooks da Tako.

    A Tako assina cada evento com RSA-4096 (chaves em /api/v1/webhook/public-keys). Enquanto a
    verificacao da assinatura nao estiver implementada, eventos so sao aceitos no modo demo.
    """
    if not _modo_demo():
        raise HTTPException(
            status_code=501,
            detail="Webhook da Tako indisponivel ate a verificacao da assinatura RSA.",
        )
    sync_service = TakoSyncService(
        area_repository=container.area_repo,
        signal_repository=container.signal_repo,
    )
    return {"status": "received", "detail": sync_service.process_webhook_payload(payload)}
