"""Endpoints de verificacao de integridade e saude dos servicos da API."""

from typing import Dict
from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=Dict[str, str])
def get_health_status() -> Dict[str, str]:
    """Retorna o estado operacional e versao dos servicos do PayTrust.

    Retorna:
        Dict[str, str]: Dicionario com status de operacao e versao da API.
    """
    return {
        "status": "healthy",
        "service": "paytrust-backend",
        "version": "0.1.0",
    }
