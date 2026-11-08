"""Gates reais PostgreSQL; requer banco descartavel exclusivo, nunca banco produtivo."""

import os
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.domain.entities.area import Area
from app.infrastructure.persistence.repositories import RepositoryBundle

URL = os.getenv("VYTAI_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="PostgreSQL de teste nao configurado")


@pytest.fixture(scope="module")
def engine():
    env = os.environ | {"DATABASE_URL": URL}
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[2],
        env=env,
        check=True,
        capture_output=True,
    )
    engine = create_engine(URL)
    yield engine
    engine.dispose()


def scope(session, company):
    session.execute(text("SET LOCAL ROLE vytai_app"))
    session.execute(
        text("SELECT set_config('vytai.empresa_id',:company,true)"), {"company": str(company)}
    )


def test_postgres_migrations_fts_and_composite_tenant_fk(engine):
    from sqlalchemy.exc import IntegrityError

    company, other, user, doc, version = [uuid4() for _ in range(5)]
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO empresa(id,nome) VALUES(:id,'Teste'),(:other,'Outro')"),
            {"id": company, "other": other},
        )
        conn.execute(text("SELECT set_config('vytai.empresa_id',:id,true)"), {"id": str(company)})
        conn.execute(
            text(
                "INSERT INTO documento(id,empresa_id,titulo,categoria,responsavel,criado_por) VALUES(:id,:company,'Política de acolhimento','POLITICA','RH',:user)"
            ),
            {"id": doc, "company": company, "user": user},
        )
        conn.execute(
            text(
                "INSERT INTO documento_versao(id,documento_id,empresa_id,numero,origem,sha256_conteudo,vigencia_inicio,status,criado_por) VALUES(:id,:doc,:company,1,'TEXTO',:hash,'2026-01-01','PRONTO',:user)"
            ),
            {"id": version, "doc": doc, "company": company, "hash": "a" * 64, "user": user},
        )
        conn.execute(
            text(
                "INSERT INTO documento_trecho(id,versao_id,empresa_id,ordem,texto) VALUES(:id,:version,:company,0,'Orientação para acolhimento e prevenção')"
            ),
            {"id": uuid4(), "version": version, "company": company},
        )
        count = conn.execute(
            text(
                "SELECT count(*) FROM documento_trecho WHERE empresa_id=:company AND tsv @@ websearch_to_tsquery('public.vytai_portuguese','prevencao')"
            ),
            {"company": company},
        ).scalar_one()
        assert count == 1
        with pytest.raises(IntegrityError) as violation, conn.begin_nested():
            conn.execute(
                text(
                    "INSERT INTO documento_versao(id,documento_id,empresa_id,numero,origem,sha256_conteudo,vigencia_inicio,status,criado_por) VALUES(:id,:doc,:other,2,'TEXTO',:hash,'2026-01-01','PRONTO',:user)"
                ),
                {"id": uuid4(), "doc": doc, "other": other, "hash": "b" * 64, "user": user},
            )
        assert violation.value.orig.sqlstate == "23503"
        # RLS com papel sem bypass, nao apenas superusuario da CI.
        role = "vytai_rls_" + uuid4().hex
        conn.exec_driver_sql(f"CREATE ROLE {role} NOLOGIN")
        conn.exec_driver_sql(f"GRANT USAGE ON SCHEMA public TO {role}")
        conn.exec_driver_sql(f"GRANT SELECT ON documento_trecho TO {role}")
        conn.exec_driver_sql(f"SET LOCAL ROLE {role}")
        conn.execute(text("SELECT set_config('vytai.empresa_id',:id,true)"), {"id": str(other)})
        assert conn.execute(text("SELECT count(*) FROM documento_trecho")).scalar_one() == 0
        conn.execute(text("SELECT set_config('vytai.empresa_id',:id,true)"), {"id": str(company)})
        assert conn.execute(text("SELECT count(*) FROM documento_trecho")).scalar_one() == 1
        conn.exec_driver_sql("RESET ROLE")
        conn.exec_driver_sql(f"DROP OWNED BY {role}")
        conn.exec_driver_sql(f"DROP ROLE {role}")
        conn.execute(
            text("DELETE FROM documento WHERE id=:id AND empresa_id=:company"),
            {"id": doc, "company": company},
        )
        assert (
            conn.execute(
                text("SELECT count(*) FROM documento_trecho WHERE empresa_id=:company"),
                {"company": company},
            ).scalar_one()
            == 0
        )


def test_postgres_repository_survives_new_session(engine):
    company = uuid4()
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO empresa(id,nome) VALUES(:id,'Persistencia')"), {"id": company}
        )
    with Session(engine) as session, session.begin():
        scope(session, company)
        RepositoryBundle(session, company).area_repo.save(
            Area(id="a", name="Persistida", headcount=5, manager_name="RH")
        )
    with Session(engine) as session, session.begin():
        scope(session, company)
        assert RepositoryBundle(session, company).area_repo.get_by_id("a").name == "Persistida"
        assert RepositoryBundle(session, uuid4()).area_repo.get_by_id("a") is None


def test_pgr_decision_persists_and_cannot_repeat(engine):
    from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO
    from app.application.use_cases.register_pgr_action_use_case import CardStateError
    from app.presentation.deps import PulsoAppContainer

    company = uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO empresa(id,nome) VALUES(:id,'Decisao')"), {"id": company})
    request = ResolveRiskCardRequestDTO(
        action_type="APROVAR_PGR", reviewer_name="RH", deadline_days=60
    )
    with Session(engine) as session, session.begin():
        scope(session, company)
        app = PulsoAppContainer(RepositoryBundle(session, company), seed=True)
        card_id = app.run_analysis_uc.execute("area_atend")["cardId"]
        item = app.register_pgr_uc.execute(card_id, request)
        item_id = item.item_id
    with Session(engine) as session, session.begin():
        scope(session, company)
        app = PulsoAppContainer(RepositoryBundle(session, company), seed=False)
        assert app.pgr_repo.get_by_id(item_id).risk_card_id == card_id
        with pytest.raises(CardStateError):
            app.register_pgr_uc.execute(card_id, request)
        assert len([i for i in app.pgr_repo.list_all() if i.risk_card_id == card_id]) == 1
