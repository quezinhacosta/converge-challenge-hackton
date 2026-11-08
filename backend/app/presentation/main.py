"""Fabrica e ponto de entrada da aplicacao FastAPI do VytAI (Pulso).

Disponibiliza:
1. Endpoints diretos da Pessoa B (/fechamento, /areas/{id}, /casos/{id}/decisao, /chat/query).
2. Endpoints modulares da API v1 (/api/v1/health, /api/v1/areas, /api/v1/risk-cards, /api/v1/pgr, /api/v1/chat, /api/v1/fechamento).
"""

import os
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import HTTPException, Request

from app.presentation.api.v1.endpoints import (
    areas as areas_v1,
)
from app.presentation.api.v1.endpoints import (
    chat as chat_v1,
)
from app.presentation.api.v1.endpoints import (
    closing as closing_v1,
)
from app.presentation.api.v1.endpoints import (
    health as health_v1,
)
from app.presentation.api.v1.endpoints import (
    pgr as pgr_v1,
)
from app.presentation.api.v1.endpoints import (
    risk_cards as risk_cards_v1,
)
from app.presentation.api.v1.endpoints import (
    tako as tako_v1,
)
from app.presentation.compat import CORSMiddleware, FastAPI
from app.presentation.knowledge_integration import KnowledgeIntegration
from app.rh_actions.api import router as rh_actions_router
from app.rh_actions.contracts import ActionError
from app.rh_actions.worker import embedded_worker


def create_application(knowledge_integration: KnowledgeIntegration | None = None) -> FastAPI:
    """Instancia e configura a aplicacao FastAPI do VytAI totalmente configurada.

    Retorna:
        FastAPI: Instancia ASGI da API do VytAI totalmente configurada.
    """

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        with embedded_worker():
            yield

    app = FastAPI(
        lifespan=lifespan,
        title="VytAI API - Gestao de Riscos Psicossociais (NR-1)",
        description=(
            "Digital Worker de Gestao de Riscos Psicossociais (NR-1 / Portaria MTE nº 1.419/2024) "
            "para o RH. Converge Challenge | Time Booleanas."
        ),
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    from fastapi.responses import JSONResponse
    from sqlalchemy.exc import IntegrityError, SQLAlchemyError

    @app.exception_handler(SQLAlchemyError)
    async def database_failure(request: Request, exc: SQLAlchemyError) -> JSONResponse:
        conflict = isinstance(exc, IntegrityError)
        return JSONResponse(
            status_code=409 if conflict else 503,
            content={
                "detail": {
                    "code": "WRITE_CONFLICT" if conflict else "DATABASE_UNAVAILABLE",
                    "message": "Operacao nao confirmada; consulte o estado antes de repetir.",
                }
            },
        )

    @app.exception_handler(ActionError)
    async def action_failure(request: Request, exc: ActionError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status, content={"detail": {"code": exc.code, "message": exc.message}}
        )

    app.include_router(rh_actions_router, prefix="/api/v1/rh", tags=["Operacao do RH"])
    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "PULSO_CORS_ORIGINS",
            "http://localhost:4200,http://127.0.0.1:4200",
        ).split(",")
        if origin.strip()
    ]
    if "*" in allowed_origins:
        raise ValueError("PULSO_CORS_ORIGINS exige origens explicitas; wildcard nao permitido.")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # A esteira antiga tinha outro estado e regras: nao a executar por HTTP.
    @app.api_route("/fechamento", methods=["POST"], deprecated=True)
    @app.api_route("/areas/{area_id}", methods=["GET"], deprecated=True)
    @app.api_route("/casos/{caso_id}/decisao", methods=["POST"], deprecated=True)
    @app.api_route("/chat/query", methods=["POST"], deprecated=True)
    def legacy_route_retired() -> None:
        raise HTTPException(
            status_code=410,
            detail={
                "code": "LEGACY_ROUTE_RETIRED",
                "replacement": "/api/v1",
                "message": "Utilize a API v1; a esteira legada foi descontinuada.",
            },
        )

    app.include_router(health_v1.router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(areas_v1.router, prefix="/api/v1/areas", tags=["Areas & Sinais"])
    app.include_router(risk_cards_v1.router, prefix="/api/v1/risk-cards", tags=["Cards de Atencao"])
    app.include_router(pgr_v1.router, prefix="/api/v1/pgr", tags=["PGR / NR-1"])
    app.include_router(chat_v1.router, prefix="/api/v1/chat", tags=["Chat do Agente"])
    app.include_router(closing_v1.router, prefix="/api/v1/fechamento", tags=["Fechamento"])
    app.include_router(tako_v1.router, prefix="/api/v1/integrations/tako", tags=["Integracao Tako"])

    from app.presentation.knowledge_integration import unavailable_router

    app.state.knowledge_integration = knowledge_integration
    app.include_router(
        knowledge_integration.router if knowledge_integration else unavailable_router(),
        prefix="/api/v1/conhecimento",
        tags=["Conhecimento"],
    )
    return app


def _integracao_documental() -> KnowledgeIntegration:
    """Frente documental: router /conhecimento + servicos por requisicao (Postgres/RLS)."""
    from app.knowledge.api import router as router_conhecimento
    from app.knowledge.integration import criar_servicos_documentais

    return KnowledgeIntegration(router=router_conhecimento, factory=criar_servicos_documentais)


app = create_application(_integracao_documental())
