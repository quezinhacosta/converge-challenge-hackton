"""Dependencias request-scoped: identidade e unidade de trabalho compartilhadas."""

import os
from collections.abc import Iterator
from uuid import UUID, uuid4

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
        return contexto_demo()
    return get_authorized_context(credential, empresa)


def contexto_demo() -> ContextoAutorizado | None:
    """Modo demo: RH ficticio de uma empresa sintetica (python -m app.digital_worker.demo).

    So vale com VYTAI_MODE=demo e as duas variaveis definidas; sem elas, demo segue anonimo.
    Nunca usar com dados reais: qualquer visitante age como esse RH.
    """
    empresa = os.getenv("VYTAI_DEMO_EMPRESA_ID", "").strip()
    usuario = os.getenv("VYTAI_DEMO_USUARIO_ID", "").strip()
    if not empresa or not usuario:
        return None
    from app.digital_worker.identidade_demo import EMPRESA_DEMO, USUARIO_DEMO

    if UUID(empresa) != EMPRESA_DEMO or UUID(usuario) != USUARIO_DEMO:
        raise RuntimeError(
            "Modo demo so aceita a empresa sintetica de app.digital_worker.demo; "
            "nunca aponte VYTAI_DEMO_* para uma empresa real."
        )
    return ContextoAutorizado(
        UUID(empresa), UUID(usuario), frozenset({"RH"}), frozenset({"RH"}), f"demo-{uuid4()}"
    )


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
