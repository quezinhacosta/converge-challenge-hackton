"""DTOs para a interacao do RH com o agente Pulso no chat corporativo."""


from app.application.dtos.compat import BaseModel, Field


class ChatQueryRequestDTO(BaseModel):
    """Pergunta ou solicitacao enviada pelo RH ao agente Pulso no chat.

    Exemplos:
        - "Como esta o time de Logistica?"
        - "Me mostra os atestados da Carla" (deve ser barrado pelo guardrail etico)
    """

    user_id: str
    user_name: str
    query_text: str = Field(..., min_length=2)


class ChatQueryResponseDTO(BaseModel):
    """Resposta gerada pelo agente Pulso respeitando estritamente os limites eticos.

    Atributos:
        reply_text: Resposta explicativa ou justificativa de recusa.
        is_refusal: True se a solicitacao tentou violar guardrails (pedir dados individuais).
        refusal_reason: Fundamentacao da recusa (LGPD, foco exclusivo em times/areas).
        sources_used: Fontes consultadas no raciocinio.
    """

    reply_text: str
    is_refusal: bool = False
    refusal_reason: str | None = None
    sources_used: list[str] = Field(default_factory=list)
