"""Casos de uso do RH. Nenhum desses metodos faz chamadas externas."""

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import UUID, uuid4, uuid5

from pydantic import TypeAdapter
from sqlalchemy import insert, select, text, update
from sqlalchemy.orm import Session

from app.application.contracts.identity import ContextoAutorizado
from app.infrastructure.persistence.repositories import TABLES
from app.rh_actions import tables as t
from app.rh_actions.contracts import (
    ActionError,
    ActionPayload,
    CalendarPayload,
    PrepareAction,
    PrepareIntervention,
    RecordEvidence,
    SlackPayload,
    TaskPayload,
    digest,
    slack_text,
)

PAYLOAD = TypeAdapter(ActionPayload)


def utcnow() -> datetime:
    return datetime.now(UTC)


def action_digest(intervention_id: UUID, payload: dict, not_before: datetime, preview: dict) -> str:
    return digest(
        {
            "interventionId": str(intervention_id),
            "payload": payload,
            "preview": preview,
            "notBefore": not_before.astimezone(UTC).isoformat(),
        }
    )


def action_preview(row: dict) -> dict:
    if row.get("preview") is not None:
        return dict(row["preview"])
    payload = PAYLOAD.validate_python(row["payload"])
    if isinstance(payload, SlackPayload):
        result = {
            "channel": payload.channel,
            "text": slack_text(payload, row["id"]),
            "sendsExternally": True,
        }
    elif isinstance(payload, CalendarPayload):
        result = {
            "calendarId": payload.calendar_id,
            "summary": "Acompanhamento de acao RH",
            "description": "Acompanhamento operacional do RH. Referencia VytAI: " + str(row["id"]),
            "startsAt": payload.starts_at.isoformat(),
            "endsAt": payload.ends_at.isoformat(),
            "attendees": list(payload.attendees),
            "sendsInvitations": bool(payload.attendees),
            "sendsExternally": True,
        }
    else:
        result = {
            "title": payload.title,
            "dueAt": payload.due_at.isoformat(),
            "sendsExternally": False,
            "scheduledReminders": [
                (payload.due_at + timedelta(days=i * payload.reminders.interval_days)).isoformat()
                for i in range(payload.reminders.max_reminders)
            ]
            if payload.reminders
            else [],
            "remindersPreview": [
                {
                    "scheduledAt": (
                        payload.due_at + timedelta(days=i * payload.reminders.interval_days)
                    ).isoformat(),
                    "channel": payload.reminders.channel,
                    "text": slack_text(
                        SlackPayload(channel=payload.reminders.channel, template="DUE_REMINDER"),
                        uuid5(row["id"], f"reminder-{i}"),
                    ),
                }
                for i in range(payload.reminders.max_reminders)
            ]
            if payload.reminders
            else [],
            "reminderPolicy": payload.reminders.model_dump(mode="json", by_alias=True)
            if payload.reminders
            else None,
        }
    return result


