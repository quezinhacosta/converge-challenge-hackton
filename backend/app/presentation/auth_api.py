"""Configuracao publica e descoberta de empresas; autorizacao continua no servidor."""

import base64
import json
import os
import re
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import text

from app.application.contracts.identity import ContextoAutorizado
from app.infrastructure.auth.context import bearer, verify_token
from app.infrastructure.persistence.database import get_engine
from app.presentation.security import runtime_context

router = APIRouter()


def is_public_key(key: str, url: str) -> bool:
    if key.startswith("sb_publishable_"):
        return True
    try:
        parts = key.split(".")
        if len(parts) != 3:
            return False
        body = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
        project = url.removeprefix("https://").split(".")[0]
        return isinstance(body, dict) and body.get("role") == "anon" and body.get("ref") == project
    except (ValueError, TypeError, UnicodeError):
        return False


@router.get("/config")
def public_config() -> dict:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    if not re.fullmatch(r"https://[a-z0-9]+\.supabase\.co", url) or not key.startswith(
        "sb_publishable_"
    ):
        raise HTTPException(503, "Login ainda nao configurado no servidor.")
    return {"url": url, "publishableKey": key}


@router.get("/empresas")
def companies(credential: HTTPAuthorizationCredentials | None = Depends(bearer)) -> list[dict]:
    if credential is None:
        raise HTTPException(401, "Autenticacao obrigatoria.")
    claims = verify_token(credential.credentials)
    try:
        user = UUID(claims["sub"])
    except (ValueError, KeyError, TypeError):
        raise HTTPException(401, "Identidade invalida.") from None
    with get_engine().connect() as conn:
        conn.execute(text("SELECT set_config('vytai.usuario_id',:user,true)"), {"user": str(user)})
        rows = (
            conn.execute(
                text(
                    "SELECT e.id,e.nome,m.papeis FROM empresa_usuario m JOIN empresa e ON e.id=m.empresa_id WHERE m.usuario_id=:user AND m.ativo AND 'RH'=ANY(m.papeis) ORDER BY e.nome,e.id"
                ),
                {"user": user},
            )
            .mappings()
            .all()
        )
    return [{"id": str(r["id"]), "nome": r["nome"], "papeis": r["papeis"]} for r in rows]


@router.get("/context")
def current_context(ctx: ContextoAutorizado | None = Depends(runtime_context)) -> dict:
    """Contexto validado pelo backend; modo demo continua sob a trava de security.py."""
    if ctx is None:
        return {
            "empresa": {"id": "empresa_demo", "nome": "Empresa Fictícia S.A. (Demo)", "papeis": ["RH"]},
            "demo": True,
        }
    with get_engine().connect() as conn:
        conn.execute(
            text("SELECT set_config('vytai.empresa_id',:e,true)"), {"e": str(ctx.empresa_id)}
        )
        row = conn.execute(
            text(
                "SELECT e.nome FROM empresa e JOIN empresa_usuario m ON m.empresa_id=e.id WHERE e.id=:e AND m.usuario_id=:u AND m.ativo AND 'RH'=ANY(m.papeis)"
            ),
            {"e": ctx.empresa_id, "u": ctx.usuario_id},
        ).first()
    if row is None:
        raise HTTPException(403, "Vinculo RH inativo.")
    return {
        "empresa": {"id": str(ctx.empresa_id), "nome": row[0], "papeis": sorted(ctx.papeis)},
        "demo": os.getenv("VYTAI_MODE", "production") == "demo"
        and ctx.request_id.startswith("demo-"),
    }
