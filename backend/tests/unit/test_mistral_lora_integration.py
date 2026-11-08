"""Testes unitarios para a integracao do modelo Mistral-7B LoRA treinado."""

import os
import pytest

from app.domain.entities.risk_factor import PsychosocialRiskFactor
from app.infrastructure.llm.resilience.failover_manager import FailoverManager
from app.infrastructure.llm.resilience.mistral_lora_provider import (
    MistralLoraProvider,
    _find_default_adapter_path,
)
from app.presentation.deps import get_container


class FailingPrimaryMock:
    name = "mock-failing-cloud-llm"

    def is_available(self) -> bool:
        return True

    def generate_hypothesis_and_action(self, *args: object, **kwargs: object) -> tuple[str, str]:
        raise TimeoutError("Cloud provider offline")

    def generate_chat_reply(self, *args: object, **kwargs: object) -> str:
        raise TimeoutError("Cloud provider chat offline")


def test_mistral_lora_adapter_path_and_files_detected() -> None:
    adapter_path = _find_default_adapter_path()
    assert os.path.exists(adapter_path), f"Diretorio {adapter_path} nao existe"

    provider = MistralLoraProvider(adapter_path=adapter_path)
    assert provider.name == "mistral-7b-lora"
    assert provider.is_available() is True


def test_mistral_lora_generates_nr1_compliant_outputs() -> None:
    provider = MistralLoraProvider()

    # Caso 1: Sobrecarga de Metas
    hipotese, acao = provider.generate_hypothesis_and_action(
        area_name="Atendimento ao Cliente",
        metrics_summary="Atestados: +45.0%, Horas Extras: +60.0%",
        context_events=[{"description": "Aumento de 35% na meta por hora"}],
        shap_narrative="Auditoria SHAP: 42% do risco veio de atestados e horas extras.",
        factor=PsychosocialRiskFactor.SOBRECARGA_METAS.value,
    )
    assert "sobrecarga" in hipotese.lower()
    assert "pgr" in acao.lower()
    assert "meta" in acao.lower()

    # Caso 2: Conflito de Lideranca
    hipotese_lid, acao_lid = provider.generate_hypothesis_and_action(
        area_name="Logística",
        metrics_summary="Demissões: 5, Queda Suporte Liderança: 1.4",
        context_events=[{"description": "Nova gerencia operacional"}],
        shap_narrative="Auditoria SHAP: 65% do risco veio do turnover voluntario.",
        factor=PsychosocialRiskFactor.LIDERANCA_CONFLITO.value,
    )
    assert "liderança" in hipotese_lid.lower() or "lideranca" in hipotese_lid.lower()
    assert "mediação" in acao_lid.lower() or "mediacao" in acao_lid.lower()

    # Caso 3: Chat Corporativo
    reply = provider.generate_chat_reply(
        query_text="Como está a conformidade da área?",
        context_data={
            "area_name": "Atendimento ao Cliente",
            "risk_score": 85.0,
            "risk_level": "VERMELHO",
        },
    )
    assert "Mistral-7B vitAI" in reply
    assert "PGR" in reply


def test_failover_manager_switches_to_mistral_lora_when_cloud_fails() -> None:
    primary = FailingPrimaryMock()
    lora_provider = MistralLoraProvider()

    manager = FailoverManager(
        primary_provider=primary,  # type: ignore
        local_lora_provider=lora_provider,
    )

    hipotese, acao, meta = manager.generate_hypothesis_and_action(
        area_name="Atendimento",
        metrics_summary="Deltas elevados",
        context_events=[{"description": "Meta estressante"}],
        shap_narrative="SHAP alto",
        factor=PsychosocialRiskFactor.SOBRECARGA_METAS.value,
    )

    assert meta.fallback_triggered is True
    assert meta.provider_used == "mistral-7b-lora"
    assert "Cloud provider offline" in str(meta.failover_reason)
    assert "sobrecarga" in hipotese.lower()


def test_app_container_integrates_mistral_lora() -> None:
    from app.presentation.deps import container

    assert hasattr(container, "mistral_lora_provider")
    assert container.mistral_lora_provider.is_available() is True
