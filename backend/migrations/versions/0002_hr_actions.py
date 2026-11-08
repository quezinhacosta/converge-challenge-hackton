"""Fila de execucao do RH e auditoria; nao altera o schema documental."""

from alembic import op

revision = "0002_hr_actions"
down_revision = "0001_shared_foundation"
branch_labels = None
depends_on = None
SQL = """
CREATE TABLE rh_intervencao (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL REFERENCES empresa(id), area_id text NOT NULL,
 title text NOT NULL, objective text NOT NULL, source_card_id text, source_pgr_id text,
 created_by uuid NOT NULL, idempotency_key varchar(128) NOT NULL, request_digest char(64) NOT NULL,
 created_at timestamptz NOT NULL, UNIQUE(empresa_id,id), UNIQUE(empresa_id,idempotency_key),
 FOREIGN KEY(empresa_id,area_id) REFERENCES area(empresa_id,id),
 FOREIGN KEY(empresa_id,source_card_id) REFERENCES risk_card(empresa_id,id),
 FOREIGN KEY(empresa_id,source_pgr_id) REFERENCES pgr_item(empresa_id,id)
);
CREATE TABLE rh_acao (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL, intervention_id uuid NOT NULL,
 kind text NOT NULL CHECK(kind IN ('TASK','SLACK','CALENDAR')),
 status text NOT NULL CHECK(status IN ('PENDING','QUEUED','RUNNING','SUCCEEDED','BLOCKED','UNKNOWN','FAILED','CANCELLED')),
 payload jsonb NOT NULL, preview jsonb NOT NULL, digest char(64) NOT NULL, approved_digest char(64), approved_by uuid,
 approved_at timestamptz, authorization_parent_id uuid, idempotency_key varchar(128) NOT NULL,
 not_before timestamptz NOT NULL, available_at timestamptz NOT NULL, attempts integer NOT NULL DEFAULT 0 CHECK(attempts BETWEEN 0 AND 5),
 lease_until timestamptz, claim_token uuid, receipt jsonb, error_code text, created_by uuid NOT NULL,
 created_at timestamptz NOT NULL, updated_at timestamptz NOT NULL,
 UNIQUE(empresa_id,id), UNIQUE(empresa_id,idempotency_key),
 FOREIGN KEY(empresa_id,intervention_id) REFERENCES rh_intervencao(empresa_id,id),
 FOREIGN KEY(empresa_id,authorization_parent_id) REFERENCES rh_acao(empresa_id,id),
 CHECK(status IN ('PENDING','CANCELLED') OR (approved_digest=digest AND approved_by IS NOT NULL AND approved_at IS NOT NULL))
);
CREATE INDEX rh_acao_fila ON rh_acao(empresa_id,status,available_at);
CREATE TABLE rh_tarefa (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL, action_id uuid NOT NULL, intervention_id uuid NOT NULL,
 title text NOT NULL, due_at timestamptz NOT NULL, responsible_user_id uuid NOT NULL,
 status text NOT NULL CHECK(status IN ('OPEN','DONE','CANCELLED')), purpose text NOT NULL CHECK(purpose IN ('INTERVENTION','REEVALUATION')),
 completed_at timestamptz, created_at timestamptz NOT NULL,
 UNIQUE(empresa_id,id),UNIQUE(empresa_id,action_id),
 FOREIGN KEY(empresa_id,action_id) REFERENCES rh_acao(empresa_id,id),
 FOREIGN KEY(empresa_id,intervention_id) REFERENCES rh_intervencao(empresa_id,id),
 FOREIGN KEY(empresa_id,responsible_user_id) REFERENCES empresa_usuario(empresa_id,usuario_id)
);
CREATE TABLE rh_evidencia (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL, task_id uuid NOT NULL, description text NOT NULL,
 url text, actor_id uuid NOT NULL, created_at timestamptz NOT NULL,
 FOREIGN KEY(empresa_id,task_id) REFERENCES rh_tarefa(empresa_id,id)
);
CREATE TABLE rh_acao_evento (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL, action_id uuid, intervention_id uuid NOT NULL,
 event_type text NOT NULL, actor_id uuid NOT NULL, details jsonb NOT NULL DEFAULT '{}', created_at timestamptz NOT NULL,
 FOREIGN KEY(empresa_id,intervention_id) REFERENCES rh_intervencao(empresa_id,id),
 FOREIGN KEY(empresa_id,action_id) REFERENCES rh_acao(empresa_id,id)
);
CREATE TABLE rh_tentativa (
 id uuid PRIMARY KEY, empresa_id uuid NOT NULL, action_id uuid NOT NULL, claim_token uuid NOT NULL,
 ordinal integer NOT NULL, status text NOT NULL CHECK(status IN ('STARTED','SUCCEEDED','REJECTED','UNKNOWN')),
 error_code text, receipt jsonb, started_at timestamptz NOT NULL, finished_at timestamptz,
 UNIQUE(empresa_id,action_id,ordinal), UNIQUE(claim_token),
 FOREIGN KEY(empresa_id,action_id) REFERENCES rh_acao(empresa_id,id)
);
ALTER TABLE rh_intervencao ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_intervencao FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_intervencao USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_intervencao FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_intervencao FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_intervencao FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT,UPDATE ON rh_intervencao TO vytai_app;
ALTER TABLE rh_acao ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_acao FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_acao USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_acao FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_acao FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_acao FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT,UPDATE ON rh_acao TO vytai_app;
ALTER TABLE rh_tarefa ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_tarefa FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_tarefa USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_tarefa FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_tarefa FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_tarefa FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT,UPDATE ON rh_tarefa TO vytai_app;
ALTER TABLE rh_evidencia ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_evidencia FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_evidencia USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_evidencia FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_evidencia FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_evidencia FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT ON rh_evidencia TO vytai_app;
ALTER TABLE rh_acao_evento ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_acao_evento FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_acao_evento USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_acao_evento FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_acao_evento FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_acao_evento FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT ON rh_acao_evento TO vytai_app;
ALTER TABLE rh_tentativa ENABLE ROW LEVEL SECURITY; ALTER TABLE rh_tentativa FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_isolada ON rh_tentativa USING(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid) WITH CHECK(empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid);
REVOKE ALL ON rh_tentativa FROM PUBLIC;
DO $b$ BEGIN IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON rh_tentativa FROM anon; END IF; IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON rh_tentativa FROM authenticated; END IF; END; $b$;
GRANT SELECT,INSERT,UPDATE ON rh_tentativa TO vytai_app;
"""


def upgrade() -> None:
    op.execute(SQL)


def downgrade() -> None:
    raise RuntimeError("Use migration corretiva; historico operacional nao deve ser apagado.")
