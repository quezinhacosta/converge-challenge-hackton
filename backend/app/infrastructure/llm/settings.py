"""Configuracao do LLM (Featherless via API compativel com OpenAI) lida de variaveis de ambiente.

Nenhuma chave fica no codigo. Em desenvolvimento, coloque os valores em backend/.env
(arquivo ignorado pelo git) ou exporte as variaveis no terminal.
"""

import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_BASE_URL = "https://api.featherless.ai/v1"
DEFAULT_MODEL_ID = "Qwen/Qwen2.5-72B-Instruct"


def _load_dotenv_if_present() -> None:
    """Carrega backend/.env se python-dotenv estiver instalado (opcional)."""
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    env_path = Path(__file__).resolve().parents[3] / ".env"
    if env_path.exists():
        load_dotenv(env_path, override=False)


def _as_bool(value: str | None, default: bool) -> bool:
    if value is None or value.strip() == "":
        return default
    return value.strip().lower() in {"1", "true", "yes", "sim", "on"}


@dataclass(frozen=True)
class LlmSettings:
    """Parametros do modelo de linguagem usados pelos agentes Strands."""

    api_key: str | None
    base_url: str
    model_id: str
    temperature: float
    max_tokens: int
    timeout_seconds: float
    enabled: bool
    demo_cache_path: str | None = None
    budget_seconds: float = 40.0

    @property
    def is_usable(self) -> bool:
        """True quando o LLM esta habilitado e ha chave configurada."""
        return self.enabled and bool(self.api_key)


def load_llm_settings() -> LlmSettings:
    """Le a configuracao do ambiente. O LLM so liga se houver FEATHERLESS_API_KEY."""
    _load_dotenv_if_present()
    api_key = os.getenv("FEATHERLESS_API_KEY")
    return LlmSettings(
        api_key=api_key,
        base_url=os.getenv("FEATHERLESS_BASE_URL", DEFAULT_BASE_URL),
        model_id=os.getenv("PULSO_LLM_MODEL", DEFAULT_MODEL_ID),
        temperature=float(os.getenv("PULSO_LLM_TEMPERATURE", "0.2")),
        max_tokens=int(os.getenv("PULSO_LLM_MAX_TOKENS", "400")),
        timeout_seconds=float(os.getenv("PULSO_LLM_TIMEOUT", "25")),
        enabled=_as_bool(os.getenv("PULSO_LLM_ENABLED"), default=bool(api_key)),
        demo_cache_path=os.getenv("PULSO_LLM_DEMO_CACHE") or None,
        budget_seconds=float(os.getenv("PULSO_LLM_BUDGET", "40")),
    )
