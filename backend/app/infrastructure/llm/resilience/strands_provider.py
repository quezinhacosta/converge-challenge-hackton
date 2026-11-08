"""Provedor primario de IA: agentes Strands sobre a Featherless (API compativel com OpenAI).

Arquitetura multiagente leve:
    - O nivel de risco e o fator vem da camada 1 (codigo). Os agentes nao decidem nivel.
    - Historiador: liga a piora dos indicadores a eventos de contexto da area.
    - Regulatorio: justifica o fator com base na NR-1 e propoe a medida do plano de acao.
    - Comunicacao: escreve a devolutiva "voce falou, a empresa fez".
    - Chat: responde o RH usando ferramentas que so devolvem dados agregados por area.

Qualquer erro (rede, timeout, JSON invalido) sobe como excecao para o FailoverManager,
que chaveia para o proximo provedor ou para o motor deterministico local.
"""

import json
import logging
import re
import time
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from concurrent.futures import TimeoutError as FutureTimeout
from datetime import date
from pathlib import Path
from typing import Any, TypeVar

from app.application.dtos.compat import BaseModel

from app.domain.entities.risk_factor import PsychosocialRiskFactor
from app.infrastructure.llm.knowledge import (
    PRIVACY_RULES,
    factor_catalog_text,
    nr1_references_text,
)
from app.infrastructure.llm.resilience.interfaces import LLMProviderProtocol
from app.infrastructure.llm.resilience.rule_based_fallback_provider import (
    RuleBasedFallbackProvider,
)
from app.infrastructure.llm.schemas import ContextHypothesis, DevolutivaText, RegulatoryAssessment
from app.infrastructure.llm.settings import LlmSettings, load_llm_settings

logger = logging.getLogger(__name__)

T = TypeVar("T", bound=BaseModel)
R = TypeVar("R")

_RETRIES = 1
_FAST_FAILURE_SECONDS = 8.0
# Uma chamada por vez a Featherless (o plano limita concorrencia); daemon nao trava o shutdown.
_EXECUTOR = ThreadPoolExecutor(max_workers=2, thread_name_prefix="pulso-llm")
# Modelos servidos em vLLM as vezes degeneram em "!!!!!!..."; removemos essas sequencias.
_DEGENERATE_RUN = re.compile(r"([^\w\s])\1{7,}")


def clean_model_text(text: str) -> str:
    """Remove sequencias degeneradas de pontuacao repetida e espacos extras."""
    return _DEGENERATE_RUN.sub("", text).strip()


# Fatores que nunca passam pelo LLM: assedio (o agente nao le denuncias) e area estavel (sem custo).
_DETERMINISTIC_FACTORS = {
    PsychosocialRiskFactor.ASSEDIO.value,
    PsychosocialRiskFactor.ESTAVEL_SEM_FATOR.value,
}

HISTORIADOR_PROMPT = f"""Voce e o Historiador de Contexto do VytAI, um digital worker de RH
que gerencia riscos psicossociais da NR-1.
Sua tarefa: ligar a piora dos indicadores de uma AREA a eventos organizacionais proximos no tempo
(nova meta, troca de gestor, reestruturacao). Use somente os dados recebidos; se nao houver
evento que explique, diga isso e use confianca baixa. Todas as datas recebidas sao passadas.
Seja conciso: a hipotese tem no maximo 2 frases. Responda em portugues do Brasil.
{PRIVACY_RULES}"""

REGULATORIO_PROMPT = f"""Voce e o Analista Regulatorio (NR-1) do VytAI.
O fator de risco e o nivel ja foram definidos pelo motor de regras; NAO os altere.
Sua tarefa: justificar o fator com os numeros recebidos, citar o item da NR-1 que fundamenta o
registro no PGR e propor UMA medida organizacional (priorize mudar a organizacao do trabalho antes
de apoio individual), com papel responsavel e prazo em dias, mais um indicador de acompanhamento.
Para medida do plano de acao, a referencia padrao e o item 1.5.5.2.2. Cada campo tem no maximo
2 frases.
Catalogo de fatores:
{factor_catalog_text()}
Referencias da NR-1:
{nr1_references_text()}
Responda em portugues do Brasil.
{PRIVACY_RULES}"""

COMUNICACAO_PROMPT = f"""Voce e o agente de Comunicacao do VytAI.
Escreva mensagens curtas, acolhedoras e concretas para equipes, em portugues do Brasil, sem jargao
juridico e sem prometer o que nao foi aprovado. Nunca cite pessoas nem dados de saude.
{PRIVACY_RULES}"""

