"""Submodulo de resiliencia, circuit breaker e substituicao automatica de IA."""

from app.infrastructure.llm.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from app.infrastructure.llm.resilience.failover_manager import (
    FailoverExecutionMetadata,
    FailoverManager,
)
from app.infrastructure.llm.resilience.gemini_provider import GeminiProvider
from app.infrastructure.llm.resilience.interfaces import LLMProviderProtocol
from app.infrastructure.llm.resilience.rule_based_fallback_provider import RuleBasedFallbackProvider

__all__ = [
    "LLMProviderProtocol",
    "CircuitBreaker",
    "CircuitState",
    "CircuitBreakerOpenError",
    "FailoverExecutionMetadata",
    "FailoverManager",
    "GeminiProvider",
    "RuleBasedFallbackProvider",
]
