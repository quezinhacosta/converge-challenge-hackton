"""Fabrica e ponto de entrada da aplicacao FastAPI do Pulso."""

import os

from app.presentation.api.v1.endpoints import areas, chat, closing, health, pgr, risk_cards
from app.presentation.compat import CORSMiddleware, FastAPI


def create_application() -> FastAPI:
    """Instancia e configura a aplicacao FastAPI do Pulso.

    Retorna:
        FastAPI: Instancia ASGI da API do Pulso totalmente configurada.
    """
    app = FastAPI(
        title="Pulso API",
        description=(
            "Digital Worker de Gestao de Riscos Psicossociais (NR-1) para o RH. "
            "Converge Challenge powered by Tako | Time Booleanas."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # Sem autenticacao ainda: libera so as origens do frontend (padrao: Angular local).
    allowed_origins = [
        origin.strip()
        for origin in os.getenv(
            "PULSO_CORS_ORIGINS", "http://localhost:4200,http://127.0.0.1:4200"
        ).split(",")
        if origin.strip()
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST"],
        allow_headers=["Content-Type"],
    )

    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(areas.router, prefix="/api/v1/areas", tags=["Areas & Sinais"])
    app.include_router(risk_cards.router, prefix="/api/v1/risk-cards", tags=["Cards de Atencao"])
    app.include_router(pgr.router, prefix="/api/v1/pgr", tags=["PGR / NR-1"])
    app.include_router(chat.router, prefix="/api/v1/chat", tags=["Chat do Agente"])
    app.include_router(closing.router, prefix="/api/v1/fechamento", tags=["Fechamento"])

    return app


app = create_application()
