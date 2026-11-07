"""Casos de uso da aplicacao Pulso."""

from app.application.use_cases.analyze_psychosocial_risks_use_case import (
    AnalyzePsychosocialRisksUseCase,
)
from app.application.use_cases.collect_and_aggregate_signals_use_case import (
    CollectAndAggregateSignalsUseCase,
)
from app.application.use_cases.generate_risk_card_use_case import (
    GenerateRiskCardUseCase,
)
from app.application.use_cases.process_rh_chat_query_use_case import (
    ProcessRhChatQueryUseCase,
)
from app.application.use_cases.register_pgr_action_use_case import (
    RegisterPgrActionUseCase,
)
from app.application.use_cases.track_risk_evolution_use_case import (
    TrackRiskEvolutionUseCase,
)

__all__ = [
    "CollectAndAggregateSignalsUseCase",
    "AnalyzePsychosocialRisksUseCase",
    "GenerateRiskCardUseCase",
    "RegisterPgrActionUseCase",
    "TrackRiskEvolutionUseCase",
    "ProcessRhChatQueryUseCase",
]
