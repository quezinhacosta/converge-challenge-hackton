"""Gates de contratos, seguranca e persistencia sem servicos externos."""

from datetime import UTC, date, datetime
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.application.contracts.indicators import IndicadoresArea, PeriodoAnalise
from app.domain.entities.area import Area
from app.domain.services.indicator_calculator import calculate_change
from app.infrastructure.auth import context as auth
from app.infrastructure.persistence.repositories import RepositoryBundle, metadata
from app.presentation.deps import PulsoAppContainer
from app.presentation.main import create_application


def test_missing_and_zero_baseline_are_not_normal():
    missing = calculate_change("horas", None, Decimal(10), "h")
    zero = calculate_change("horas", Decimal(4), Decimal(0), "h")
    assert missing.qualidade == "INDISPONIVEL" and missing.delta_percentual is None
    assert zero.qualidade == "SEM_BASELINE" and zero.delta_absoluto == 4
    assert zero.delta_percentual is None
    valid = calculate_change("horas", Decimal(15), Decimal(10), "h")
    assert valid.delta_percentual == 50


def snapshot(**kwargs):
    args = dict(
        snapshot_id=uuid4(),
        empresa_id=uuid4(),
        area_id="a",
        periodo=PeriodoAnalise(inicio=date(2026, 10, 1), fim=date(2026, 11, 1)),
        calculado_em=datetime.now(UTC),
        estado="DADOS_INSUFICIENTES",
        quorum_ok=None,
        versao_calculo="1",
        origem_dados="REAL",
    )
    return IndicadoresArea(**(args | kwargs))


def test_snapshot_immutable_and_no_fake_green():
    value = snapshot()
    with pytest.raises(ValidationError):
        value.score = Decimal(10)
    with pytest.raises(ValidationError):
        snapshot(score=Decimal(0), nivel="VERDE")
    with pytest.raises(ValidationError):
        snapshot(estado="ELEGIVEL", quorum_ok=True, score=Decimal("NaN"))


def test_bad_period_rejected():
    with pytest.raises(ValidationError):
        PeriodoAnalise(inicio=date(2026, 11, 1), fim=date(2026, 10, 1))


def test_production_api_fails_closed(monkeypatch):
    monkeypatch.setenv("VYTAI_MODE", "production")
    client = TestClient(create_application())
    assert client.get("/api/v1/areas").status_code == 401
    assert client.get("/api/v1/risk-cards/active").status_code == 401
    assert client.post("/api/v1/fechamento").status_code == 401
    assert client.get("/api/v1/health").status_code == 200
    assert client.post("/fechamento").status_code == 410


def test_cors_is_explicit(monkeypatch):
    monkeypatch.setenv("PULSO_CORS_ORIGINS", "https://vytai.vercel.app")
    client = TestClient(create_application())
    headers = {"Origin": "https://attacker.invalid", "Access-Control-Request-Method": "GET"}
    assert client.options("/api/v1/areas", headers=headers).status_code == 400
    headers["Origin"] = "https://vytai.vercel.app"
    assert client.options("/api/v1/areas", headers=headers).status_code == 200
    monkeypatch.setenv("PULSO_CORS_ORIGINS", "*")
    with pytest.raises(ValueError):
        create_application()


def test_jwt_signature_issuer_audience_and_expiry(monkeypatch):
    key = ec.generate_private_key(ec.SECP256R1())
    monkeypatch.setenv("SUPABASE_JWT_ISSUER", "https://example.supabase.co/auth/v1")
    client = SimpleNamespace(
        get_signing_key_from_jwt=lambda _: SimpleNamespace(key=key.public_key())
    )
    monkeypatch.setattr(auth, "jwks_client", lambda _: client)
    now = int(datetime.now(UTC).timestamp())
    claims = dict(
        sub=str(uuid4()),
        iat=now,
        exp=now + 60,
        iss="https://example.supabase.co/auth/v1",
        aud="authenticated",
    )

    def token(values):
        return jwt.encode(values, key, algorithm="ES256")

    assert auth.verify_token(token(claims))["sub"] == claims["sub"]
    for change in [dict(aud="other"), dict(iss="https://evil.invalid"), dict(exp=now - 60)]:
        with pytest.raises(Exception) as error:
            auth.verify_token(token(claims | change))
        assert error.value.status_code == 401
    forged = jwt.encode(claims, "untrusted-test-secret-longer-than-32-bytes", algorithm="HS256")
    with pytest.raises(Exception) as error:
        auth.verify_token(forged)
    assert error.value.status_code == 401


def test_repository_persists_and_filters_tenant(tmp_path):
    # SQLite e somente um test double; migrations/RLS sao testados em PostgreSQL na CI.
    engine = create_engine("sqlite:///" + str(tmp_path / "repositories.db"))
    metadata.create_all(engine)
    a, b = uuid4(), uuid4()
    with Session(engine) as session, session.begin():
        RepositoryBundle(session, a).area_repo.save(
            Area(id="same", name="A", headcount=10, manager_name="RH")
        )
        RepositoryBundle(session, b).area_repo.save(
            Area(id="same", name="B", headcount=6, manager_name="RH")
        )
    engine.dispose()
    with Session(engine) as session:
        assert RepositoryBundle(session, a).area_repo.get_by_id("same").name == "A"
        assert RepositoryBundle(session, b).area_repo.list_all()[0].name == "B"
    with pytest.raises(RuntimeError):
        with Session(engine) as session, session.begin():
            RepositoryBundle(session, a).area_repo.save(
                Area(id="rollback", name="X", headcount=10, manager_name="RH")
            )
            raise RuntimeError("rollback")
    with Session(engine) as session:
        assert RepositoryBundle(session, a).area_repo.get_by_id("rollback") is None
    engine.dispose()


def test_card_citations_roundtrip():
    from app.application.dtos.risk_card_dto import RiskCardDTO

    container = PulsoAppContainer()
    card = container.risk_card_repo.list_all()[0]
    card.fontes_documentais = [
        dict(
            ref="C1",
            documento_id=uuid4(),
            versao_id=uuid4(),
            trecho_id=uuid4(),
            titulo="Politica",
            versao_rotulo="1",
            trecho="Fonte",
        )
    ]
    card.evidencia_documental_suficiente = True
    result = RiskCardDTO.from_entity(card).model_dump(mode="json", by_alias=True)
    assert result["fontesDocumentais"][0]["ref"] == "C1"
    assert result["evidenciaDocumentalSuficiente"] is True


def test_missing_history_does_not_create_card():
    container = PulsoAppContainer(seed=False)
    container.area_repo.save(Area(id="empty", name="Area", headcount=10, manager_name="RH"))
    result = container.run_analysis_uc.execute("empty")
    assert result["riskLevel"] is None
    assert result["analysisStatus"] == "DADOS_INSUFICIENTES"
    assert result["cardId"] is None


def test_commit_error_is_not_successful_http(monkeypatch):
    from fastapi import Depends
    from sqlalchemy.exc import OperationalError

    app = create_application()

    def failing_uow():
        yield None
        raise OperationalError("commit", {}, Exception("test"))

    @app.post("/test-transaction")
    def route(session=Depends(failing_uow, scope="function")):
        return {"ok": True}

    client = TestClient(app, raise_server_exceptions=False)
    result = client.post("/test-transaction")
    assert result.status_code == 503
    assert result.json()["detail"]["code"] == "DATABASE_UNAVAILABLE"
