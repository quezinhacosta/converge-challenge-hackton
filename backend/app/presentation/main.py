"""FastAPI application factory and server entrypoint for PayTrust."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.presentation.api.v1.endpoints import absences, health, payroll


def create_application() -> FastAPI:
    """Instantiate and configure the FastAPI application.

    Returns:
        FastAPI: Fully configured ASGI application instance.
    """
    app = FastAPI(
        title="PayTrust API",
        description=(
            "Digital Worker for Payroll Governance, Anti-Fraud, and Leaves. "
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
    app.include_router(payroll.router, prefix="/api/v1/payroll", tags=["Payroll Audit"])
    app.include_router(absences.router, prefix="/api/v1/absences", tags=["Absence & Compliance"])

    return app


app = create_application()
