"""Dependencias request-scoped: identidade e unidade de trabalho compartilhadas."""

import os
from collections.abc import Iterator

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.infrastructure.auth.context import bearer, get_authorized_context
from app.infrastructure.persistence.database import get_engine


def runtime_context(
    credential: HTTPAuthorizationCredentials | None = Depends(bearer),
    empresa: str | None = Header(default=None, alias="X-Empresa-Id"),
) -> ContextoAutorizado | None:
    if os.getenv("VYTAI_MODE", "production") == "demo" and credential is None:
        return None
    return get_authorized_context(credential, empresa)


def request_session(
    ctx: ContextoAutorizado | None = Depends(runtime_context),
) -> Iterator[Session | None]:
    if ctx is None:
        yield None
        return
    with Session(get_engine()) as session:
        with session.begin():
            session.execute(
                text("SELECT set_config('vytai.empresa_id', :empresa, true)"),
                {"empresa": str(ctx.empresa_id)},
            )
            yield session


def require_authorized_context(
    ctx: ContextoAutorizado | None = Depends(runtime_context),
) -> ContextoAutorizado:
    from fastapi import HTTPException

    if ctx is None:
        raise HTTPException(401, "Conhecimento exige identidade autenticada.")
    return ctx
