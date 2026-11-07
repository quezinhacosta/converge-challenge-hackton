"""Health check endpoints for liveness and readiness monitoring."""

from typing import Dict
from fastapi import APIRouter

router = APIRouter()


@router.get("", response_model=Dict[str, str])
def get_health_status() -> Dict[str, str]:
    """Retrieve the operational status of the PayTrust API and services.

    Returns:
        Dict[str, str]: Service status and version metadata.
    """
    return {
        "status": "healthy",
        "service": "paytrust-backend",
        "version": "0.1.0",
    }
