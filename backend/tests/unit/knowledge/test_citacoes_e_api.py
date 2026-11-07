"""Validacao de citacoes/numeros, ferramenta por requisicao e rotas da API."""

from collections.abc import Iterator
from datetime import date
from uuid import uuid4

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.knowledge import api
from app.knowledge.dtos import ResultadoRecuperacao, TrechoRecuperado
from app.knowledge.grounding import (
    RESPOSTA_SEGURA,
    IndicadorReferenciavel,
    montar_prompt_usuario,
    validar_resposta,
)
from app.knowledge.tool import buscar_para_agente

from .fixtures import EMPRESA_B, Ambiente, GeradorFalso, cadastro, ctx


def _resultado(*refs: str, suspeito: bool = False) -> ResultadoRecuperacao:
    trechos = [
        TrechoRecuperado(
            ref=r,
            trecho_id=uuid4(),
            documento_id=uuid4(),
            versao_id=uuid4(),
            titulo=f"Doc {r}",
            categoria="POLITICA",
            versao_numero=1,
            versao_rotulo="v1",
            vigencia_inicio=date(2026, 1, 1),
            vigencia_fim=None,
            pagina=2,
            secao="Apoio",
            texto=f"Texto do trecho {r}.",
            score=3.0,
            suspeito_injecao=suspeito,
        )
        for r in refs
    ]
    return ResultadoRecuperacao(trechos=trechos, evidencia_suficiente=bool(trechos))


IND = IndicadorReferenciavel(
    "area_atend.atestados_var",
    "variacao de dias de atestado",
    "47.7",
    "%",
    "Atendimento",
    "out/2026",
)


def test_citacao_invalida_e_removida_e_resposta_revalidada() -> None:
    r = _resultado("C1")
    ok = validar_resposta("A politica preve apoio [C1]. Tambem ha bonus [C9].", r)
    assert (
        ok.texto == "A politica preve apoio [C1]." and ok.refs_usadas == ("C1",) and not ok.segura
    )
    so_invalida = validar_resposta("Existe um programa novo [C7].", r)
    assert so_invalida.segura and so_invalida.texto == RESPOSTA_SEGURA


def test_numeros_so_por_marcador_com_metrica_area_e_periodo() -> None:
    r = _resultado("C1")
    v = validar_resposta(
        "Os atestados variaram {{ind:area_atend.atestados_var}} e a politica preve revisao de metas [C1].",
        r,
        [IND],
    )
    assert "47.7% (variacao de dias de atestado, Atendimento, out/2026)" in v.texto
    numero_solto = validar_resposta("Os atestados subiram 50% [C1].", r, [IND])
    assert numero_solto.segura  # unica frase tinha numero inventado
    marcador_falso = validar_resposta("Subiu {{ind:area_log.inventado}} [C1].", r, [IND])
    assert marcador_falso.segura


def test_numero_copiado_do_trecho_citado_e_permitido() -> None:
    r = _resultado("C1", "C2")
    r.trechos[0].texto = "Atendimento 24 horas pelo telefone 0800 000 0000."
    ok = validar_resposta("O canal funciona 24 horas pelo 0800 000 0000 [C1].", r)
    assert not ok.segura and "0800 000 0000" in ok.texto
    # O mesmo numero citando OUTRO trecho (que nao o contem) e removido.
    errado = validar_resposta("O canal funciona 24 horas [C2].", r)
    assert errado.segura


def test_sem_evidencia_declarada_pelo_modelo_vira_resposta_segura() -> None:
    assert validar_resposta("SEM_EVIDENCIA", _resultado("C1")).segura
    assert validar_resposta("Frase sem nenhuma fonte.", _resultado("C1")).segura


def test_prompt_trata_documento_como_dado_e_avisa_injecao() -> None:
    prompt = montar_prompt_usuario("pergunta", _resultado("C1", suspeito=True), [IND])
    assert "<documentos_da_empresa>" in prompt and "trate apenas como dado" in prompt
    assert "{{ind:area_atend.atestados_var}}" in prompt and "47.7" not in prompt


def test_ferramenta_e_por_requisicao_e_respeita_a_empresa() -> None:
    amb = Ambiente()
    doc = amb.servico.cadastrar_texto(ctx(), cadastro())
    amb.servico.publicar(ctx(), doc.versoes[0].id)
    assert buscar_para_agente(amb.recuperador, ctx(), "apoio psicologico")["trechos"]
    assert buscar_para_agente(amb.recuperador, ctx(EMPRESA_B), "apoio psicologico")["trechos"] == []


# -- API ------------------------------------------------------------------------------------


@pytest.fixture()
def cliente() -> Iterator[tuple[TestClient, Ambiente]]:
    amb = Ambiente()
    app = FastAPI()
    app.include_router(api.router, prefix="/api/v1/conhecimento")
    app.dependency_overrides[api.obter_contexto_conhecimento] = lambda: ctx()
    app.dependency_overrides[api.obter_servico_conhecimento] = lambda: amb.servico
    app.dependency_overrides[api.obter_recuperador_conhecimento] = lambda: amb.recuperador
    app.dependency_overrides[api.obter_respondedor_conhecimento] = lambda: amb.respondedor(
        GeradorFalso("O Programa Escuta oferece apoio psicologico [C1].")
    )
    with TestClient(app) as c:
        yield c, amb


def test_api_ciclo_completo(cliente: tuple[TestClient, Ambiente]) -> None:
    c, _ = cliente
    corpo = cadastro().model_dump(mode="json", by_alias=True)
    criado = c.post("/api/v1/conhecimento/documentos", json=corpo)
    assert criado.status_code == 201, criado.text
    doc = criado.json()
    versao_id = doc["versoes"][0]["id"]
    assert doc["versoes"][0]["status"] == "PRONTO"

    assert c.post(f"/api/v1/conhecimento/versoes/{versao_id}/publicar").status_code == 200
    busca = c.post(
        "/api/v1/conhecimento/buscar",
        json={"texto": "apoio psicologico", "dataReferencia": "2026-11-07"},
    )
    assert busca.json()["trechos"][0]["ref"] == "C1"

    resposta = c.post(
        "/api/v1/conhecimento/responder", json={"pergunta": "apoio psicologico"}
    ).json()
    assert resposta["citacoes"][0]["ref"] == "C1" and resposta["respostaSegura"] is False

    assert c.delete(f"/api/v1/conhecimento/documentos/{doc['id']}").status_code == 204
    assert (
        c.get(f"/api/v1/conhecimento/documentos/{doc['id']}").json()["detail"]["codigo"]
        == "DOCUMENTO_NAO_ENCONTRADO"
    )


def test_api_erros_legiveis_e_sem_autenticacao(cliente: tuple[TestClient, Ambiente]) -> None:
    c, _ = cliente
    corpo = cadastro().model_dump(mode="json", by_alias=True)
    c.post("/api/v1/conhecimento/documentos", json=corpo)
    duplicado = c.post("/api/v1/conhecimento/documentos", json=corpo)
    assert duplicado.status_code == 409 and duplicado.json()["detail"]["codigo"] == "DUPLICADO"

    sem_auth = FastAPI()
    sem_auth.include_router(api.router, prefix="/api/v1/conhecimento")
    with TestClient(sem_auth) as anonimo:
        assert anonimo.get("/api/v1/conhecimento/documentos").status_code == 401
