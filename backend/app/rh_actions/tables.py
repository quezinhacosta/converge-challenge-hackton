"""Mapeamento Core: schema criado apenas por Alembic."""

from sqlalchemy import JSON, Column, DateTime, Integer, MetaData, String, Table, Text, Uuid

metadata = MetaData()


def table(name: str, *columns: Column) -> Table:
    return Table(
        name,
        metadata,
        Column("id", Uuid, primary_key=True),
        Column("empresa_id", Uuid, nullable=False),
        *columns,
    )


interventions = table(
    "rh_intervencao",
    Column("area_id", Text),
    Column("title", Text),
    Column("objective", Text),
    Column("source_card_id", Text),
    Column("source_pgr_id", Text),
    Column("created_by", Uuid),
    Column("idempotency_key", String),
    Column("request_digest", String),
    Column("created_at", DateTime(timezone=True)),
)
actions = table(
    "rh_acao",
    Column("intervention_id", Uuid),
    Column("kind", String),
    Column("status", String),
    Column("payload", JSON),
    Column("preview", JSON),
    Column("digest", String),
    Column("approved_digest", String),
    Column("approved_by", Uuid),
    Column("approved_at", DateTime(timezone=True)),
    Column("authorization_parent_id", Uuid),
    Column("idempotency_key", String),
    Column("not_before", DateTime(timezone=True)),
    Column("available_at", DateTime(timezone=True)),
    Column("attempts", Integer),
    Column("lease_until", DateTime(timezone=True)),
    Column("claim_token", Uuid),
    Column("receipt", JSON),
    Column("error_code", String),
    Column("created_by", Uuid),
    Column("created_at", DateTime(timezone=True)),
    Column("updated_at", DateTime(timezone=True)),
)
tasks = table(
    "rh_tarefa",
    Column("action_id", Uuid),
    Column("intervention_id", Uuid),
    Column("title", Text),
    Column("due_at", DateTime(timezone=True)),
    Column("responsible_user_id", Uuid),
    Column("status", String),
    Column("purpose", String),
    Column("completed_at", DateTime(timezone=True)),
    Column("created_at", DateTime(timezone=True)),
)
evidence = table(
    "rh_evidencia",
    Column("task_id", Uuid),
    Column("description", Text),
    Column("url", Text),
    Column("actor_id", Uuid),
    Column("created_at", DateTime(timezone=True)),
)
events = table(
    "rh_acao_evento",
    Column("action_id", Uuid),
    Column("intervention_id", Uuid),
    Column("event_type", String),
    Column("actor_id", Uuid),
    Column("details", JSON),
    Column("created_at", DateTime(timezone=True)),
)
attempts = table(
    "rh_tentativa",
    Column("action_id", Uuid),
    Column("claim_token", Uuid),
    Column("ordinal", Integer),
    Column("status", String),
    Column("error_code", String),
    Column("receipt", JSON),
    Column("started_at", DateTime(timezone=True)),
    Column("finished_at", DateTime(timezone=True)),
)
