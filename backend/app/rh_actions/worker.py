"""Worker duravel por empresa. Claim/commit -> chamada externa -> receipt/commit."""

import argparse
import os
import time
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from datetime import timedelta
from typing import Any
from uuid import UUID, uuid4, uuid5

from sqlalchemy import insert, select, text, update
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.infrastructure.persistence.database import get_engine
from app.rh_actions import tables as t
from app.rh_actions.connectors import Connectors, ConnectorSettings, DeliveryError
from app.rh_actions.contracts import ActionError, SlackPayload, TaskPayload
from app.rh_actions.service import PAYLOAD, ActionService, action_digest, action_preview, utcnow

MAX_ATTEMPTS = 5
LEASE_SECONDS = 120


class ActionWorker:
    def __init__(
        self, session_factory: Callable[[], Session], ctx: ContextoAutorizado, connectors: Any
    ):
        self.session_factory, self.ctx, self.connectors = session_factory, ctx, connectors

    @contextmanager
    def transaction(self) -> Iterator[Session]:
        with self.session_factory() as session, session.begin():
            session.execute(text("SET LOCAL ROLE vytai_app"))
            session.execute(
                text("SELECT set_config('vytai.empresa_id',:empresa,true)"),
                {"empresa": str(self.ctx.empresa_id)},
            )
            yield session

    def active_rh(self, session: Session, user: UUID) -> bool:
        return (
            session.execute(
                text(
                    "SELECT 1 FROM empresa_usuario WHERE empresa_id=:empresa "
                    "AND usuario_id=:user AND ativo AND 'RH'=ANY(papeis)"
                ),
                {"empresa": self.ctx.empresa_id, "user": user},
            ).first()
            is not None
        )

    def reap(self) -> int:
        now = utcnow()
        count = 0
        with self.transaction() as session:
            if not self.active_rh(session, self.ctx.usuario_id):
                raise ActionError(
                    403, "WORKER_PRINCIPAL_REVOKED", "Principal do worker sem vinculo ativo no RH."
                )
            rows = (
                session.execute(
                    select(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id,
                        t.actions.c.status == "RUNNING",
                        t.actions.c.lease_until < now,
                    )
                    .with_for_update(skip_locked=True)
                    .limit(100)
                )
                .mappings()
                .all()
            )
            service = ActionService(session, self.ctx)
            for row in rows:
                uncertain = row["kind"] == "SLACK" or (
                    row["kind"] == "CALENDAR" and row["attempts"] >= MAX_ATTEMPTS
                )
                status = (
                    "UNKNOWN"
                    if uncertain
                    else ("QUEUED" if row["attempts"] < MAX_ATTEMPTS else "FAILED")
                )
                session.execute(
                    update(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id, t.actions.c.id == row["id"]
                    )
                    .values(
                        status=status,
                        lease_until=None,
                        available_at=now,
                        error_code="LEASE_EXPIRED",
                        updated_at=now,
                    )
                )
                session.execute(
                    update(t.attempts)
                    .where(
                        t.attempts.c.empresa_id == self.ctx.empresa_id,
                        t.attempts.c.claim_token == row["claim_token"],
                        t.attempts.c.status == "STARTED",
                    )
                    .values(status="UNKNOWN", error_code="LEASE_EXPIRED", finished_at=now)
                )
                service.event(
                    row["intervention_id"], "EXECUTION_LEASE_EXPIRED", row["id"], {"state": status}
                )
                count += 1
        return count

    def claim(self) -> dict | None:
        now = utcnow()
        with self.transaction() as session:
            if not self.active_rh(session, self.ctx.usuario_id):
                raise ActionError(
                    403, "WORKER_PRINCIPAL_REVOKED", "Principal do worker sem vinculo ativo no RH."
                )
            selected_row = (
                session.execute(
                    select(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id,
                        t.actions.c.status == "QUEUED",
                        t.actions.c.available_at <= now,
                        t.actions.c.attempts < MAX_ATTEMPTS,
                    )
                    .order_by(t.actions.c.available_at, t.actions.c.created_at)
                    .with_for_update(skip_locked=True)
                    .limit(1)
                )
                .mappings()
                .first()
            )
            if selected_row is None:
                return None
            row = dict(selected_row)
            service = ActionService(session, self.ctx)
            error = None
            if not self.active_rh(session, row["approved_by"]):
                error = "APPROVER_REVOKED"
            elif row["digest"] != row["approved_digest"] or row["digest"] != action_digest(
                row["intervention_id"], row["payload"], row["not_before"], row["preview"]
            ):
                error = "APPROVAL_MISMATCH"
            elif row["kind"] != row["payload"].get("kind"):
                error = "PAYLOAD_MISMATCH"
            if not error:
                try:
                    service.ensure_area(
                        service.get(t.interventions, row["intervention_id"])["area_id"]
                    )
                except ActionError:
                    error = "AREA_NOT_ELIGIBLE"
            if error:
                session.execute(
                    update(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id, t.actions.c.id == row["id"]
                    )
                    .values(status="BLOCKED", error_code=error, updated_at=now)
                )
                service.event(
                    row["intervention_id"], "EXECUTION_BLOCKED", row["id"], {"code": error}
                )
                return {"skipped": True, "id": row["id"]}
            payload = PAYLOAD.validate_python(row["payload"])
            if isinstance(payload, SlackPayload) and payload.task_id:
                task = service.get(t.tasks, payload.task_id)
                if task["status"] != "OPEN":
                    service.cancel(row["id"])
                    return {"skipped": True, "id": row["id"]}
            token = uuid4()
            ordinal = row["attempts"] + 1
            session.execute(
                update(t.actions)
                .where(t.actions.c.empresa_id == self.ctx.empresa_id, t.actions.c.id == row["id"])
                .values(
                    status="RUNNING",
                    claim_token=token,
                    lease_until=now + timedelta(seconds=LEASE_SECONDS),
                    attempts=ordinal,
                    updated_at=now,
                )
            )
            session.execute(
                insert(t.attempts).values(
                    id=uuid4(),
                    empresa_id=self.ctx.empresa_id,
                    action_id=row["id"],
                    claim_token=token,
                    ordinal=ordinal,
                    status="STARTED",
                    started_at=now,
                )
            )
            service.event(
                row["intervention_id"], "EXECUTION_STARTED", row["id"], {"attempt": ordinal}
            )
            return row | {"claim_token": token, "attempts": ordinal}

    def _task(
        self, session: Session, service: ActionService, row: dict, payload: TaskPayload
    ) -> dict:
        responsible = payload.responsible_user_id or row["approved_by"]
        if not self.active_rh(session, responsible):
            raise DeliveryError("RESPONSIBLE_REVOKED")
        id = uuid5(row["id"], "task")
        session.execute(
            insert(t.tasks).values(
                id=id,
                empresa_id=self.ctx.empresa_id,
                action_id=row["id"],
                intervention_id=row["intervention_id"],
                title=payload.title,
                due_at=payload.due_at,
                responsible_user_id=responsible,
                status="OPEN",
                purpose=payload.purpose,
                created_at=utcnow(),
            )
        )
        if payload.reminders:
            for index in range(payload.reminders.max_reminders):
                due = payload.due_at + timedelta(days=index * payload.reminders.interval_days)
                if due < utcnow():
                    continue  # Nao enviar uma rajada retroativa ao recuperar um worker.
                child = uuid5(row["id"], f"reminder-{index}")
                child_payload = SlackPayload(
                    channel=payload.reminders.channel, template="DUE_REMINDER", task_id=id
                ).model_dump(mode="json", by_alias=True)
                preview = action_preview({"payload": child_payload, "id": child})
                fingerprint = action_digest(row["intervention_id"], child_payload, due, preview)
                session.execute(
                    insert(t.actions).values(
                        id=child,
                        empresa_id=self.ctx.empresa_id,
                        intervention_id=row["intervention_id"],
                        kind="SLACK",
                        status="QUEUED",
                        payload=child_payload,
                        preview=preview,
                        digest=fingerprint,
                        approved_digest=fingerprint,
                        approved_by=row["approved_by"],
                        approved_at=row["approved_at"],
                        authorization_parent_id=row["id"],
                        idempotency_key=f"reminder:{row['id']}:{index}",
                        not_before=due,
                        available_at=due,
                        attempts=0,
                        created_by=self.ctx.usuario_id,
                        created_at=utcnow(),
                        updated_at=utcnow(),
                    )
                )
                service.event(
                    row["intervention_id"],
                    "REMINDER_AUTHORIZED_BY_POLICY",
                    child,
                    {"parentActionId": str(row["id"]), "index": index},
                )
        return {"provider": "INTERNAL", "taskId": str(id)}

    def finish(
        self, row: dict, receipt: dict | None = None, error: DeliveryError | None = None
    ) -> None:
        now = utcnow()
        with self.transaction() as session:
            service = ActionService(session, self.ctx)
            current = service.get(t.actions, row["id"], True)
            if current["claim_token"] != row["claim_token"] or current["status"] not in {
                "RUNNING",
                "UNKNOWN",
            }:
                return
            payload = PAYLOAD.validate_python(row["payload"])
            if error is None and isinstance(payload, TaskPayload):
                # Insercao da tarefa, politicas derivadas e receipt na mesma transacao.
                try:
                    receipt = self._task(session, service, row, payload)
                except DeliveryError as problem:
                    error = problem
            if error:
                retry = error.retryable and row["attempts"] < MAX_ATTEMPTS
                status = (
                    "QUEUED"
                    if retry
                    else (
                        "UNKNOWN"
                        if error.uncertain
                        else (
                            "BLOCKED"
                            if error.code
                            in {
                                "CONNECTOR_DISABLED",
                                "CONNECTOR_NOT_CONFIGURED",
                                "TARGET_NOT_ALLOWED",
                                "RESPONSIBLE_REVOKED",
                                "EVENT_EXPIRED",
                            }
                            else "FAILED"
                        )
                    )
                )
                session.execute(
                    update(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id, t.actions.c.id == row["id"]
                    )
                    .values(
                        status=status,
                        error_code=error.code,
                        lease_until=None,
                        available_at=now
                        + timedelta(seconds=max(error.delay, 2 ** row["attempts"])),
                        updated_at=now,
                    )
                )
                attempt_status = "UNKNOWN" if error.uncertain else "REJECTED"
            else:
                session.execute(
                    update(t.actions)
                    .where(
                        t.actions.c.empresa_id == self.ctx.empresa_id, t.actions.c.id == row["id"]
                    )
                    .values(
                        status="SUCCEEDED",
                        receipt=receipt,
                        error_code=None,
                        lease_until=None,
                        updated_at=now,
                    )
                )
                status = "SUCCEEDED"
                attempt_status = "SUCCEEDED"
            session.execute(
                update(t.attempts)
                .where(
                    t.attempts.c.empresa_id == self.ctx.empresa_id,
                    t.attempts.c.claim_token == row["claim_token"],
                )
                .values(
                    status=attempt_status,
                    error_code=error.code if error else None,
                    receipt=receipt,
                    finished_at=now,
                )
            )
            service.event(
                row["intervention_id"],
                "EXECUTION_" + status,
                row["id"],
                {"code": error.code if error else None},
            )

    def run_once(self) -> dict:
        self.reap()
        row = self.claim()
        if row is None:
            return {"processed": False}
        if row.get("skipped"):
            return {"processed": True, "id": str(row["id"]), "skipped": True}
        payload = PAYLOAD.validate_python(row["payload"])
        if isinstance(payload, TaskPayload):
            self.finish(row)
        else:
            try:
                receipt = self.connectors.send(
                    self.ctx.empresa_id, row["id"], payload, row["digest"], row["preview"]
                )
            except DeliveryError as error:
                self.finish(row, error=error)
            except Exception:
                # Sem certeza do ponto da falha: nunca assumir que nada foi enviado.
                self.finish(row, error=DeliveryError("EXECUTION_OUTCOME_UNKNOWN", uncertain=True))
            else:
                self.finish(row, receipt=receipt)
        return {"processed": True, "id": str(row["id"])}


