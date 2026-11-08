"""Repositorio documental no PostgreSQL real (migration 0001, RLS, FTS, cascata).

Requer banco DESCARTAVEL em VYTAI_TEST_DATABASE_URL (nunca producao). Sem a variavel, pula.
"""

import os
import subprocess
import sys
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.knowledge.domain import ContextoAutorizado, StatusVersao
from app.knowledge.dtos import ConsultaRecuperacao, NovaVersaoTextoRequest, PerguntaRequest
from app.knowledge.integration import montar_servicos
from app.knowledge.sql_repository import RepositorioConhecimentoSQL
from tests.unit.knowledge.fixtures import POLITICA_APOIO, POLITICA_APOIO_V2, GeradorFalso, cadastro

URL = os.getenv("VYTAI_TEST_DATABASE_URL")
pytestmark = pytest.mark.skipif(not URL, reason="PostgreSQL de teste nao configurado")
DIA = date(2026, 11, 7)


@pytest.fixture(scope="module")
def engine():
    subprocess.run(
        [sys.executable, "-m", "alembic", "upgrade", "head"],
        cwd=Path(__file__).resolve().parents[2],
        env=os.environ | {"DATABASE_URL": URL},
        check=True,
        capture_output=True,
    )
    eng = create_engine(URL)
    yield eng
    eng.dispose()


def _empresa(engine) -> ContextoAutorizado:
    empresa = uuid4()
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO empresa(id,nome) VALUES(:id,'Teste RAG')"), {"id": empresa})
    return ContextoAutorizado(empresa, uuid4(), frozenset({"RH"}), frozenset({"RH"}), "req")


def _sessao(engine, ctx: ContextoAutorizado):
    """Igual ao request_session: papel sem bypass de RLS + empresa da requisicao."""
    session = Session(engine)
    session.begin()
    session.execute(text("SET LOCAL ROLE vytai_app"))
    session.execute(
        text("SELECT set_config('vytai.empresa_id',:e,true)"), {"e": str(ctx.empresa_id)}
    )
    return session


def _servicos(session, ctx):
    repo = RepositorioConhecimentoSQL(session)
    return montar_servicos(ctx, repo, repo, GeradorFalso("O Programa Escuta oferece apoio [C1]."))


def test_ciclo_completo_no_postgres(engine):
    ctx = _empresa(engine)
    with _sessao(engine, ctx) as s:
        sv = _servicos(s, ctx)
        doc = sv.servico.cadastrar_texto(ctx, cadastro(texto=POLITICA_APOIO))
        v1 = doc.versoes[0]
        assert v1.status == StatusVersao.PRONTO and v1.quantidade_trechos >= 2
        sv.servico.publicar(ctx, v1.id)
        s.commit()

    with _sessao(engine, ctx) as s:
        sv = _servicos(s, ctx)
        r = sv.recuperador.buscar(
            ctx, ConsultaRecuperacao(texto="apoio psicologico", data_referencia=DIA)
        )
        assert r.evidencia_suficiente and "Programa Escuta" in r.trechos[0].texto
        resposta = sv.respondedor.responder(ctx, PerguntaRequest(pergunta="apoio psicologico"))
        assert resposta.citacoes and not resposta.resposta_segura

        doc = sv.servico.adicionar_versao_texto(
            ctx,
            doc.id,
            NovaVersaoTextoRequest(
                texto=POLITICA_APOIO_V2,
                vigencia_inicio=date(2026, 1, 1),
                confirma_sem_dados_sensiveis=True,
            ),
        )
        sv.servico.publicar(ctx, doc.versoes[1].id)
        textos = " ".join(
            t.texto
            for t in sv.recuperador.buscar(
                ctx,
                ConsultaRecuperacao(texto="Programa Escuta apoio psicologico", data_referencia=DIA),
            ).trechos
        )
        assert "Programa Cuidar" in textos and "Programa Escuta oferece" not in textos
        s.commit()

    with _sessao(engine, ctx) as s:
        sv = _servicos(s, ctx)
        sv.servico.excluir(ctx, doc.id)
        s.commit()

    with engine.begin() as conn:  # conta administrativa: nada ficou para tras
        for tabela in ("documento_versao", "documento_arquivo", "documento_trecho"):
            n = conn.execute(
                text(f"SELECT count(*) FROM {tabela} WHERE empresa_id=:e"), {"e": ctx.empresa_id}
            ).scalar_one()
            assert n == 0, tabela
        eventos = (
            conn.execute(
                text("SELECT acao FROM documento_evento WHERE empresa_id=:e"), {"e": ctx.empresa_id}
            )
            .scalars()
            .all()
        )
        assert "EXCLUIDO" in eventos


def test_rls_isola_empresas_e_bloqueio_remove_original(engine):
    a, b = _empresa(engine), _empresa(engine)
    with _sessao(engine, a) as s:
        sv = _servicos(s, a)
        doc = sv.servico.cadastrar_texto(a, cadastro(texto=POLITICA_APOIO))
        sv.servico.publicar(a, doc.versoes[0].id)
        bloqueado = sv.servico.cadastrar_texto(
            a, cadastro(texto="Laudo do Joao anexado.", titulo="Laudo")
        )
        assert bloqueado.versoes[0].status == StatusVersao.BLOQUEADO
        s.commit()

    with _sessao(engine, b) as s:  # empresa B, mesma consulta: RLS + filtro explicito
        sv = _servicos(s, b)
        r = sv.recuperador.buscar(
            b, ConsultaRecuperacao(texto="apoio psicologico", data_referencia=DIA)
        )
        assert r.trechos == []
        n = s.execute(text("SELECT count(*) FROM documento")).scalar_one()
        assert n == 0  # RLS: B nao enxerga nenhuma linha de A

    with engine.begin() as conn:
        assert (
            conn.execute(
                text("SELECT count(*) FROM documento_arquivo WHERE versao_id=:v"),
                {"v": bloqueado.versoes[0].id},
            ).scalar_one()
            == 0
        )


def test_reivindicacao_concorrente_processa_uma_vez(engine):
    from datetime import UTC, datetime, timedelta

    ctx = _empresa(engine)
    with _sessao(engine, ctx) as s:
        sv = _servicos(s, ctx)
        doc = sv.servico.cadastrar_texto(ctx, cadastro(texto=POLITICA_APOIO))
        s.commit()
    versao_id = doc.versoes[0].id
    with _sessao(engine, ctx) as s:
        s.execute(text("UPDATE documento_versao SET status='ERRO' WHERE id=:v"), {"v": versao_id})
        s.commit()
    agora = datetime.now(UTC)
    with _sessao(engine, ctx) as s1, _sessao(engine, ctx) as s2:
        primeiro = RepositorioConhecimentoSQL(s1).reivindicar_processamento(
            ctx.empresa_id, versao_id, agora, agora - timedelta(minutes=10)
        )
        s1.commit()
        segundo = RepositorioConhecimentoSQL(s2).reivindicar_processamento(
            ctx.empresa_id, versao_id, agora, agora - timedelta(minutes=10)
        )
        assert primeiro is not None and segundo is None
