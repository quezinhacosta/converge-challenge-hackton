"""Caso de uso para processamento de perguntas do RH no chat com aplicacao dos guardrails eticos."""

from typing import Protocol, Tuple
from app.application.dtos.chat_dto import ChatQueryRequestDTO, ChatQueryResponseDTO


class EthicalGuardrailValidator(Protocol):
    """Protocolo de deteccao de violacao de privacidade (pedidos individuais / quebra de LGPD)."""

    def inspect_query_for_individual_data(self, query_text: str) -> Tuple[bool, str | None]:
        """Avalia se a consulta do usuario solicita dados de individuos ou rankings pessoais."""
        ...


class AgentChatService(Protocol):
    """Protocolo do agente Pulso em laco de ferramentas para responder sobre a saude dos times."""

    def generate_team_response(self, query_text: str) -> tuple[str, list[str]]:
        """Gera resposta consultando exclusivamente dados agregados de times e areas."""
        ...


class ProcessRhChatQueryUseCase:
    """Processa consultas interativas enviadas pelo RH (ex.: 'Como esta o time de Logistica?').

    Guardrail Etico Rigoroso:
        - Bloqueia e recusa imediatamente solicitacoes direcionadas a pessoas especificas
          (ex.: 'Me mostra os atestados da Carla'), explicando que o Pulso atua exclusivamente
          no nivel de areas/times e respeita a LGPD.
    """

    def __init__(
        self,
        guardrail_validator: EthicalGuardrailValidator,
        chat_service: AgentChatService,
    ) -> None:
        """Inicializa o caso de uso."""
        self.guardrail_validator = guardrail_validator
        self.chat_service = chat_service

    def execute(self, request: ChatQueryRequestDTO) -> ChatQueryResponseDTO:
        """Processa a mensagem do usuario no chat, aplicando guardrails antes de consultar ferramentas."""
        is_blocked, refusal_reason = self.guardrail_validator.inspect_query_for_individual_data(
            request.query_text
        )

        # Caso 5 do Pitch: Tentativa de pedir dados de individuo barrada
        if is_blocked and refusal_reason:
            return ChatQueryResponseDTO(
                reply_text=refusal_reason,
                is_refusal=True,
                refusal_reason="LGPD / Foco exclusivo em coletivos e areas (NR-1)",
                sources_used=["guardrail_privacidade_lgpd"],
            )

        # Consulta permitida sobre areas/times
        reply_text, sources = self.chat_service.generate_team_response(request.query_text)
        return ChatQueryResponseDTO(
            reply_text=reply_text,
            is_refusal=False,
            refusal_reason=None,
            sources_used=sources,
        )