CHAT_PROMPT = f"""Voce e o VytAI, analista digital de riscos psicossociais (NR-1) do RH.
Responda perguntas do RH sobre AREAS usando apenas as ferramentas disponiveis. Se a area tiver
menos de 5 pessoas, explique que os dados ficam ocultos por LGPD. Se pedirem dados de uma pessoa,
recuse e explique que o VytAI so trabalha com areas. Seja breve (ate 5 frases) e cite os numeros.
Voce pode preparar intervencoes, comunicacoes e reavaliacoes com as ferramentas disponiveis.
Preparar nao e aprovar ou executar. Nunca diga que enviou mensagem, agendou evento ou concluiu
uma tarefa sem recibo confirmado. Oriente o RH a revisar a proposta na fila /acoes-rh.
Nao tome decisoes do PGR nem registre evidencia de execucao por conta propria.
{PRIVACY_RULES}"""


class StrandsFeatherlessProvider(LLMProviderProtocol):
    """Provedor de IA generativa com agentes Strands e modelo hospedado na Featherless."""

    def __init__(
        self,
        settings: LlmSettings | None = None,
        chat_tools: list[Callable[..., Any]] | None = None,
    ) -> None:
        """Recebe configuracao e as ferramentas (somente por area) usadas pelo agente de chat."""
        self.settings = settings or load_llm_settings()
        self.chat_tools = chat_tools or []
        self._model: Any | None = None
        self._local = RuleBasedFallbackProvider()

    @property
    def name(self) -> str:
        """Identificador exibido nos metadados de execucao."""
        return f"featherless-strands:{self.settings.model_id}"

    def is_available(self) -> bool:
        """Disponivel quando ha chave e o pacote strands esta instalado."""
        if not self.settings.is_usable:
            return False
        try:
            import strands  # noqa: F401
        except ImportError:
            logger.warning("Pacote strands-agents nao instalado; provedor desativado.")
            return False
        return True

    # ------------------------------------------------------------------ infraestrutura

    def _get_model(self) -> Any:
        if self._model is None:
            from strands.models.openai import OpenAIModel

            self._model = OpenAIModel(
                client_args={
                    "api_key": self.settings.api_key,
                    "base_url": self.settings.base_url,
                    "timeout": self.settings.timeout_seconds,
                    "max_retries": 0,
                },
                model_id=self.settings.model_id,
                params={
                    "temperature": self.settings.temperature,
                    "max_tokens": self.settings.max_tokens,
                    # Penalidades leves evitam a degeneracao em "!!!!..." vista na Featherless.
                    "frequency_penalty": 0.3,
                    "presence_penalty": 0.1,
                },
            )
        return self._model

    def _new_agent(self, system_prompt: str, tools: list[Any] | None = None, name: str = "") -> Any:
        from strands import Agent

        return Agent(
            model=self._get_model(),
            system_prompt=system_prompt,
            tools=tools or [],
            callback_handler=None,
            name=name or None,
        )

    def _with_retry(self, task: Callable[[], R], label: str) -> R:
        """Nova tentativa so quando a falha foi rapida (ex.: resposta vazia).

        Falhas lentas (degeneracao ate o limite de tokens, timeout) sobem direto para o
        FailoverManager, para a demo nunca ficar minutos esperando.
        """
        last_error: Exception | None = None
        for attempt in range(1 + _RETRIES):
            started = time.perf_counter()
            try:
                return task()
            except Exception as exc:  # noqa: BLE001 - sobe para o FailoverManager no fim
                last_error = exc
                elapsed = time.perf_counter() - started
                logger.warning(
                    "%s falhou (tentativa %s, %.1fs): %s", label, attempt + 1, elapsed, exc
                )
                if elapsed > _FAST_FAILURE_SECONDS:
                    break
        raise RuntimeError(f"{label} falhou: {last_error}")

    def _run_structured(self, system_prompt: str, prompt: str, output_model: type[T]) -> T:
        """Executa um agente especialista e devolve a saida validada pelo Pydantic."""

        def task() -> T:
            agent = self._new_agent(system_prompt)
            result = agent(prompt, structured_output_model=output_model)
            output = getattr(result, "structured_output", None)
            if not isinstance(output, output_model):
                raise RuntimeError(f"Agente nao devolveu {output_model.__name__} valido.")
            return output

        return self._with_retry(task, output_model.__name__)

    # ------------------------------------------------------------------ protocolo

    def generate_hypothesis_and_action(
        self,
        area_name: str,
        metrics_summary: str,
        context_events: list[dict[str, Any]],
        shap_narrative: str,
        factor: str,
    ) -> tuple[str, str]:
        """Historiador + Regulatorio: hipotese de contexto e medida para o PGR."""
        if factor in _DETERMINISTIC_FACTORS:
            return self._local.generate_hypothesis_and_action(
                area_name, metrics_summary, context_events, shap_narrative, factor
            )

        events_text = (
            "\n".join(f"- {e.get('date', '')}: {e.get('desc', '')}" for e in context_events)
            or "- nenhum evento registrado"
        )
        base_prompt = (
            f"Data de hoje: {date.today().isoformat()}\n"
            f"Area: {area_name}\n"
            f"Indicadores (agregados da area): {metrics_summary}\n"
            f"Explicacao do score: {shap_narrative}\n"
            f"Fator definido pelo motor: {factor}\n"
            f"Eventos de contexto:\n{events_text}\n"
        )

        cache_key = f"{area_name}|{factor}|{metrics_summary}"
        cached = self._read_demo_cache(cache_key)
        if cached is not None:
            return cached

        # Orcamento total: se a Featherless ficar lenta, o FailoverManager assume na hora.
        # A thread continua e, se terminar, grava a resposta no cache de demo.
        future = _EXECUTOR.submit(self._specialists_pipeline, base_prompt, cache_key)
        try:
            return future.result(timeout=self.settings.budget_seconds)
        except FutureTimeout as exc:
            raise RuntimeError(
                f"Agentes passaram do orcamento de {self.settings.budget_seconds:.0f}s"
            ) from exc

    def _specialists_pipeline(self, base_prompt: str, cache_key: str) -> tuple[str, str]:
        """Historiador -> Regulatorio. Roda numa thread para respeitar o orcamento de tempo."""
        hypothesis = self._run_structured(HISTORIADOR_PROMPT, base_prompt, ContextHypothesis)
        assessment = self._run_structured(
            REGULATORIO_PROMPT,
            base_prompt + f"Hipotese do Historiador: {hypothesis.hipotese}\n",
            RegulatoryAssessment,
        )

        hypothesis_text = f"{hypothesis.hipotese} {assessment.justificativa}".strip()
        action_text = (
            f"{assessment.medida_sugerida} Acompanhamento: {assessment.indicador_acompanhamento}. "
            f"Base: {assessment.referencia_nr1}"
        )
        self._write_demo_cache(cache_key, hypothesis_text, action_text)
        return hypothesis_text, action_text

    # ------------------------------------------------------------------ cache de demo

    def _read_demo_cache(self, key: str) -> tuple[str, str] | None:
        """Com PULSO_LLM_DEMO_CACHE definido, reaproveita a ultima resposta boa da IA."""
        path = self.settings.demo_cache_path
        if not path or not Path(path).exists():
            return None
        try:
            entry = json.loads(Path(path).read_text(encoding="utf-8")).get(key)
        except (OSError, ValueError):
            return None
        if not entry:
            return None
        return str(entry[0]), str(entry[1])

    def _write_demo_cache(self, key: str, hypothesis: str, action: str) -> None:
        path = self.settings.demo_cache_path
        if not path:
            return
        try:
            file = Path(path)
            data = json.loads(file.read_text(encoding="utf-8")) if file.exists() else {}
            data[key] = [hypothesis, action]
            file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        except (OSError, ValueError) as exc:
            logger.warning("Nao foi possivel gravar o cache de demo: %s", exc)

    def generate_chat_reply(self, query_text: str, context_data: dict[str, Any]) -> str:
        """Agente de chat com ferramentas por area. O guardrail roda antes, no caso de uso."""
        prompt = query_text
        if context_data:
            prompt = (
                f"Contexto adicional (agregado): {context_data}\n\nPergunta do RH: {query_text}"
            )

        def task() -> str:
            agent = self._new_agent(CHAT_PROMPT, tools=self.chat_tools, name="pulso_chat")
            reply = clean_model_text(str(agent(prompt)))
            if len(reply) < 5:
                raise RuntimeError("Resposta vazia ou degenerada do agente de chat.")
            return reply

        return self._with_retry(task, "chat")

    def generate_devolutiva(self, area_name: str, action_description: str) -> str:
        """Agente de Comunicacao: devolutiva para a equipe apos a aprovacao do RH."""
        output = self._run_structured(
            COMUNICACAO_PROMPT,
            (
                f"Escreva a devolutiva 'voce falou, a empresa fez' para a equipe {area_name}. "
                f"Medida aprovada pelo RH: {action_description}. Maximo de 4 frases."
            ),
            DevolutivaText,
        )
        return output.texto
