"""Testes do provedor Strands/Featherless sem rede (o LLM e substituido por respostas fixas)."""

from typing import Any

from app.infrastructure.llm.resilience.failover_manager import FailoverManager
from app.infrastructure.llm.resilience.strands_provider import (
    StrandsFeatherlessProvider,
    clean_model_text,
)
from app.infrastructure.llm.schemas import ContextHypothesis, RegulatoryAssessment
from app.infrastructure.llm.settings import LlmSettings
from app.presentation.deps import PulsoAppContainer


def _settings(enabled: bool = True, key: str | None = "test-key") -> LlmSettings:
    return LlmSettings(
        api_key=key,
        base_url="https://example.invalid/v1",
        model_id="test-model",
        temperature=0.0,
        max_tokens=100,
        timeout_seconds=1.0,
        enabled=enabled,
    )


class _FakeStrandsProvider(StrandsFeatherlessProvider):
    """Substitui a chamada ao modelo por respostas fixas validadas pelos schemas."""

    def __init__(self) -> None:
        super().__init__(settings=_settings())
        self.calls: list[str] = []

    def _run_structured(self, system_prompt: str, prompt: str, output_model: Any) -> Any:
        self.calls.append(output_model.__name__)
        if output_model is ContextHypothesis:
            return ContextHypothesis(
                hipotese="A piora comecou 2 semanas apos a nova meta.",
                evento_relacionado="nova meta",
                confianca=0.8,
            )
        return RegulatoryAssessment(
            justificativa="Atestados +45% e horas extras +60%.",
            referencia_nr1="Item 1.5.5.2.2",
            medida_sugerida="Revisar a meta com a lideranca em 15 dias (gestor da area).",
            indicador_acompanhamento="dias de atestado no proximo fechamento",
            confianca=0.7,
        )


def test_clean_model_text_strips_degenerate_runs() -> None:
    assert clean_model_text("!!!!!!!!!!!!\n\nArea de Design oculta.") == "Area de Design oculta."
    assert clean_model_text("Atencao!! Ok.") == "Atencao!! Ok."


def test_provider_unavailable_without_key() -> None:
    assert StrandsFeatherlessProvider(settings=_settings(key=None)).is_available() is False
    assert StrandsFeatherlessProvider(settings=_settings(enabled=False)).is_available() is False


def test_specialists_compose_hypothesis_and_action() -> None:
    provider = _FakeStrandsProvider()
    hypothesis, action = provider.generate_hypothesis_and_action(
        "Atendimento",
        "atestados +45%",
        [{"date": "2026-08-01", "desc": "nova meta"}],
        "",
        "SOBRECARGA_METAS",
    )
    assert provider.calls == ["ContextHypothesis", "RegulatoryAssessment"]
    assert "nova meta" in hypothesis
    assert "1.5.5.2.2" in action


def test_demo_cache_reuses_first_good_answer(tmp_path: Any) -> None:
    import dataclasses

    provider = _FakeStrandsProvider()
    provider.settings = dataclasses.replace(
        provider.settings, demo_cache_path=str(tmp_path / "cache.json")
    )
    first = provider.generate_hypothesis_and_action("Atendimento", "m", [], "", "SOBRECARGA_METAS")
    second = provider.generate_hypothesis_and_action("Atendimento", "m", [], "", "SOBRECARGA_METAS")
    assert first == second
    assert provider.calls == ["ContextHypothesis", "RegulatoryAssessment"]


def test_harassment_never_reaches_llm() -> None:
    provider = _FakeStrandsProvider()
    _, action = provider.generate_hypothesis_and_action("Vendas", "", [], "", "ASSEDIO")
    assert provider.calls == []
    assert "comite de compliance" in action


def test_failover_uses_local_engine_when_primary_raises() -> None:
    class _Broken(_FakeStrandsProvider):
        def _run_structured(self, *args: Any, **kwargs: Any) -> Any:
            raise RuntimeError("timeout")

    manager = FailoverManager(primary_provider=_Broken())
    _, action, meta = manager.generate_hypothesis_and_action(
        "Atendimento", "", [], "", "SOBRECARGA_METAS"
    )
    assert meta.fallback_triggered is True
    assert "revisar a meta" in action


def test_small_area_is_not_analyzed() -> None:
    container = PulsoAppContainer()
    result = container.analyze_risks_uc.execute("area_des")
    assert result["is_anonymized"] is True
    assert result["context_events"] == []


def test_chat_tools_hide_small_areas() -> None:
    container = PulsoAppContainer()
    chat_tools_any: list[Any] = container.llm_provider.chat_tools  # type: ignore[assignment]
    tools = {getattr(t, "tool_name", getattr(t, "__name__", "")): t for t in chat_tools_any}
    hidden = tools["sinais_da_area"]("Design")
    assert hidden["dados_ocultos_lgpd"] is True
    visible = tools["sinais_da_area"]("logistica")
    assert visible["area_id"] == "area_log"
