"""Gerenciador de Failover e Substituicao de Modelos de IA (Resiliencia em Cascata).

Garante que o Digital Worker Pulso NUNCA fique fora do ar:
    1. Tenta o Provedor Primario (ex: Gemini 1.5 Pro).
    2. Se houver falha, timeout ou circuit breaker aberto, chaveia para o Provedor Secundario.
    3. Se todos os provedores em nuvem falharem, assume o Provedor Terciario Deterministico Local.
"""

from dataclasses import dataclass
import logging
import time
from typing import Any, Dict, List, Optional, Tuple

from app.infrastructure.llm.resilience.circuit_breaker import CircuitBreaker
from app.infrastructure.llm.resilience.gemini_provider import GeminiProvider
from app.infrastructure.llm.resilience.interfaces import LLMProviderProtocol
from app.infrastructure.llm.resilience.rule_based_fallback_provider import RuleBasedFallbackProvider

logger = logging.getLogger(__name__)


@dataclass
class FailoverExecutionMetadata:
    """Metadados de observabilidade sobre a execucao e eventual substituicao de IA.

    Atributos:
        provider_used: Nome do provedor que efetivamente concluiu a requisicao.
        fallback_triggered: Indica se houve ativacao do plano de contingencia.
        failover_reason: Causa do chaveamento caso o primario tenha falhado.
        circuit_state: Estado atual do circuito do provedor principal.
        latency_ms: Tempo total de execucao em milissegundos.
    """

    provider_used: str
    fallback_triggered: bool
    failover_reason: Optional[str] = None
    circuit_state: str = "CLOSED"
    latency_ms: float = 0.0

    def to_dict(self) -> Dict[str, Any]:
        """Converte metadados para dicionario serializavel."""
        return {
            "provider_used": self.provider_used,
            "fallback_triggered": self.fallback_triggered,
            "failover_reason": self.failover_reason,
            "circuit_state": self.circuit_state,
            "latency_ms": round(self.latency_ms, 2),
        }


class FailoverManager:
    """Orquestrador da cadeia de resiliencia e substituicao automatica de IA."""

    def __init__(
        self,
        primary_provider: Optional[LLMProviderProtocol] = None,
        secondary_provider: Optional[LLMProviderProtocol] = None,
        fallback_provider: Optional[LLMProviderProtocol] = None,
    ) -> None:
        """Inicializa os provedores da cascata e seus circuit breakers."""
        self.primary = primary_provider or GeminiProvider()
        self.secondary = secondary_provider
        self.fallback = fallback_provider or RuleBasedFallbackProvider()

        self.primary_circuit = CircuitBreaker(provider_name=self.primary.name)

    def generate_hypothesis_and_action(
        self,
        area_name: str,
        metrics_summary: str,
        context_events: List[Dict[str, Any]],
        shap_narrative: str,
        factor: str,
    ) -> Tuple[str, str, FailoverExecutionMetadata]:
        """Executa a geracao da hipotese e acao tentando a cadeia de provedores em cascata.

        Retorna:
            Tuple[str, str, FailoverExecutionMetadata]:
                (hipotese, acao_proposta, metadados_de_execucao).
        """
        start_time = time.perf_counter()

        # 1. Tentativa com o Provedor Primario (protegido por Circuit Breaker)
        if self.primary.is_available() and self.primary_circuit.can_execute():
            try:
                hypothesis, action = self.primary_circuit.execute_with_circuit(
                    lambda: self.primary.generate_hypothesis_and_action(
                        area_name, metrics_summary, context_events, shap_narrative, factor
                    )
                )
                latency = (time.perf_counter() - start_time) * 1000.0
                metadata = FailoverExecutionMetadata(
                    provider_used=self.primary.name,
                    fallback_triggered=False,
                    circuit_state=self.primary_circuit.state.value,
                    latency_ms=latency,
                )
                return hypothesis, action, metadata
            except Exception as exc:
                fail_reason = f"Falha no provedor primario '{self.primary.name}': {str(exc)}"
                logger.warning("%s. Chaveando para o proximo da cadeia.", fail_reason)
        else:
            fail_reason = (
                f"Provedor primario '{self.primary.name}' indisponivel ou com circuito "
                f"'{self.primary_circuit.state.value}'."
            )

        # 2. Tentativa com Provedor Secundario (se configurado)
        if self.secondary and self.secondary.is_available():
            try:
                hypothesis, action = self.secondary.generate_hypothesis_and_action(
                    area_name, metrics_summary, context_events, shap_narrative, factor
                )
                latency = (time.perf_counter() - start_time) * 1000.0
                metadata = FailoverExecutionMetadata(
                    provider_used=self.secondary.name,
                    fallback_triggered=True,
                    failover_reason=fail_reason,
                    circuit_state=self.primary_circuit.state.value,
                    latency_ms=latency,
                )
                return hypothesis, action, metadata
            except Exception as exc:
                fail_reason += f" | Falha no provedor secundario: {str(exc)}"

        # 3. Contingencia Absoluta: Provedor Terciario Deterministico Local (Zero Falhas)
        hypothesis, action = self.fallback.generate_hypothesis_and_action(
            area_name, metrics_summary, context_events, shap_narrative, factor
        )
        latency = (time.perf_counter() - start_time) * 1000.0
        metadata = FailoverExecutionMetadata(
            provider_used=self.fallback.name,
            fallback_triggered=True,
            failover_reason=fail_reason,
            circuit_state=self.primary_circuit.state.value,
            latency_ms=latency,
        )

        return hypothesis, action, metadata

    def generate_chat_reply(
        self,
        query_text: str,
        context_data: Dict[str, Any],
    ) -> Tuple[str, FailoverExecutionMetadata]:
        """Gera a resposta do chat corporativo com substituicao automatica em caso de falha."""
        start_time = time.perf_counter()

        if self.primary.is_available() and self.primary_circuit.can_execute():
            try:
                reply = self.primary_circuit.execute_with_circuit(
                    lambda: self.primary.generate_chat_reply(query_text, context_data)
                )
                latency = (time.perf_counter() - start_time) * 1000.0
                metadata = FailoverExecutionMetadata(
                    provider_used=self.primary.name,
                    fallback_triggered=False,
                    circuit_state=self.primary_circuit.state.value,
                    latency_ms=latency,
                )
                return reply, metadata
            except Exception as exc:
                fail_reason = f"Provedor primario falhou no chat: {str(exc)}"
        else:
            fail_reason = f"Circuito do provedor primario '{self.primary_circuit.state.value}'."

        # Contingencia com o Fallback Local
        reply = self.fallback.generate_chat_reply(query_text, context_data)
        latency = (time.perf_counter() - start_time) * 1000.0
        metadata = FailoverExecutionMetadata(
            provider_used=self.fallback.name,
            fallback_triggered=True,
            failover_reason=fail_reason,
            circuit_state=self.primary_circuit.state.value,
            latency_ms=latency,
        )
        return reply, metadata
