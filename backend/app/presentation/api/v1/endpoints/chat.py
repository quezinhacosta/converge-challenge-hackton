"""Endpoints para interacao do RH com o agente Pulso em linguagem natural."""

from fastapi import APIRouter, HTTPException, status

from app.application.dtos.chat_dto import ChatQueryRequestDTO, ChatQueryResponseDTO

router = APIRouter()


@router.post("", response_model=ChatQueryResponseDTO, status_code=status.HTTP_200_OK)
def send_chat_query_to_pulso(payload: ChatQueryRequestDTO) -> ChatQueryResponseDTO:
    """Envia pergunta ao agente Pulso, aplicando guardrails de privacidade antes de responder."""
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando injecao de dependencias.",
    )
