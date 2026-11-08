import os
from contextlib import contextmanager
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.application.contracts.identity import ContextoAutorizado
from tests.integration.test_postgres_foundation import engine as engine
from tests.integration.test_rh_actions_postgres import setup as setup

pytestmark = pytest.mark.skipif(
    not os.getenv("VYTAI_TEST_DATABASE_URL"), reason="PostgreSQL de teste nao configurado"
)


def test_memberships_are_scoped_to_verified_user_and_revocation(setup, engine, monkeypatch):
    import app.presentation.auth_api as auth
    from app.presentation.main import create_application

    ctx, _, _, _ = setup

    @contextmanager
    def connect():
        with engine.connect() as conn:
            conn.execute(text("SET LOCAL ROLE vytai_app"))
            yield conn

    class RuntimeEngine:
        def connect(self):
            return connect()

    monkeypatch.setattr(auth, "get_engine", lambda: RuntimeEngine())
    monkeypatch.setattr(
        auth,
        "verify_token",
        lambda _: {
            "sub": str(ctx.usuario_id),
            "user_metadata": {"papeis": ["RH"], "empresa_id": str(uuid4())},
        },
    )
    client = TestClient(create_application())
    assert client.get("/api/v1/auth/empresas").status_code == 401
    result = client.get("/api/v1/auth/empresas", headers={"Authorization": "Bearer test"})
    assert result.status_code == 200, result.text
    assert result.json() == [{"id": str(ctx.empresa_id), "nome": "RH teste", "papeis": ["RH"]}]
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE empresa_usuario SET ativo=false WHERE empresa_id=:e AND usuario_id=:u"),
            {"e": ctx.empresa_id, "u": ctx.usuario_id},
        )
    assert (
        client.get("/api/v1/auth/empresas", headers={"Authorization": "Bearer test"}).json() == []
    )


def test_demo_context_comes_only_from_backend_identity(setup, engine, monkeypatch):
    import app.presentation.auth_api as auth
    from app.presentation.main import create_application
    from app.presentation.security import runtime_context

    ctx, _, _, _ = setup
    demo = ContextoAutorizado(
        ctx.empresa_id, ctx.usuario_id, ctx.papeis, ctx.escopos_permitidos, "demo-test"
    )
    app = create_application()
    app.dependency_overrides[runtime_context] = lambda: demo
    monkeypatch.setattr(auth, "get_engine", lambda: engine)
    monkeypatch.setenv("VYTAI_MODE", "demo")
    response = TestClient(app).get("/api/v1/auth/context")
    assert response.status_code == 200 and response.json()["demo"] is True
    assert response.json()["empresa"]["id"] == str(ctx.empresa_id)
    monkeypatch.setenv("VYTAI_MODE", "production")
    assert TestClient(app).get("/api/v1/auth/context").json()["demo"] is False
