"""Interfaces de repositorio da camada de dominio do Pulso."""

from app.domain.repositories.interfaces import (
    AreaRepository,
    PgrInventoryRepository,
    RiskCardRepository,
    SignalRepository,
    SurveyRepository,
)

__all__ = [
    "AreaRepository",
    "SignalRepository",
    "RiskCardRepository",
    "PgrInventoryRepository",
    "SurveyRepository",
]
