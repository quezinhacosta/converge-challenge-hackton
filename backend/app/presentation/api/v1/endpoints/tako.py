"""Endpoints da API v1 para integracao e sincronizacao com a Tako (customer-api.8arm.io)."""

from datetime import date
from typing import Any, Dict, List
from app.presentation.compat import APIRouter, HTTPException, status
from app.presentation.deps import get_container
from app.infrastructure.integrations.tako import TakoApiClient, TakoSyncService

router = APIRouter()


@router.get("/status")
def get_tako_status() -> Dict[str, Any]:
    """Retorna o status da integracao com a Tako API."""
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
def sync_tako_data() -> Dict[str, Any]:
    """Executa a sincronizacao de dados da Tako para alimentacao do motor NR-1."""
    container = get_container()
    sync_service = TakoSyncService(
        area_repository=container.area_repo,
        signal_repository=container.signal_repo,
    )

    try:
        areas = sync_service.sync_areas_and_headcount()
        metrics = sync_service.sync_monthly_metrics(competence_period=date.today().replace(day=1))
        return {
            "status": "success",
            "message": "Sincronização com Tako concluída com sucesso.",
            "areas_synchronized": len(areas),
            "metrics_calculated": len(metrics),
            "areas": [{"id": a.id, "name": a.name, "headcount": a.headcount} for a in areas],
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Erro durante sincronizacao com a Tako API: {str(exc)}",
        )


@router.post("/webhook")
def receive_tako_webhook(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Receptor de webhooks da Tako para ingestao de eventos em tempo real."""
    container = get_container()
    sync_service = TakoSyncService(
        area_repository=container.area_repo,
        signal_repository=container.signal_repo,
    )

    result_message = sync_service.process_webhook_payload(payload)
    return {
        "status": "received",
        "detail": result_message,
    }
