"""Interfaces e definicoes de tipos para provedores de LLM e contingencia."""

from typing import Any, Protocol


class LLMProviderProtocol(Protocol):
    """Protocolo padrao que todo provedor de IA generativa deve implementar."""

    @property
    def name(self) -> str:
        """Nome identificador do provedor (ex: 'gemini-1.5-pro', 'local-deterministic')."""
        ...

    def generate_hypothesis_and_action(
        self,
        area_name: str,
        metrics_summary: str,
        context_events: list[dict[str, Any]],
        shap_narrative: str,
        factor: str,
    ) -> tuple[str, str]:
        """Gera a hipotese de contexto organizacional e a sugestao de acao do PGR."""
        ...

    def generate_chat_reply(
        self,
        query_text: str,
        context_data: dict[str, Any],
    ) -> str:
        """Gera a resposta em linguagem natural para o chat corporativo do RH."""
        ...

    def is_available(self) -> bool:
        """Verifica se o provedor esta pronto para operacao."""
        ...
