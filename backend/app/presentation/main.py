"""Fabrica da aplicacao FastAPI e ponto de entrada da API do PayTrust."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.v1.endpoints import absences, health, payroll


def create_application() -> FastAPI:
    """Instancia e configura a aplicacao FastAPI do PayTrust.

    Retorna:
        FastAPI: Instancia ASGI da aplicacao totalmente configurada.
    """
    app = FastAPI(
        title="PayTrust API",
        description=(
            "Digital Worker de Governanca, Anti-Fraude e Afastamentos na Folha de Pagamento. "
            "Powered by Tako / Converge Challenge."
        ),
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
    app.include_router(payroll.router, prefix="/api/v1/payroll", tags=["Auditoria de Folha"])
    app.include_router(absences.router, prefix="/api/v1/absences", tags=["Afastamentos e Compliance"])

    return app


app = create_application()
