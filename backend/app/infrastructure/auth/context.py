"""Auth Supabase assimetrica + membership no servidor. Sem fallback anonimo produtivo."""

import os
from functools import lru_cache
from uuid import UUID, uuid4

import jwt
from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import text

from app.application.contracts.identity import ContextoAutorizado

bearer = HTTPBearer(auto_error=False)


@lru_cache(maxsize=8)
def jwks_client(issuer: str) -> jwt.PyJWKClient:
    return jwt.PyJWKClient(issuer.rstrip("/") + "/.well-known/jwks.json", timeout=5)


def verify_token(token: str) -> dict:
    issuer = os.getenv("SUPABASE_JWT_ISSUER", "").rstrip("/")
    if not issuer.startswith("https://"):
        raise HTTPException(503, "Autenticacao nao configurada.")
    try:
        key = jwks_client(issuer).get_signing_key_from_jwt(token)
        return jwt.decode(
            token,
            key.key,
            algorithms=["ES256", "RS256"],
            audience="authenticated",
            issuer=issuer,
            options={"require": ["exp", "iat", "sub", "iss", "aud"]},
        )
    except jwt.PyJWKClientConnectionError:
        raise HTTPException(503, "Servico de autenticacao indisponivel.") from None
    except (jwt.PyJWTError, ValueError):
        raise HTTPException(401, "Token invalido.") from None


def get_authorized_context(
    credential: HTTPAuthorizationCredentials | None = Depends(bearer),
    empresa: str | None = Header(default=None, alias="X-Empresa-Id"),
) -> ContextoAutorizado:
    if credential is None:
        raise HTTPException(401, "Autenticacao obrigatoria.")
    claims = verify_token(credential.credentials)
    try:
        user_id = UUID(claims["sub"])
        selected = UUID(empresa) if empresa else None
    except (ValueError, KeyError, TypeError):
        raise HTTPException(401, "Identidade invalida.") from None
    from app.infrastructure.persistence.database import get_engine

    with get_engine().connect() as conn:
        conn.execute(
            text("SELECT set_config('vytai.usuario_id',:user,true)"), {"user": str(user_id)}
        )
        rows = (
            conn.execute(
                text(
                    "SELECT empresa_id, papeis FROM empresa_usuario "
                    "WHERE usuario_id=:user AND ativo=true"
                ),
                {"user": user_id},
            )
            .mappings()
            .all()
        )
    rows = [r for r in rows if selected is None or r["empresa_id"] == selected]
    if len(rows) != 1:
        raise HTTPException(403, "Empresa nao autorizada ou selecao necessaria.")
    roles = frozenset(rows[0]["papeis"])
    scopes = frozenset({"RH", "RH_E_GESTORES"}) if "RH" in roles else frozenset()
    if not scopes:
        raise HTTPException(403, "Perfil sem acesso ao MVP.")
    return ContextoAutorizado(rows[0]["empresa_id"], user_id, roles, scopes, str(uuid4()))
