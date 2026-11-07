"""Fabrica e ponto de entrada da aplicacao FastAPI do vitAI (Pulso).

Disponibiliza:
1. Endpoints diretos da Pessoa B (/fechamento, /areas/{id}, /casos/{id}/decisao, /chat/query).
2. Endpoints modulares da API v1 (/api/v1/health, /api/v1/areas, /api/v1/risk-cards, /api/v1/pgr, /api/v1/chat, /api/v1/fechamento).
"""

import os

from app.presentation.api.v1.endpoints import (
    areas as areas_v1,
    chat as chat_v1,
    closing as closing_v1,
    health as health_v1,
    pgr as pgr_v1,
    risk_cards as risk_cards_v1,
)
from app.presentation.compat import CORSMiddleware, FastAPI, status
from app.schemas import (
    AreaData,
    ChatQueryRequest,
    ChatQueryResponse,
    DecisaoRequest,
    DecisaoResponse,
    FechamentoSummaryResponse,
)
from app.main import (
    consultar_chat_copiloto,
    executar_fechamento_mensal,
    obter_dados_area,
    registrar_decisao_rh,
)


def create_application() -> FastAPI:
    """Instancia e configura a aplicacao FastAPI do vitAI totalmente configurada.

    Retorna:
        FastAPI: Instancia ASGI da API do vitAI totalmente configurada.
    """
    app = FastAPI(
        title="vitAI API - Gestao de Riscos Psicossociais (NR-1)",
        description=(
            "Digital Worker de Gestao de Riscos Psicossociais (NR-1 / Portaria MTE nº 1.419/2024) "
            "para o RH. Converge Challenge | Time Booleanas."
        ),
        version="0.2.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "PULSO_CORS_ORIGINS",
            "*,http://localhost:4200,http://127.0.0.1:4200,http://localhost:3000,http://127.0.0.1:3000",
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # -------------------------------------------------------------------------
    # Rotas Diretas da Pessoa B (Slack Bot e MCP)
    # -------------------------------------------------------------------------
    app.post(
        "/fechamento",
        response_model=FechamentoSummaryResponse,
        status_code=status.HTTP_200_OK,
        tags=["Pessoa B - Core Fechamento"],
    )(executar_fechamento_mensal)

    app.get(
        "/areas/{area_id}",
        response_model=AreaData,
        status_code=status.HTTP_200_OK,
        tags=["Pessoa B - Areas"],
    )(obter_dados_area)

    app.post(
        "/casos/{caso_id}/decisao",
        response_model=DecisaoResponse,
        status_code=status.HTTP_200_OK,
        tags=["Pessoa B - Deliberacao Humana"],
    )(registrar_decisao_rh)

    app.post(
        "/chat/query",
        response_model=ChatQueryResponse,
        status_code=status.HTTP_200_OK,
        tags=["Pessoa B - Copiloto Chat"],
    )(consultar_chat_copiloto)

    # -------------------------------------------------------------------------
    # Rotas Modulares da API v1
    # -------------------------------------------------------------------------
    app.include_router(health_v1.router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(areas_v1.router, prefix="/api/v1/areas", tags=["Areas & Sinais"])
    app.include_router(risk_cards_v1.router, prefix="/api/v1/risk-cards", tags=["Cards de Atencao"])
    app.include_router(pgr_v1.router, prefix="/api/v1/pgr", tags=["PGR / NR-1"])
    app.include_router(chat_v1.router, prefix="/api/v1/chat", tags=["Chat do Agente"])
    app.include_router(closing_v1.router, prefix="/api/v1/fechamento", tags=["Fechamento"])

    return app


app = create_application()
