"""Testes unitarios para a Camada 1 (XGBoost + SHAP) e Camada de Resiliencia (Failover)."""

import pytest

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.infrastructure.llm.resilience.circuit_breaker import (
    CircuitBreaker,
    CircuitBreakerOpenError,
    CircuitState,
)
from app.infrastructure.llm.resilience.failover_manager import FailoverManager
from app.infrastructure.llm.resilience.rule_based_fallback_provider import RuleBasedFallbackProvider
from app.infrastructure.ml.xgboost_risk_engine import XGBoostRiskEngine


class FailingProviderMock:
    """Mock de provedor que falha propositalmente para testar o failover."""

    name = "mock-failing-llm"

    def is_available(self) -> bool:
        return True

    def generate_hypothesis_and_action(self, *args: object, **kwargs: object) -> tuple[str, str]:
        raise ConnectionResetError("Timeout de 4000ms atingido na API externa.")

    def generate_chat_reply(self, *args: object, **kwargs: object) -> str:
        raise TimeoutError("Falha de rede ao conectar no provedor primario.")


def test_xgboost_shap_atendimento_sobrecarga_breakdown() -> None:
    """Valida se o XGBoost com SHAP atribui corretamente os pesos percentuais de explicabilidade legal."""
    engine = XGBoostRiskEngine()

    result = engine.predict(
        variacao_dias_atestado_pct=45.0,
        variacao_horas_extras_pct=60.0,
        pedidos_demissao=4,
        media_empresa_pedidos_demissao=1.0,
        queda_nota_clima=1.5,
    )

    assert result.risk_level == RiskLevel.VERMELHO
    assert result.probable_factor == PsychosocialRiskFactor.SOBRECARGA_METAS
    assert result.risk_score >= 80.0

    # Verifica se a soma das contribuicoes do SHAP e aproximadamente 100%
    total_pct = sum(item.contribution_pct for item in result.shap_breakdown)
    assert 99.0 <= total_pct <= 101.0

    # Verifica se a feature de maior peso sao os atestados (+45%)
    top_feature = result.shap_breakdown[0]
    assert top_feature.feature_name == "delta_atestados"
    assert top_feature.contribution_pct >= 30.0

    # Verifica a narrativa legal de auditoria
    assert "Auditoria SHAP" in result.audit_narrative


def test_xgboost_shap_logistica_lideranca_breakdown() -> None:
    """Valida se no caso de Logistica o turnover voluntario responde pelo maior peso no SHAP."""
    engine = XGBoostRiskEngine()

    result = engine.predict(
        variacao_dias_atestado_pct=5.0,
        variacao_horas_extras_pct=8.0,
        pedidos_demissao=5,
        media_empresa_pedidos_demissao=1.0,
        queda_nota_clima=1.2,
    )

    assert result.risk_level == RiskLevel.AMARELO
    assert result.probable_factor == PsychosocialRiskFactor.LIDERANCA_CONFLITO
    assert result.shap_breakdown[0].feature_name == "razao_turnover"
    assert result.shap_breakdown[0].contribution_pct == 65.0


def test_circuit_breaker_transition_to_open() -> None:
    """Valida se o circuit breaker abre apos o numero limite de falhas consecutivas."""
    cb = CircuitBreaker(
        provider_name="test-llm", failure_threshold=2, recovery_cooldown_seconds=10.0
    )

    assert cb.state == CircuitState.CLOSED
    assert cb.can_execute() is True

    # Primeira falha
    cb.record_failure(RuntimeError("Erro 500"))
    assert cb.state == CircuitState.CLOSED

    # Segunda falha (atinge o threshold)
    cb.record_failure(RuntimeError("Rate limit 429"))
    assert cb.state == CircuitState.OPEN
    assert cb.can_execute() is False

    # Tentativa de chamada com circuito aberto lanca excecao especifica
    with pytest.raises(CircuitBreakerOpenError):
        cb.execute_with_circuit(lambda: "resultado")


def test_failover_manager_substitui_ia_quando_primario_falha() -> None:
    """Valida se o FailoverManager substitui a IA primária pelo fallback deterministico local sem travar."""
    primary_failing = FailingProviderMock()
    fallback_local = RuleBasedFallbackProvider()

    manager = FailoverManager(
        primary_provider=primary_failing,  # type: ignore
        fallback_provider=fallback_local,
    )

    hypothesis, action, metadata = manager.generate_hypothesis_and_action(
        area_name="Atendimento ao Cliente",
        metrics_summary="Atestados +45%, Horas Extras +60%",
        context_events=[{"date": "2026-08-15", "desc": "Nova meta implantada"}],
        shap_narrative="38% do risco veio dos atestados.",
        factor="SOBRECARGA_METAS",
    )

    # Validacao do chaveamento de contingencia
    assert metadata.fallback_triggered is True
    assert metadata.provider_used == "local-deterministic-engine"
    assert "Timeout" in str(metadata.failover_reason)

    # Validacao do conteudo gerado pelo motor de contingencia
    assert "revisar a meta com a lideranca" in action
    assert "revisao de metas" in hypothesis.lower()
