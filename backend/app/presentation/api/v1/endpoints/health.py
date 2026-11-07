"""Endpoint de verificacao de integridade e liveness da API do Pulso."""

from typing import Dict
from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=Dict[str, str])
def get_health_status() -> Dict[str, str]:
    """Retorna o status operacional da API do Pulso."""
    return {
        "status": "healthy",
        "service": "pulso-backend",
        "version": "0.1.0",
    }
