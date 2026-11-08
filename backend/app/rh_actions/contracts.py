"""Conteudo revisavel. O modelo pode preparar; somente RH autenticado aprova."""

import hashlib
import json
from datetime import datetime
from typing import Annotated, Literal
from uuid import UUID
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import ConfigDict, Field, field_validator, model_validator

from app.application.dtos.compat import ApiModel


class StrictModel(ApiModel):
    model_config = ConfigDict(extra="forbid")


class ReminderPolicy(StrictModel):
    channel: str = Field(pattern=r"^[CG][A-Z0-9]{5,30}$")
    interval_days: int = Field(default=7, ge=1, le=30)
    max_reminders: int = Field(default=2, ge=1, le=3)


class TaskPayload(StrictModel):
    kind: Literal["TASK"] = "TASK"
    title: str = Field(min_length=5, max_length=160)
    due_at: datetime
    responsible_user_id: UUID | None = None
    reminders: ReminderPolicy | None = None
    purpose: Literal["INTERVENTION", "REEVALUATION"] = "INTERVENTION"

    @field_validator("due_at")
    @classmethod
    def aware_due(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("dueAt deve ter timezone.")
        return value


class SlackPayload(StrictModel):
    kind: Literal["SLACK"] = "SLACK"
    channel: str = Field(pattern=r"^[CG][A-Z0-9]{5,30}$")
    template: Literal["FOLLOW_UP", "DUE_REMINDER", "EVIDENCE_REQUEST"] = "FOLLOW_UP"
    task_id: UUID | None = None


class CalendarPayload(StrictModel):
    kind: Literal["CALENDAR"] = "CALENDAR"
    calendar_id: str = Field(min_length=3, max_length=254)
    starts_at: datetime
    ends_at: datetime
    timezone: str = "America/Fortaleza"
    attendees: tuple[str, ...] = Field(default=(), max_length=20)

    @model_validator(mode="after")
    def valid_event(self) -> "CalendarPayload":
        import re

        if self.starts_at.tzinfo is None or self.ends_at.tzinfo is None:
            raise ValueError("Horarios devem ter timezone.")
        if (
            self.ends_at <= self.starts_at
            or (self.ends_at - self.starts_at).total_seconds() > 8 * 3600
        ):
            raise ValueError("Compromisso deve durar de 1 segundo a 8 horas.")
        try:
            ZoneInfo(self.timezone)
        except (ZoneInfoNotFoundError, ValueError):
            raise ValueError("Fuso horario invalido.") from None
        if any(not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+", email) for email in self.attendees):
            raise ValueError("Participante invalido.")
        return self


ActionPayload = Annotated[TaskPayload | SlackPayload | CalendarPayload, Field(discriminator="kind")]


class PrepareIntervention(StrictModel):
    area_id: str = Field(min_length=1, max_length=100)
    title: str = Field(min_length=5, max_length=160)
    objective: str = Field(min_length=10, max_length=1500)
    source_card_id: str | None = None
    source_pgr_id: str | None = None
    first_task: TaskPayload


class PrepareAction(StrictModel):
    payload: ActionPayload
    not_before: datetime

    @field_validator("not_before")
    @classmethod
    def aware(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("notBefore deve ter timezone.")
        return value


class ApproveAction(StrictModel):
    expected_digest: str = Field(pattern=r"^[a-f0-9]{64}$")


class RecordEvidence(StrictModel):
    description: str = Field(min_length=10, max_length=1000)
    url: str | None = Field(default=None, max_length=2048)

    @field_validator("url")
    @classmethod
    def safe_reference(cls, value: str | None) -> str | None:
        from urllib.parse import urlsplit

        if value:
            parts = urlsplit(value)
            if parts.scheme != "https" or not parts.hostname or parts.username or parts.password:
                raise ValueError(
                    "Referencia deve ser HTTPS sem credenciais. Nao sera acessada automaticamente."
                )
        return value


class ReconcileAction(StrictModel):
    outcome: Literal["CONFIRMED", "NOT_DELIVERED"]
    description: str = Field(min_length=15, max_length=1000)
    external_reference: str = Field(min_length=3, max_length=254)


class ActionError(Exception):
    def __init__(self, status: int, code: str, message: str):
        self.status, self.code, self.message = status, code, message
        super().__init__(code)


def digest(value: dict) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    ).hexdigest()


def slack_text(payload: SlackPayload, action_id: UUID) -> str:
    labels = {
        "FOLLOW_UP": "Existe um acompanhamento de RH para revisar.",
        "DUE_REMINDER": "Uma tarefa de RH chegou ao prazo de acompanhamento.",
        "EVIDENCE_REQUEST": "O RH precisa registrar evidencias de execucao de uma acao.",
    }
    # Texto deliberadamente neutro; nunca transportar objetivo/RAG/dados de saude ao canal.
    return labels[payload.template] + f" Consulte a fila privada do VytAI. Referencia: {action_id}."
