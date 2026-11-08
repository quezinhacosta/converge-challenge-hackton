"""Endpoint de verificacao de integridade e liveness da API do Pulso."""

import os

from app.presentation.compat import APIRouter

router = APIRouter()


@router.get("", response_model=dict[str, str])
def get_health_status() -> dict[str, str]:
    """Retorna o status operacional da API do Pulso."""
    return {
        "status": "healthy",
        "service": "pulso-backend",
        "version": "0.3.0",
        "mode": os.getenv("VYTAI_MODE", "production"),
    }
