"""Implementacao do padrao Circuit Breaker para chamadas a provedores de IA.

Evita que timeouts repetidos ou indisponibilidade de APIs externas travem
o Digital Worker, chaveando imediatamente para provedores substitutos ou
para o fallback deterministico local.
"""

import logging
from collections.abc import Callable
from datetime import UTC, datetime
from enum import Enum
from typing import TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(str, Enum):
    """Estados do circuito de protecao."""

    CLOSED = "CLOSED"  # Operacao normal, todas as chamadas sao permitidas
    OPEN = "OPEN"  # Circuito aberto por falhas: chamadas sao bloqueadas imediatamente
    HALF_OPEN = "HALF_OPEN"  # Circuito em teste para avaliar recuperacao do servico


class CircuitBreakerOpenError(Exception):
    """Excecao lancada quando uma chamada e tentada com circuito aberto."""

    def __init__(self, provider_name: str, cooldown_remaining: float) -> None:
        super().__init__(
            f"Circuit breaker aberto para o provedor '{provider_name}'. "
            f"Tente novamente em {cooldown_remaining:.1f} segundos."
        )
        self.provider_name = provider_name
        self.cooldown_remaining = cooldown_remaining


class CircuitBreaker:
    """Controlador de circuito para isolamento de falhas de APIs externas."""

    def __init__(
        self,
        provider_name: str,
        failure_threshold: int = 3,
        recovery_cooldown_seconds: float = 30.0,
    ) -> None:
        """Inicializa o circuit breaker.

        Argumentos:
            provider_name: Nome do provedor monitorado.
            failure_threshold: Quantidade consecutiva de falhas para abrir o circuito.
            recovery_cooldown_seconds: Segundos de espera antes de tentar recuperar (Half-Open).
        """
        self.provider_name = provider_name
        self.failure_threshold = failure_threshold
        self.recovery_cooldown_seconds = recovery_cooldown_seconds

        self.state = CircuitState.CLOSED
        self.consecutive_failures = 0
        self.last_failure_time: float = 0.0
        self.last_state_change: float = datetime.now(UTC).timestamp()

    def record_success(self) -> None:
        """Registra sucesso na execucao, resetando contadores e fechando o circuito."""
        self.consecutive_failures = 0
        if self.state != CircuitState.CLOSED:
            logger.info("Circuit breaker fechado com sucesso para '%s'.", self.provider_name)
            self.state = CircuitState.CLOSED
            self.last_state_change = datetime.now(UTC).timestamp()

    def record_failure(self, error: Exception) -> None:
        """Registra falha na execucao, incrementando o contador e abrindo o circuito se exceder."""
        now = datetime.now(UTC).timestamp()
        self.consecutive_failures += 1
        self.last_failure_time = now

        logger.warning(
            "Falha #%d registrada no provedor '%s': %s",
            self.consecutive_failures,
            self.provider_name,
            str(error),
        )

        if self.consecutive_failures >= self.failure_threshold:
            if self.state != CircuitState.OPEN:
                self.state = CircuitState.OPEN
                self.last_state_change = now
                logger.error(
                    "Circuit breaker ABERTO para o provedor '%s' apos %d falhas consecutivas.",
                    self.provider_name,
                    self.consecutive_failures,
                )

    def can_execute(self) -> bool:
        """Verifica se uma nova chamada pode ser disparada pelo provedor."""
        now = datetime.now(UTC).timestamp()

        if self.state == CircuitState.CLOSED:
            return True

        if self.state == CircuitState.OPEN:
            elapsed = now - self.last_failure_time
            if elapsed >= self.recovery_cooldown_seconds:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change = now
                logger.info(
                    "Circuit breaker para '%s' em modo HALF_OPEN para teste de recuperacao.",
                    self.provider_name,
                )
                return True
            return False

        # Modo HALF_OPEN: permite 1 tentativa de teste
        return True

    def execute_with_circuit(self, operation: Callable[[], T]) -> T:
        """Executa a operacao protegida pelo circuit breaker."""
        now = datetime.now(UTC).timestamp()

        if not self.can_execute():
            remaining = max(0.0, self.recovery_cooldown_seconds - (now - self.last_failure_time))
            raise CircuitBreakerOpenError(self.provider_name, remaining)

        try:
            result = operation()
            self.record_success()
            return result
        except Exception as exc:
            self.record_failure(exc)
            raise exc