class ActionService:
    def __init__(self, session: Session, ctx: ContextoAutorizado):
        if "RH" not in ctx.papeis:
            raise ActionError(403, "RH_REQUIRED", "Apenas o RH pode operar esta fila.")
        self.session, self.ctx = session, ctx

    def _where(self, table: Any) -> Any:
        return table.c.empresa_id == self.ctx.empresa_id

    def get(self, table: Any, id: UUID, lock: bool = False) -> dict:
        query = select(table).where(self._where(table), table.c.id == id)
        if lock:
            query = query.with_for_update()
        row = self.session.execute(query).mappings().first()
        if row is None:
            raise ActionError(404, "NOT_FOUND", "Registro nao encontrado.")
        return dict(row)

    def event(
        self,
        intervention_id: UUID,
        event_type: str,
        action_id: UUID | None = None,
        details: dict | None = None,
    ) -> None:
        self.session.execute(
            insert(t.events).values(
                id=uuid4(),
                empresa_id=self.ctx.empresa_id,
                intervention_id=intervention_id,
                action_id=action_id,
                event_type=event_type,
                actor_id=self.ctx.usuario_id,
                details=details or {},
                created_at=utcnow(),
            )
        )

    def ensure_area(self, area_id: str) -> None:
        row = self.session.execute(
            select(TABLES["area"].c.payload).where(
                self._where(TABLES["area"]), TABLES["area"].c.id == area_id
            )
        ).scalar_one_or_none()
        if row is None:
            raise ActionError(404, "AREA_NOT_FOUND", "Area nao encontrada.")
        if row.get("headcount", 0) < 5:
            raise ActionError(409, "BLOCKED_PRIVACY", "Grupo sem elegibilidade para este fluxo.")

    def _responsible(self, user_id: UUID) -> None:
        found = self.session.execute(
            text(
                "SELECT 1 FROM empresa_usuario WHERE empresa_id=:empresa "
                "AND usuario_id=:usuario AND ativo AND 'RH'=ANY(papeis)"
            ),
            {"empresa": self.ctx.empresa_id, "usuario": user_id},
        ).first()
        if not found:
            raise ActionError(
                422, "RESPONSIBLE_NOT_RH", "Responsavel deve ter vinculo ativo no RH desta empresa."
            )

    def validate_payload(self, payload: Any, intervention_id: UUID) -> None:
        now = utcnow()
        if isinstance(payload, TaskPayload):
            if payload.due_at <= now or payload.due_at > now + timedelta(days=366):
                raise ActionError(
                    422, "INVALID_DUE_DATE", "Prazo deve estar no futuro, em ate um ano."
                )
            self._responsible(payload.responsible_user_id or self.ctx.usuario_id)
        elif isinstance(payload, CalendarPayload):
            if payload.starts_at <= now or payload.starts_at > now + timedelta(days=366):
                raise ActionError(
                    422, "STALE_EVENT", "Compromisso precisa estar no futuro, em ate um ano."
                )
        elif payload.task_id:
            task = self.get(t.tasks, payload.task_id)
            if task["intervention_id"] != intervention_id or task["status"] != "OPEN":
                raise ActionError(
                    409, "TASK_NOT_OPEN", "Tarefa vinculada nao esta aberta nesta intervencao."
                )

    def _lock_key(self, namespace: str, key: str) -> None:
        self.session.execute(
            text("SELECT pg_advisory_xact_lock(hashtextextended(:key,0))"),
            {"key": f"{self.ctx.empresa_id}:{namespace}:{key}"},
        )

    def prepare_intervention(self, request: PrepareIntervention, key: str) -> dict:
        self._lock_key("intervention", key)
        body = request.model_dump(mode="json", by_alias=True)
        request_hash = digest(body)
        existing = (
            self.session.execute(
                select(t.interventions).where(
                    self._where(t.interventions), t.interventions.c.idempotency_key == key
                )
            )
            .mappings()
            .first()
        )
        if existing:
            if existing["request_digest"] != request_hash:
                raise ActionError(409, "IDEMPOTENCY_CONFLICT", "Chave ja usada com outro conteudo.")
            return self.intervention(existing["id"])
        self.ensure_area(request.area_id)
        for field, table, source_id in [
            ("card", TABLES["risk_card"], request.source_card_id),
            ("pgr", TABLES["pgr_item"], request.source_pgr_id),
        ]:
            if source_id:
                item = self.session.execute(
                    select(table.c.payload).where(self._where(table), table.c.id == source_id)
                ).scalar_one_or_none()
                if item is None or item.get("area_id") != request.area_id:
                    raise ActionError(
                        404, "SOURCE_NOT_FOUND", "Fonte nao encontrada na area autorizada."
                    )
                if field == "card" and (
                    item.get("probable_risk_factor") == "ASSEDIO"
                    or item.get("status") == "ESCALADO"
                ):
                    raise ActionError(
                        409, "COMPLIANCE_ONLY", "Caso escalado exige o fluxo de compliance."
                    )
        id = uuid4()
        self.session.execute(
            insert(t.interventions).values(
                id=id,
                empresa_id=self.ctx.empresa_id,
                area_id=request.area_id,
                title=request.title,
                objective=request.objective,
                source_card_id=request.source_card_id,
                source_pgr_id=request.source_pgr_id,
                created_by=self.ctx.usuario_id,
                idempotency_key=key,
                request_digest=request_hash,
                created_at=utcnow(),
            )
        )
        self.event(id, "INTERVENTION_PREPARED")
        self.prepare_action(
            id, PrepareAction(payload=request.first_task, not_before=utcnow()), "initial:" + str(id)
        )
        return self.intervention(id)

    def prepare_action(self, intervention_id: UUID, request: PrepareAction, key: str) -> dict:
        self._lock_key("action", key)
        intervention = self.get(t.interventions, intervention_id)
        self.ensure_area(intervention["area_id"])
        payload = request.payload.model_dump(mode="json", by_alias=True)
        existing = (
            self.session.execute(
                select(t.actions).where(self._where(t.actions), t.actions.c.idempotency_key == key)
            )
            .mappings()
            .first()
        )
        id = existing["id"] if existing else uuid4()
        preview = action_preview({"payload": payload, "id": id})
        fingerprint = action_digest(intervention_id, payload, request.not_before, preview)
        if existing:
            if existing["digest"] != fingerprint:
                raise ActionError(409, "IDEMPOTENCY_CONFLICT", "Chave ja usada com outro conteudo.")
            return self.action(existing["id"])
        self.validate_payload(request.payload, intervention_id)
        if request.not_before > utcnow() + timedelta(days=366):
            raise ActionError(422, "INVALID_SCHEDULE", "Agendamento maximo de um ano.")
        now = utcnow()
        self.session.execute(
            insert(t.actions).values(
                id=id,
                empresa_id=self.ctx.empresa_id,
                intervention_id=intervention_id,
                kind=request.payload.kind,
                status="PENDING",
                payload=payload,
                preview=preview,
                digest=fingerprint,
                idempotency_key=key,
                not_before=request.not_before,
                available_at=request.not_before,
                attempts=0,
                created_by=self.ctx.usuario_id,
                created_at=now,
                updated_at=now,
            )
        )
        self.event(
            intervention_id,
            "ACTION_PREPARED",
            id,
            {"digest": fingerprint, "kind": request.payload.kind},
        )
        return self.action(id)

    def action(self, id: UUID) -> dict:
        row = self.get(t.actions, id)
        row["preview"] = action_preview(row)
        return row

    def approve(self, id: UUID, expected_digest: str) -> dict:
        row = self.get(t.actions, id, True)
        if row["digest"] != expected_digest or row["digest"] != action_digest(
            row["intervention_id"], row["payload"], row["not_before"], row["preview"]
        ):
            raise ActionError(
                409, "STALE_APPROVAL", "Conteudo diferente do revisado. Revise a proposta atual."
            )
        if row["status"] != "PENDING":
            raise ActionError(409, "ALREADY_REVIEWED", "Acao ja revisada; consulte o estado atual.")
        self.ensure_area(self.get(t.interventions, row["intervention_id"])["area_id"])
        self.validate_payload(PAYLOAD.validate_python(row["payload"]), row["intervention_id"])
        self.session.execute(
            update(t.actions)
            .where(self._where(t.actions), t.actions.c.id == id)
            .values(
                status="QUEUED",
                approved_digest=expected_digest,
                approved_by=self.ctx.usuario_id,
                approved_at=utcnow(),
                updated_at=utcnow(),
            )
        )
        self.event(row["intervention_id"], "ACTION_APPROVED", id, {"digest": expected_digest})
        return self.action(id)

    def cancel(self, id: UUID) -> dict:
        row = self.get(t.actions, id, True)
        if row["status"] not in {"PENDING", "QUEUED", "BLOCKED"}:
            raise ActionError(
                409,
                "NOT_CANCELLABLE",
                "Acao em execucao ou com resultado registrado. Consulte o historico.",
            )
        self.session.execute(
            update(t.actions)
            .where(self._where(t.actions), t.actions.c.id == id)
            .values(status="CANCELLED", updated_at=utcnow())
        )
        self.event(row["intervention_id"], "ACTION_CANCELLED", id)
        return self.action(id)

    def retry(self, id: UUID) -> dict:
        row = self.get(t.actions, id, True)
        if row["status"] not in {"BLOCKED", "FAILED"} or row["attempts"] >= 5:
            raise ActionError(
                409, "RETRY_NOT_SAFE", "Resultado incerto nao pode ser reenviado automaticamente."
            )
        if row["approved_digest"] != action_digest(
            row["intervention_id"], row["payload"], row["not_before"], row["preview"]
        ):
            raise ActionError(409, "STALE_APPROVAL", "A aprovacao nao corresponde ao conteudo.")
        self.session.execute(
            update(t.actions)
            .where(self._where(t.actions), t.actions.c.id == id)
            .values(status="QUEUED", available_at=utcnow(), updated_at=utcnow(), error_code=None)
        )
        self.event(row["intervention_id"], "RETRY_REQUESTED", id)
        return self.action(id)

    def intervention(self, id: UUID) -> dict:
        item = self.get(t.interventions, id)
        item["actions"] = [
            self.action(r)
            for r in self.session.execute(
                select(t.actions.c.id)
                .where(self._where(t.actions), t.actions.c.intervention_id == id)
                .order_by(t.actions.c.created_at)
            ).scalars()
        ]
        item["tasks"] = [
            dict(r)
            for r in self.session.execute(
                select(t.tasks).where(self._where(t.tasks), t.tasks.c.intervention_id == id)
            ).mappings()
        ]
        return item

    def list_interventions(self) -> list[dict]:
        return [
            dict(r)
            for r in self.session.execute(
                select(t.interventions)
                .where(self._where(t.interventions))
                .order_by(t.interventions.c.created_at.desc())
                .limit(100)
            ).mappings()
        ]

    def pending(self) -> dict:
        now = utcnow()
        actions = [
            dict(r)
            for r in self.session.execute(
                select(t.actions)
                .where(
                    self._where(t.actions),
                    t.actions.c.status.in_(
                        ["PENDING", "QUEUED", "RUNNING", "BLOCKED", "UNKNOWN", "FAILED"]
                    ),
                )
                .order_by(t.actions.c.created_at)
                .limit(100)
            ).mappings()
        ]
        tasks = [
            dict(r)
            for r in self.session.execute(
                select(t.tasks)
                .where(self._where(t.tasks), t.tasks.c.status == "OPEN")
                .order_by(t.tasks.c.due_at)
                .limit(100)
            ).mappings()
        ]
        for item in actions:
            item["preview"] = action_preview(item)
        for item in tasks:
            item["overdue"] = item["due_at"] < now
        return {"actions": actions, "tasks": tasks, "asOf": now}

    def record_evidence(self, task_id: UUID, request: RecordEvidence) -> dict:
        task = self.get(t.tasks, task_id, True)
        if task["status"] != "OPEN":
            raise ActionError(409, "TASK_NOT_OPEN", "Tarefa nao esta aberta.")
        id = uuid4()
        self.session.execute(
            insert(t.evidence).values(
                id=id,
                empresa_id=self.ctx.empresa_id,
                task_id=task_id,
                description=request.description,
                url=request.url,
                actor_id=self.ctx.usuario_id,
                created_at=utcnow(),
            )
        )
        self.event(
            task["intervention_id"],
            "EVIDENCE_RECORDED",
            task["action_id"],
            {"evidenceId": str(id), "source": "RH_REPORTED"},
        )
        return {"id": id, "source": "RH_REPORTED"}

    def complete_task(self, id: UUID) -> dict:
        task = self.get(t.tasks, id, True)
        if task["status"] != "OPEN":
            raise ActionError(409, "TASK_NOT_OPEN", "Tarefa nao esta aberta.")
        found = self.session.execute(
            select(t.evidence.c.id).where(self._where(t.evidence), t.evidence.c.task_id == id)
        ).first()
        if not found:
            raise ActionError(
                409, "EVIDENCE_REQUIRED", "Registre evidencia da execucao antes de concluir."
            )
        self.session.execute(
            update(t.tasks)
            .where(self._where(t.tasks), t.tasks.c.id == id)
            .values(status="DONE", completed_at=utcnow())
        )
        self.event(task["intervention_id"], "TASK_COMPLETED_BY_RH", task["action_id"])
        # Cancelar lembretes ainda nao enviados; RUNNING e conferido no claim/finalizacao.
        children = (
            self.session.execute(
                select(t.actions).where(
                    self._where(t.actions),
                    t.actions.c.authorization_parent_id == task["action_id"],
                    t.actions.c.status == "QUEUED",
                )
            )
            .mappings()
            .all()
        )
        for child in children:
            self.cancel(child["id"])
        return self.get(t.tasks, id)

    def history(self, intervention_id: UUID) -> dict:
        self.get(t.interventions, intervention_id)
        event_rows = [
            dict(r)
            for r in self.session.execute(
                select(t.events)
                .where(self._where(t.events), t.events.c.intervention_id == intervention_id)
                .order_by(t.events.c.created_at)
            ).mappings()
        ]
        task_ids = select(t.tasks.c.id).where(
            self._where(t.tasks), t.tasks.c.intervention_id == intervention_id
        )
        evidence_rows = [
            dict(r)
            for r in self.session.execute(
                select(t.evidence).where(
                    self._where(t.evidence), t.evidence.c.task_id.in_(task_ids)
                )
            ).mappings()
        ]
        return {"events": event_rows, "evidence": evidence_rows}

    def cancel_task(self, id: UUID) -> dict:
        task = self.get(t.tasks, id, True)
        if task["status"] != "OPEN":
            raise ActionError(409, "TASK_NOT_OPEN", "Tarefa nao esta aberta.")
        self.session.execute(
            update(t.tasks)
            .where(self._where(t.tasks), t.tasks.c.id == id)
            .values(status="CANCELLED")
        )
        for child in (
            self.session.execute(
                select(t.actions.c.id).where(
                    self._where(t.actions),
                    t.actions.c.authorization_parent_id == task["action_id"],
                    t.actions.c.status == "QUEUED",
                )
            )
            .scalars()
            .all()
        ):
            self.cancel(child)
        self.event(task["intervention_id"], "TASK_CANCELLED_BY_RH", task["action_id"])
        return self.get(t.tasks, id)

    def request_review(self, id: UUID) -> dict:
        row = self.get(t.actions, id, True)
        if row["status"] not in {"BLOCKED", "FAILED"}:
            raise ActionError(
                409,
                "REVIEW_NOT_SAFE",
                "Execucao incerta deve ser reconciliada antes de nova aprovacao.",
            )
        if row["attempts"] >= 5:
            raise ActionError(
                409, "ATTEMPTS_EXHAUSTED", "Limite de tentativas atingido; revise o caso."
            )
        self.session.execute(
            update(t.actions)
            .where(self._where(t.actions), t.actions.c.id == id)
            .values(
                status="PENDING",
                approved_by=None,
                approved_at=None,
                approved_digest=None,
                error_code=None,
                updated_at=utcnow(),
            )
        )
        self.event(row["intervention_id"], "NEW_REVIEW_REQUESTED", id)
        return self.action(id)

    def reconcile(self, id: UUID, request: Any) -> dict:
        row = self.get(t.actions, id, True)
        if row["status"] != "UNKNOWN":
            raise ActionError(409, "NOT_UNCERTAIN", "Acao nao esta pendente de conferencia.")
        confirmed = request.outcome == "CONFIRMED"
        receipt = (
            {
                "provider": "RH_REPORTED",
                "externalReference": request.external_reference,
                "confirmedBy": str(self.ctx.usuario_id),
            }
            if confirmed
            else None
        )
        self.session.execute(
            update(t.actions)
            .where(self._where(t.actions), t.actions.c.id == id)
            .values(
                status="SUCCEEDED" if confirmed else "FAILED",
                receipt=receipt,
                error_code=None if confirmed else "RH_CONFIRMED_NOT_DELIVERED",
                updated_at=utcnow(),
            )
        )
        self.event(
            row["intervention_id"],
            "OUTCOME_RECONCILED_BY_RH",
            id,
            {
                "outcome": request.outcome,
                "externalReference": request.external_reference,
                "description": request.description,
            },
        )
        return self.action(id)
