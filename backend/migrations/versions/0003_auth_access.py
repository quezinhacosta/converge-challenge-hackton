"""Acesso de membership somente pelo backend, com RLS."""

from alembic import op

revision = "0003_auth_access"
down_revision = "0002_hr_actions"
branch_labels = None
depends_on = None
SQL = """
-- Membership e cadastro de empresa nunca sao acessados pelo Data API publico.
REVOKE ALL ON empresa,empresa_usuario FROM PUBLIC;
DO $b$ BEGIN
IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='anon') THEN REVOKE ALL ON empresa,empresa_usuario FROM anon; END IF;
IF EXISTS(SELECT 1 FROM pg_roles WHERE rolname='authenticated') THEN REVOKE ALL ON empresa,empresa_usuario FROM authenticated; END IF;
END; $b$;
ALTER TABLE empresa_usuario ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresa_usuario FORCE ROW LEVEL SECURITY;
CREATE POLICY membership_servidor ON empresa_usuario FOR SELECT TO vytai_app USING(
 empresa_id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid OR
 usuario_id=NULLIF(current_setting('vytai.usuario_id',true),'')::uuid);
ALTER TABLE empresa ENABLE ROW LEVEL SECURITY;
ALTER TABLE empresa FORCE ROW LEVEL SECURITY;
CREATE POLICY empresa_servidor ON empresa FOR SELECT TO vytai_app USING(
 id=NULLIF(current_setting('vytai.empresa_id',true),'')::uuid OR
 EXISTS(SELECT 1 FROM empresa_usuario m WHERE m.empresa_id=empresa.id AND m.ativo AND m.usuario_id=NULLIF(current_setting('vytai.usuario_id',true),'')::uuid));
CREATE INDEX empresa_usuario_login ON empresa_usuario(usuario_id) WHERE ativo;
"""


def upgrade() -> None:
    op.execute(SQL)


def downgrade() -> None:
    raise RuntimeError("Usar migration corretiva; nao remover a protecao de acesso.")
