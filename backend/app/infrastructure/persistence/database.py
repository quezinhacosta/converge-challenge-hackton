"""Conexoes PostgreSQL apenas; migrations nunca executam no startup da API."""

import os
from functools import lru_cache
from typing import Any

from fastapi import HTTPException
from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine


@lru_cache(maxsize=1)
def get_engine() -> Engine:
    url = os.getenv("DATABASE_URL", "")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    if not url.startswith("postgresql+psycopg://"):
        raise HTTPException(503, "Persistencia PostgreSQL nao configurada.")
    engine = create_engine(
        url,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
        hide_parameters=True,
        # Producao/Supabase: require (padrao). So desenvolvimento local usa DATABASE_SSLMODE=disable.
        connect_args={"sslmode": os.getenv("DATABASE_SSLMODE", "require")},
    )

    @event.listens_for(engine, "connect")
    def restrict_role(dbapi_connection: Any, connection_record: Any) -> None:
        # Conta administrativa nunca executa consultas de negocio com bypass de RLS.
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET ROLE vytai_app")
        dbapi_connection.commit()

    return engine
