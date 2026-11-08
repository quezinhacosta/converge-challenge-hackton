"""Módulo de integração com a API da Tako (customer-api.8arm.io)."""

from app.infrastructure.integrations.tako.tako_client import TakoApiClient
from app.infrastructure.integrations.tako.tako_sync_service import TakoSyncService

__all__ = ["TakoApiClient", "TakoSyncService"]
