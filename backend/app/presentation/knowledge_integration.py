"""Ponto compartilhado de integracao. A implementacao documental pertence ao Claude."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.application.dtos.chat_dto import ChatQueryResponseDTO
from app.presentation.security import runtime_context


class KnowledgeServices(Protocol):
    # Instancia exclusiva da requisicao; o contexto nao pode ficar em singleton global.
    chat_tools: tuple[Any, ...]

    def finalize_chat(self, response: ChatQueryResponseDTO) -> ChatQueryResponseDTO: ...


@dataclass(frozen=True)
class KnowledgeIntegration:
    router: APIRouter
    factory: Callable[[ContextoAutorizado, Any], KnowledgeServices]


def get_knowledge_services(
    request: Request, ctx: ContextoAutorizado | None, session: Session | None
) -> KnowledgeServices | None:
    binding: KnowledgeIntegration | None = request.app.state.knowledge_integration
    if binding is None:
        return None
    if ctx is None:
        raise HTTPException(401, "Conhecimento exige identidade autenticada.")
    return binding.factory(ctx, session)


def unavailable_router() -> APIRouter:
    router = APIRouter()

    @router.get("/status")
    def unavailable(ctx: ContextoAutorizado | None = Depends(runtime_context)) -> None:
        if ctx is None:
            raise HTTPException(401, "Conhecimento exige identidade autenticada.")
        raise HTTPException(
            503, {"code": "KNOWLEDGE_NOT_INSTALLED", "message": "Cadastro documental indisponivel."}
        )

    return router