def main() -> None:
    parser = argparse.ArgumentParser(description="Worker de acoes aprovadas do RH (nuvem).")
    parser.add_argument("--once", action="store_true")
    parser.add_argument("--poll-seconds", type=int, default=5)
    args = parser.parse_args()
    empresa = os.getenv("VYTAI_WORKER_EMPRESA_ID", "")
    actor = os.getenv("VYTAI_WORKER_ACTOR_ID", "")
    if not empresa or not actor:
        parser.error("Configure a empresa e o principal RH do worker.")
    ctx = ContextoAutorizado(
        UUID(empresa), UUID(actor), frozenset({"RH"}), frozenset({"RH"}), str(uuid4())
    )
    connectors = Connectors(ConnectorSettings.from_env())
    worker = ActionWorker(lambda: Session(get_engine()), ctx, connectors)
    try:
        while True:
            result = worker.run_once()
            print(result, flush=True)  # Apenas IDs/estado, nunca conteudo ou segredos.
            if args.once:
                break
            if not result["processed"]:
                time.sleep(max(1, args.poll_seconds))
    finally:
        connectors.close()


@contextmanager
def embedded_worker() -> Iterator[None]:
    """Opcional para Web Service; fila duravel permanece no banco, nao na thread."""
    import logging
    import threading

    log = logging.getLogger(__name__)
    if os.getenv("VYTAI_WORKER_ENABLED", "").lower() != "true":
        yield
        return
    empresa = UUID(os.environ["VYTAI_WORKER_EMPRESA_ID"])
    actor = UUID(os.environ["VYTAI_WORKER_ACTOR_ID"])
    ctx = ContextoAutorizado(empresa, actor, frozenset({"RH"}), frozenset({"RH"}), str(uuid4()))
    stop = threading.Event()

    def loop() -> None:
        connectors = Connectors(ConnectorSettings.from_env())
        worker = ActionWorker(lambda: Session(get_engine()), ctx, connectors)
        try:
            while not stop.is_set():
                try:
                    worker.run_once()
                except Exception:
                    log.error("HR_WORKER_TICK_FAILED")
                stop.wait(5)
        finally:
            connectors.close()

    thread = threading.Thread(target=loop, name="vytai-rh-worker", daemon=True)
    thread.start()
    try:
        yield
    finally:
        stop.set()
        thread.join(timeout=1)


if __name__ == "__main__":
    main()
