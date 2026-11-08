import os
from contextlib import contextmanager
from datetime import timedelta
from uuid import uuid4

import pytest
from sqlalchemy import text, update
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.domain.entities.area import Area
from app.infrastructure.persistence.repositories import RepositoryBundle
from app.rh_actions import tables as t
from app.rh_actions.connectors import DeliveryError
from app.rh_actions.contracts import (
    ActionError,
    PrepareAction,
    PrepareIntervention,
    RecordEvidence,
    ReminderPolicy,
    SlackPayload,
    TaskPayload,
)
from app.rh_actions.service import ActionService, utcnow
from app.rh_actions.worker import ActionWorker
from tests.integration.test_postgres_foundation import engine as engine
from tests.integration.test_postgres_foundation import scope

pytestmark = pytest.mark.skipif(
    not os.getenv("VYTAI_TEST_DATABASE_URL"), reason="PostgreSQL de teste nao configurado"
)


class FakeConnector:
    def __init__(self):
        self.calls = []
        self.error = None

    def send(self, *args):
        self.calls.append(args)
        if self.error:
            raise self.error
        return {"provider": "TEST", "reference": "confirmed"}


@pytest.fixture
def setup(engine):
    company, user = uuid4(), uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO empresa(id,nome) VALUES(:id,'RH teste')"), {"id": company})
        conn.execute(
            text(
                "INSERT INTO empresa_usuario(empresa_id,usuario_id,papeis,ativo) VALUES(:company,:user,ARRAY['RH'],true)"
            ),
            {"company": company, "user": user},
        )
    ctx = ContextoAutorizado(company, user, frozenset({"RH"}), frozenset({"RH"}), "test")

    @contextmanager
    def service(context=ctx):
        with Session(engine) as session, session.begin():
            scope(session, context.empresa_id)
            yield ActionService(session, context)

    with service() as svc:
        RepositoryBundle(svc.session, company).area_repo.save(
            Area(id="area", name="Setor", headcount=10, manager_name="RH")
        )
    connector = FakeConnector()
    worker = ActionWorker(lambda: Session(engine), ctx, connector)
    return ctx, service, worker, connector


def prepare(service, reminders=False):
    request = PrepareIntervention(
        areaId="area",
        title="Acompanhar carga do setor",
        objective="Reduzir a sobrecarga por meio de acompanhamento do RH.",
        firstTask=TaskPayload(
            title="Reunir evidências de execução",
            dueAt=utcnow() + timedelta(days=15),
            reminders=ReminderPolicy(channel="C123456") if reminders else None,
        ),
    )
    with service() as svc:
        item = svc.prepare_intervention(request, "intervention-test")
        assert svc.prepare_intervention(request, "intervention-test")["id"] == item["id"]
    return item


def test_task_requires_approval_evidence_and_cancels_reminders(setup):
    ctx, service, worker, connector = setup
    item = prepare(service, True)
    action = item["actions"][0]
    assert worker.run_once()["processed"] is False
    with service() as svc:
        with pytest.raises(ActionError, match="STALE_APPROVAL"):
            svc.approve(action["id"], "f" * 64)
        svc.approve(action["id"], action["digest"])
        with pytest.raises(ActionError, match="ALREADY_REVIEWED"):
            svc.approve(action["id"], action["digest"])
    assert worker.run_once()["processed"]
    assert worker.run_once()["processed"] is False
    assert connector.calls == []
    with service() as svc:
        current = svc.intervention(item["id"])
        assert current["actions"][0]["status"] == "SUCCEEDED"
        assert len(current["tasks"]) == 1
        children = [a for a in current["actions"] if a["authorization_parent_id"]]
        assert len(children) == 2 and all(a["status"] == "QUEUED" for a in children)
        task = current["tasks"][0]
        with pytest.raises(ActionError):
            svc.complete_task(task["id"])
        svc.record_evidence(
            task["id"], RecordEvidence(description="RH registrou a realização da reunião.")
        )
        svc.complete_task(task["id"])
        assert all(
            a["status"] == "CANCELLED"
            for a in svc.intervention(item["id"])["actions"]
            if a["authorization_parent_id"]
        )


def test_uncertain_delivery_never_automatically_repeats(setup):
    _, service, worker, connector = setup
    item = prepare(service)
    with service() as svc:
        action = svc.prepare_action(
            item["id"],
            PrepareAction(payload=SlackPayload(channel="C123456"), notBefore=utcnow()),
            "slack-test",
        )
        svc.approve(action["id"], action["digest"])
    connector.error = DeliveryError("SLACK_OUTCOME_UNKNOWN", uncertain=True)
    worker.run_once()
    worker.run_once()
    assert len(connector.calls) == 1
    with service() as svc:
        assert svc.action(action["id"])["status"] == "UNKNOWN"
        with pytest.raises(ActionError):
            svc.retry(action["id"])


