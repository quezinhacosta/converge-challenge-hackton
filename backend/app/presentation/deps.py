"""Provedor de dependencias e estado em memoria para a API do Pulso."""

from collections.abc import Iterator
from typing import Any

from fastapi import Depends, Request
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
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
from app.presentation.security import request_session, runtime_context
from scripts.seed_synthetic_data import seed_in_memory_repositories


class PulsoAppContainer:
    """Container singleton contendo repositorios em memoria populados e casos de uso."""

    def __init__(
        self,
        repositories: Any = None,
        seed: bool = True,
        context: ContextoAutorizado | None = None,
        session: Session | None = None,
        knowledge: Any = None,
    ) -> None:
        self.knowledge = knowledge
        self.context = context
        self.session = session
        if repositories is None:
            self.area_repo = InMemoryAreaRepository()
            self.signal_repo = InMemorySignalRepository()
            self.risk_card_repo = InMemoryRiskCardRepository()
            self.pgr_repo = InMemoryPgrInventoryRepository()
            self.survey_repo = InMemorySurveyRepository()
        else:
            for name in ("area_repo", "signal_repo", "risk_card_repo", "pgr_repo", "survey_repo"):
                setattr(self, name, getattr(repositories, name))
        self.seed_summary = None
        if seed:
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
        operational_tools = []
        if context is not None and "RH" in context.papeis:
            from app.infrastructure.persistence.database import get_engine
            from app.rh_actions.tools import build_rh_tools

            operational_tools = build_rh_tools(context, lambda: Session(get_engine()))
        self.llm_provider = StrandsFeatherlessProvider(
            chat_tools=operational_tools
            + build_area_tools(self.area_repo, self.collect_signals_uc)
            + list(knowledge.chat_tools if knowledge else ())
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


container = PulsoAppContainer()  # Apenas fixture/demo; nunca selecionado em producao.


def get_container(
    request: Request,
    ctx: ContextoAutorizado | None = Depends(runtime_context),
    session: Session | None = Depends(request_session, scope="function"),
) -> Iterator[PulsoAppContainer]:
    """Um container por requisicao autenticada; transacao fecha em request_session."""
    if ctx is None:
        yield container
        return
    from app.infrastructure.persistence.repositories import RepositoryBundle
    from app.presentation.knowledge_integration import get_knowledge_services

    assert session is not None
    knowledge = get_knowledge_services(request, ctx, session)
    yield PulsoAppContainer(
        RepositoryBundle(session, ctx.empresa_id),
        seed=False,
        context=ctx,
        session=session,
        knowledge=knowledge,
    )
