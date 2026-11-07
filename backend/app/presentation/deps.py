"""Provedor de dependencias e estado em memoria para a API do Pulso."""

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
from app.application.use_cases.run_area_analysis_use_case import RunAreaAnalysisUseCase
from app.application.use_cases.track_risk_evolution_use_case import (
    TrackRiskEvolutionUseCase,
)
from app.infrastructure.guardrails.privacy_guardrail import (
    PrivacyAndEthicsGuardrail,
)
from app.infrastructure.llm.pulso_agent import PulsoAgentLLM
from app.infrastructure.llm.resilience.failover_manager import FailoverManager
from app.infrastructure.llm.resilience.gemini_provider import GeminiProvider
from app.infrastructure.llm.resilience.strands_provider import StrandsFeatherlessProvider
from app.infrastructure.repositories.in_memory_pulso_repositories import (
    InMemoryAreaRepository,
    InMemoryPgrInventoryRepository,
    InMemoryRiskCardRepository,
    InMemorySignalRepository,
    InMemorySurveyRepository,
)
from app.infrastructure.tools.strands_area_tools import build_area_tools
from scripts.seed_synthetic_data import seed_in_memory_repositories


class PulsoAppContainer:
    """Container singleton contendo repositorios em memoria populados e casos de uso."""

    def __init__(self) -> None:
        self.area_repo = InMemoryAreaRepository()
        self.signal_repo = InMemorySignalRepository()
        self.risk_card_repo = InMemoryRiskCardRepository()
        self.pgr_repo = InMemoryPgrInventoryRepository()
        self.survey_repo = InMemorySurveyRepository()

        # Popular base sintetica dos 7 cenarios
        self.seed_summary = seed_in_memory_repositories(
            self.area_repo,
            self.signal_repo,
            self.risk_card_repo,
            self.pgr_repo,
            self.survey_repo,
        )

        # Componentes de infraestrutura
        self.guardrail = PrivacyAndEthicsGuardrail(
            known_area_terms=[a.name for a in self.area_repo.list_all()]
        )
        self.collect_signals_uc = CollectAndAggregateSignalsUseCase(
            self.area_repo, self.signal_repo, self.guardrail
        )

        # Camada 2: agentes Strands na Featherless (primario), Gemini (secundario), regras (local)
        self.llm_provider = StrandsFeatherlessProvider(
            chat_tools=build_area_tools(self.area_repo, self.collect_signals_uc)
        )
        self.llm_agent = PulsoAgentLLM(
            failover_manager=FailoverManager(
                primary_provider=self.llm_provider,
                secondary_provider=GeminiProvider(),
            ),
            devolutiva_writer=self.llm_provider,
        )

        # Casos de uso
        self.analyze_risks_uc = AnalyzePsychosocialRisksUseCase(
            self.area_repo, self.signal_repo, self.survey_repo, self.llm_agent
        )
        self.generate_card_uc = GenerateRiskCardUseCase(
            self.area_repo, self.risk_card_repo, self.llm_agent
        )
        self.register_pgr_uc = RegisterPgrActionUseCase(
            self.risk_card_repo, self.pgr_repo, self.survey_repo, self.llm_agent
        )
        self.track_evolution_uc = TrackRiskEvolutionUseCase(
            self.pgr_repo, self.risk_card_repo, self.signal_repo
        )
        self.chat_uc = ProcessRhChatQueryUseCase(self.guardrail, self.llm_agent)
        self.run_analysis_uc = RunAreaAnalysisUseCase(
            self.area_repo, self.risk_card_repo, self.analyze_risks_uc, self.generate_card_uc
        )


container = PulsoAppContainer()


def get_container() -> PulsoAppContainer:
    """Retorna a instancia singleton do container da aplicacao."""
    return container
