"""Caso de uso para processamento de perguntas do RH no chat com aplicacao dos guardrails eticos."""

from typing import Protocol
from app.application.dtos.chat_dto import ChatQueryRequestDTO, ChatQueryResponseDTO
from app.domain.repositories.interfaces import AreaRepository, SignalRepository


class EthicalGuardrailValidator(Protocol):
    """Protocolo de deteccao de violacao de privacidade (pedidos individuais / quebra de LGPD)."""

    def inspect_query(self, query_text: str) -> tuple[bool, str | None]:
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
        """Inicializa o caso de uso.

        Argumentos:
            guardrail_validator: Validador deterministico e semantico de privacidade.
            chat_service: Servico de raciocinio em laco de ferramentas para areas.
        """
        self.guardrail_validator = guardrail_validator
        self.chat_service = chat_service

    def execute(self, request: ChatQueryRequestDTO) -> ChatQueryResponseDTO:
        """Processa a mensagem do usuario no chat, aplicando guardrails antes de consultar ferramentas.

        Argumentos:
            request: DTO contendo o texto da mensagem e dados do usuario.

        Retorna:
            ChatQueryResponseDTO: Resposta autorizada sobre times ou recusa justificada.
        """
        raise NotImplementedError(
            "ProcessRhChatQueryUseCase.execute e um stub de interface estrutural."
        )
