"""Endpoints para interacao do RH com o agente Pulso em linguagem natural."""

from app.application.dtos.chat_dto import ChatQueryRequestDTO, ChatQueryResponseDTO
from app.presentation.compat import APIRouter, Depends, status
from app.presentation.deps import PulsoAppContainer, get_container

router = APIRouter()


@router.post("", response_model=ChatQueryResponseDTO, status_code=status.HTTP_200_OK)
def send_chat_query_to_pulso(
    payload: ChatQueryRequestDTO,
    container: PulsoAppContainer = Depends(get_container, scope="function"),
) -> ChatQueryResponseDTO:
    """Envia pergunta ao agente Pulso, aplicando guardrails de privacidade antes de responder."""
    if container.context is not None:
        payload = payload.model_copy(
            update={"user_id": str(container.context.usuario_id), "user_name": "RH"}
        )
    response = container.chat_uc.execute(payload)
    if container.knowledge is not None and not response.is_refusal:
        response = container.knowledge.finalize_chat(response)
    return response
