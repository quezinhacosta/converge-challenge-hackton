"""Provisionamento administrativo explicito. Nunca chamado pelo frontend/agente."""

import argparse
import os
from uuid import UUID

from sqlalchemy import create_engine, text


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vincular usuario Supabase existente ao RH de uma empresa existente."
    )
    parser.add_argument("--empresa-id", required=True, type=UUID)
    parser.add_argument("--email", required=True)
    args = parser.parse_args()
    url = os.environ.get("DATABASE_ADMIN_URL", "")
    if not url:
        parser.error("Configure DATABASE_ADMIN_URL apenas no ambiente administrativo.")
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)
    engine = create_engine(url, hide_parameters=True, connect_args={"sslmode": "require"})
    try:
        with engine.begin() as conn:
            if not conn.execute(
                text("SELECT 1 FROM empresa WHERE id=:id"), {"id": args.empresa_id}
            ).first():
                raise ValueError(
                    "Empresa inexistente; crie a organizacao explicitamente antes do vinculo."
                )
            users = (
                conn.execute(
                    text(
                        "SELECT id,email_confirmed_at FROM auth.users WHERE lower(email)=lower(:email) AND deleted_at IS NULL"
                    ),
                    {"email": args.email.strip()},
                )
                .mappings()
                .all()
            )
            if len(users) != 1 or users[0]["email_confirmed_at"] is None:
                raise ValueError("Necessario um usuario Supabase existente com email confirmado.")
            conn.execute(
                text(
                    "INSERT INTO empresa_usuario(empresa_id,usuario_id,papeis,ativo) VALUES(:empresa,:user,ARRAY['RH'],true) ON CONFLICT(empresa_id,usuario_id) DO UPDATE SET papeis=ARRAY['RH'],ativo=true"
                ),
                {"empresa": args.empresa_id, "user": users[0]["id"]},
            )
            assert conn.execute(
                text(
                    "SELECT 1 FROM empresa_usuario WHERE empresa_id=:empresa AND usuario_id=:user AND ativo AND 'RH'=ANY(papeis)"
                ),
                {"empresa": args.empresa_id, "user": users[0]["id"]},
            ).first()
        print("Vinculo RH confirmado. Nenhum token ou senha foi gerado.")
    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
