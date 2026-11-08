"""Ciclo do digital worker no PostgreSQL real: demo -> fechamento -> propostas -> memoria."""

import os
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, select, text
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.digital_worker.ciclo import executar_ciclo
from app.digital_worker.demo import EMPRESA_DEMO, USUARIO_DEMO, preparar_demo
from app.infrastructure.persistence.repositories import RepositoryBundle
from app.knowledge.integration import criar_servicos_documentais
from app.presentation.deps import PulsoAppContainer
from app.rh_actions import tables as t
from app.rh_actions.service import ActionService
from tests.integration.test_postgres_foundation import URL, scope
from tests.integration.test_postgres_foundation import engine as engine

pytestmark = pytest.mark.skipif(
    not os.getenv("VYTAI_TEST_DATABASE_URL"), reason="PostgreSQL de teste nao configurado"
)
CTX = ContextoAutorizado(EMPRESA_DEMO, USUARIO_DEMO, frozenset({"RH"}), frozenset({"RH"}), "t")


def _ciclo(engine: Any, canal: str | None = None) -> dict[str, Any]:
    with Session(engine) as session, session.begin():
        scope(session, EMPRESA_DEMO)
        conhecimento = criar_servicos_documentais(CTX, session)
        container = PulsoAppContainer(
            RepositoryBundle(session, EMPRESA_DEMO),
            seed=False,
            context=CTX,
            session=session,
            knowledge=conhecimento,
        )
        return executar_ciclo(
            CTX, container, conhecimento, ActionService(session, CTX), canal_slack=canal
        ).como_dict()


def test_ciclo_prepara_propostas_sem_duplicar_e_respeita_compliance(engine):
    primeira = preparar_demo(engine)
    assert preparar_demo(engine)["novos"] == 0  # idempotente
    assert primeira["empresa"] == EMPRESA_DEMO

    r1 = _ciclo(engine, canal="C0DEMO123")
    assert r1["areasAnalisadas"] >= 5 and r1["cardsAbertos"] >= 1
    preparadas = [c for c in r1["cards"] if c["resultado"] == "PROPOSTA_PREPARADA"]
    assert preparadas, r1["cards"]
    vermelho = next(c for c in preparadas if c["nivel"] == "VERMELHO")
    assert vermelho["avisoSlack"] is True
    assert vermelho["temAcaoDaEmpresa"] is True  # achou o Programa Cuidar / canal na base
    assert all(
        c["resultado"] != "PROPOSTA_PREPARADA" for c in r1["cards"] if c["fator"] == "ASSEDIO"
    )

    r2 = _ciclo(engine, canal="C0DEMO123")
    assert {c["intervencaoId"] for c in r2["cards"] if c["intervencaoId"]} == {
        c["intervencaoId"] for c in r1["cards"] if c["intervencaoId"]
    }
    assert all(c["resultado"] != "PROPOSTA_PREPARADA" for c in r2["cards"])

    with Session(engine) as session, session.begin():
        scope(session, EMPRESA_DEMO)
        acoes = session.execute(
            select(t.actions.c.status, t.actions.c.payload).where(
                t.actions.c.empresa_id == EMPRESA_DEMO
            )
        ).all()
        # Nada executa sozinho: tudo aguarda a aprovacao do RH.
        assert acoes and {a.status for a in acoes} == {"PENDING"}
        objetivo = session.execute(
            select(t.interventions.c.objective).where(
                t.interventions.c.id == vermelho["intervencaoId"]
            )
        ).scalar_one()
        assert "A empresa já oferece" in objetivo and "Fontes:" in objetivo


def test_demo_sem_login_e_decisao_vira_memoria(engine, monkeypatch):
    preparar_demo(engine)
    app_engine = create_engine(URL)

    @event.listens_for(app_engine, "connect")
    def _papel(dbapi_connection: Any, _: Any) -> None:
        with dbapi_connection.cursor() as cursor:
            cursor.execute("SET ROLE vytai_app")
        dbapi_connection.commit()

    import app.presentation.security as security
    from app.presentation.main import _integracao_documental, create_application

    monkeypatch.setattr(security, "get_engine", lambda: app_engine)
    monkeypatch.setenv("VYTAI_MODE", "demo")
    monkeypatch.setenv("VYTAI_DEMO_EMPRESA_ID", str(EMPRESA_DEMO))
    monkeypatch.setenv("VYTAI_DEMO_USUARIO_ID", str(USUARIO_DEMO))
    monkeypatch.setenv("PULSO_LLM_ENABLED", "false")
    with TestClient(create_application(_integracao_documental())) as client:
        status = client.get("/api/v1/conhecimento/status")
        assert status.status_code == 200 and status.json()["publicados"] >= 5
        ciclo = client.post("/api/v1/worker/ciclo")
        assert ciclo.status_code == 200, ciclo.text
        card = next(c for c in ciclo.json()["cards"] if c["fator"] != "ASSEDIO")
        decisao = client.post(
            f"/api/v1/risk-cards/{card['cardId']}/resolve",
            json={
                "actionType": "APROVAR_PGR",
                "reviewerName": "RH",
                "responsiblePerson": "Lideranca da area",
                "deadlineDays": 60,
            },
        )
        assert decisao.status_code in (200, 201), decisao.text
        busca = client.post(
            "/api/v1/conhecimento/buscar",
            json={"texto": f"decisao do RH {card['area']}", "categorias": ["PLANO_ACAO_ANTERIOR"]},
        )
        titulos = [x["titulo"] for x in busca.json()["trechos"]]
        assert any(t.startswith("Decisao ") and card["area"] in t for t in titulos), titulos
    app_engine.dispose()
    with Session(engine) as session, session.begin():
        auditoria = session.execute(
            text("SELECT count(*) FROM auditoria WHERE recurso_id=:c"), {"c": card["cardId"]}
        ).scalar_one()
        assert auditoria == 1