def test_revoked_approver_and_tenant_isolation(setup, engine):
    ctx, service, worker, connector = setup
    item = prepare(service)
    action = item["actions"][0]
    other = ContextoAutorizado(uuid4(), uuid4(), frozenset({"RH"}), frozenset({"RH"}), "other")
    with service(other) as svc:
        assert svc.list_interventions() == []
        with pytest.raises(ActionError):
            svc.action(action["id"])
    with service() as svc:
        svc.approve(action["id"], action["digest"])
    # Worker separado do aprovador para testar revogação no momento da execução.
    actor = uuid4()
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO empresa_usuario(empresa_id,usuario_id,papeis,ativo) VALUES(:company,:user,ARRAY['RH'],true)"
            ),
            {"company": ctx.empresa_id, "user": actor},
        )
        conn.execute(
            text(
                "UPDATE empresa_usuario SET ativo=false WHERE empresa_id=:company AND usuario_id=:user"
            ),
            {"company": ctx.empresa_id, "user": ctx.usuario_id},
        )
    worker.ctx = ContextoAutorizado(
        ctx.empresa_id, actor, ctx.papeis, ctx.escopos_permitidos, "worker"
    )
    worker.run_once()
    with service() as svc:
        assert svc.action(action["id"])["status"] == "BLOCKED"
    assert connector.calls == []


def test_claim_crash_recovers_slack_as_unknown(setup):
    _, service, worker, connector = setup
    item = prepare(service)
    with service() as svc:
        action = svc.prepare_action(
            item["id"],
            PrepareAction(payload=SlackPayload(channel="C123456"), notBefore=utcnow()),
            "lease-test",
        )
        svc.approve(action["id"], action["digest"])
    row = worker.claim()
    assert row and row["id"] == action["id"]
    with service() as svc:
        svc.session.execute(
            update(t.actions)
            .where(t.actions.c.id == action["id"])
            .values(lease_until=utcnow() - timedelta(seconds=1))
        )
    assert worker.reap() == 1
    worker.run_once()
    with service() as svc:
        assert svc.action(action["id"])["status"] == "UNKNOWN"
    assert connector.calls == []


def test_http_review_contract_and_human_confirmation(setup):
    from fastapi.testclient import TestClient

    from app.presentation.main import create_application
    from app.presentation.security import request_session, require_authorized_context

    ctx, service, worker, connector = setup
    app = create_application()
    app.dependency_overrides[require_authorized_context] = lambda: ctx

    def db():
        with service() as svc:
            yield svc.session

    app.dependency_overrides[request_session] = db
    with TestClient(app) as client:
        body = {
            "areaId": "area",
            "title": "Plano de acompanhamento",
            "objective": "Acompanhar evidências do setor em conjunto com o RH.",
            "firstTask": {
                "kind": "TASK",
                "title": "Verificar execução da medida",
                "dueAt": (utcnow() + timedelta(days=15)).isoformat(),
            },
        }
        response = client.post(
            "/api/v1/rh/intervencoes", json=body, headers={"Idempotency-Key": "http-test-key"}
        )
        assert response.status_code == 201, response.text
        item = response.json()
        action = item["actions"][0]
        assert action["status"] == "PENDING" and "dueAt" in action["preview"]
        assert (
            client.post(
                f"/api/v1/rh/acoes/{action['id']}/aprovar", json={"expectedDigest": "0" * 64}
            ).status_code
            == 409
        )
        assert (
            client.post(
                f"/api/v1/rh/acoes/{action['id']}/aprovar",
                json={"expectedDigest": action["digest"]},
            ).status_code
            == 200
        )
        assert connector.calls == []
        worker.run_once()
        result = client.get(f"/api/v1/rh/intervencoes/{item['id']}").json()
        assert result["actions"][0]["status"] == "SUCCEEDED" and len(result["tasks"]) == 1
        assert (
            client.post(
                f"/api/v1/rh/tarefas/{result['tasks'][0]['id']}/concluir", json={}
            ).status_code
            == 409
        )


def test_parallel_claims_execute_once(setup):
    from concurrent.futures import ThreadPoolExecutor

    _, service, worker, connector = setup
    item = prepare(service)
    action = item["actions"][0]
    with service() as svc:
        svc.approve(action["id"], action["digest"])
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(lambda _: worker.claim(), range(2)))
    claimed = [r for r in results if r]
    assert len(claimed) == 1
    worker.finish(claimed[0])
    with service() as svc:
        assert len(svc.intervention(item["id"])["tasks"]) == 1
