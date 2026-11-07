"""Endpoints para interacao do RH com o agente Pulso em linguagem natural."""

from app.presentation.compat import APIRouter, Depends, status

from app.application.dtos.chat_dto import ChatQueryRequestDTO, ChatQueryResponseDTO
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.post("", response_model=ChatQueryResponseDTO, status_code=status.HTTP_200_OK)
def send_chat_query_to_pulso(
    payload: ChatQueryRequestDTO,
    container: PulsoAppContainer = Depends(get_container),
) -> ChatQueryResponseDTO:
    """Envia pergunta ao agente Pulso, aplicando guardrails de privacidade antes de responder."""
    return container.chat_uc.execute(payload)
