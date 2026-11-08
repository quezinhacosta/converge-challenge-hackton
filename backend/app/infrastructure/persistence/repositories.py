"""Repositorios por requisicao: filtro de empresa explicito e transacao compartilhada."""

from dataclasses import asdict, fields, is_dataclass
from datetime import date, datetime
from enum import Enum
from types import UnionType
from typing import Any, cast, get_args, get_origin, get_type_hints
from uuid import UUID

from sqlalchemy import JSON, Column, MetaData, Table, Text, insert, select, update
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select

from app.domain.entities.area import Area
from app.domain.entities.pgr_inventory import PgrRiskItem
from app.domain.entities.risk_card import RiskCard
from app.domain.entities.signals import AreaMonthlyMetrics, ContextEvent
from app.domain.entities.survey import SurveySummary, TeamDevolutivaMessage

metadata = MetaData()
# O schema e criado exclusivamente por Alembic, nunca por create_all no runtime.
TABLES = {}
for name, extras in {
    "area": [],
    "metrica_area": ["area_id", "periodo"],
    "evento_area": ["area_id"],
    "risk_card": ["area_id"],
    "pgr_item": ["card_id"],
    "survey_summary": ["area_id", "periodo"],
    "team_devolutiva": ["area_id", "card_id"],
}.items():
    from sqlalchemy import Date, Uuid

    TABLES[name] = Table(
        name,
        metadata,
        Column("empresa_id", Uuid, primary_key=True),
        Column("id", Text, primary_key=True),
        Column("payload", JSON, nullable=False),
        *(Column(k, Date if k == "periodo" else Text) for k in extras),
    )


def encode(value: Any) -> Any:
    if is_dataclass(value) and not isinstance(value, type):
        return {k: encode(v) for k, v in asdict(value).items()}
    if isinstance(value, Enum):
        return value.value
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    if isinstance(value, dict):
        return {k: encode(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(v) for v in value]
    return value


def decode(cls: Any, value: Any) -> Any:
    if value is None:
        return None
    origin = get_origin(cls)
    if origin is UnionType:
        return decode(next(t for t in get_args(cls) if t is not type(None)), value)
    if origin is list:
        return [decode(get_args(cls)[0], v) for v in value]
    if origin is dict:
        return value
    if cls in (date, datetime):
        return cls.fromisoformat(value)
    if isinstance(cls, type) and issubclass(cls, Enum):
        return cls(value)
    if is_dataclass(cls):
        hints = get_type_hints(cls)
        return cast(Any, cls)(
            **{f.name: decode(hints[f.name], value[f.name]) for f in fields(cls) if f.name in value}
        )
    return value


class EntityRepository:
    def __init__(self, session: Session, empresa_id: UUID, table: str, entity: Any) -> None:
        self.session, self.empresa_id, self.table, self.entity = (
            session,
            empresa_id,
            TABLES[table],
            entity,
        )

    def _query(self) -> Select:
        return select(self.table.c.payload).where(self.table.c.empresa_id == self.empresa_id)

    def get_by_id(self, id: str) -> Any:
        stmt = self._query().where(self.table.c.id == id)
        if self.entity is RiskCard:
            stmt = stmt.with_for_update()
        row = self.session.execute(stmt).scalar_one_or_none()
        return decode(self.entity, row) if row is not None else None

    def list_all(self) -> list[Any]:
        return [decode(self.entity, v) for v in self.session.execute(self._query()).scalars()]

    def save(self, entity: Any) -> Any:
        values = {"payload": encode(entity)}
        if "area_id" in self.table.c:
            values["area_id"] = entity.area_id
        if "card_id" in self.table.c:
            values["card_id"] = entity.risk_card_id
        if "periodo" in self.table.c:
            values["periodo"] = entity.competence_period
        predicate = (self.table.c.empresa_id == self.empresa_id) & (self.table.c.id == entity.id)
        exists = self.session.execute(select(self.table.c.id).where(predicate)).first()
        if exists:
            self.session.execute(update(self.table).where(predicate).values(**values))
        else:
            self.session.execute(
                insert(self.table).values(empresa_id=self.empresa_id, id=entity.id, **values)
            )
        return entity


class CardRepository(EntityRepository):
    def list_active(self) -> list[RiskCard]:
        return [c for c in self.list_all() if c.status.value == "ABERTO"]


class SignalRepository:
    def __init__(self, session: Session, empresa_id: UUID) -> None:
        self.metrics = EntityRepository(session, empresa_id, "metrica_area", AreaMonthlyMetrics)
        self.events = EntityRepository(session, empresa_id, "evento_area", ContextEvent)

    def add_metrics(self, value: AreaMonthlyMetrics) -> None:
        self.metrics.save(value)

    def add_event(self, value: ContextEvent) -> None:
        self.events.save(value)

    def get_metrics_history(self, area_id: str, months: int = 6) -> list[AreaMonthlyMetrics]:
        return sorted(
            (m for m in self.metrics.list_all() if m.area_id == area_id),
            key=lambda m: m.competence_period,
            reverse=True,
        )[:months]

    def get_context_events(self, area_id: str) -> list[ContextEvent]:
        return [e for e in self.events.list_all() if e.area_id == area_id]

    def get_company_average_metrics(self, period: date) -> AreaMonthlyMetrics | None:
        # Nao fabricar uma media a partir do primeiro registro.
        return None


class SurveyRepository:
    def __init__(self, session: Session, empresa_id: UUID) -> None:
        self.summaries = EntityRepository(session, empresa_id, "survey_summary", SurveySummary)
        self.messages = EntityRepository(
            session, empresa_id, "team_devolutiva", TeamDevolutivaMessage
        )

    def get_latest_summary(self, area_id: str) -> SurveySummary | None:
        rows = [m for m in self.summaries.list_all() if m.area_id == area_id]
        return max(rows, key=lambda m: m.competence_period) if rows else None

    def save_summary(self, value: SurveySummary) -> Any:
        return self.summaries.save(value)

    def save_devolutiva(self, value: TeamDevolutivaMessage) -> Any:
        return self.messages.save(value)


class RepositoryBundle:
    def __init__(self, session: Session, empresa_id: UUID) -> None:
        self.area_repo = EntityRepository(session, empresa_id, "area", Area)
        self.signal_repo = SignalRepository(session, empresa_id)
        self.risk_card_repo = CardRepository(session, empresa_id, "risk_card", RiskCard)
        self.pgr_repo = EntityRepository(session, empresa_id, "pgr_item", PgrRiskItem)
        self.survey_repo = SurveyRepository(session, empresa_id)
