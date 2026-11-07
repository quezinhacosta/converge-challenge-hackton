"""Gerador de texto para respostas fundamentadas (Strands + Featherless, sem ferramentas).

Reaproveita a configuracao existente (FEATHERLESS_API_KEY, PULSO_LLM_MODEL...). Sem chave,
nao e criado e o respondedor usa o plano B extrativo.
"""

from typing import Any

from app.infrastructure.llm.settings import LlmSettings, load_llm_settings


class GeradorTextoStrands:
    def __init__(self, settings: LlmSettings | None = None) -> None:
        self.settings = settings or load_llm_settings()
        self.nome_modelo = self.settings.model_id
        self._modelo: Any | None = None

    @classmethod
    def criar_se_configurado(cls) -> "GeradorTextoStrands | None":
        settings = load_llm_settings()
        return cls(settings) if settings.is_usable else None

    def _model(self) -> Any:
        if self._modelo is None:
            from strands.models.openai import OpenAIModel

            self._modelo = OpenAIModel(
                client_args={
                    "api_key": self.settings.api_key,
                    "base_url": self.settings.base_url,
                    "timeout": self.settings.timeout_seconds,
                    "max_retries": 0,
                },
                model_id=self.settings.model_id,
                params={
                    "temperature": 0.1,
                    "max_tokens": self.settings.max_tokens,
                    "frequency_penalty": 0.3,
                },
            )
        return self._modelo

    def gerar(self, sistema: str, usuario: str) -> str:
        from strands import Agent

        agente = Agent(model=self._model(), system_prompt=sistema, tools=[], callback_handler=None)
        return str(agente(usuario)).strip()
