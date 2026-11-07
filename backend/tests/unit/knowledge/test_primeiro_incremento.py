"""Primeiro incremento: cadastrar -> processar -> recuperar autorizado -> responder com citacao
-> atualizar/excluir sem recuperar conteudo obsoleto."""

from datetime import date

import pytest

from app.knowledge.domain import ErroConhecimento, StatusVersao
from app.knowledge.dtos import ConsultaRecuperacao, NovaVersaoTextoRequest, PerguntaRequest

from .fixtures import EMPRESA_B, POLITICA_APOIO_V2, Ambiente, GeradorFalso, cadastro, ctx

CONSULTA = ConsultaRecuperacao(texto="apoio psicologico", data_referencia=date(2026, 11, 7))


def _buscar(amb: Ambiente, contexto=None, texto: str = "apoio psicologico"):
    return amb.recuperador.buscar(
        contexto or ctx(), ConsultaRecuperacao(texto=texto, data_referencia=date(2026, 11, 7))
    )


def test_ciclo_completo_com_versao_e_exclusao() -> None:
    amb = Ambiente()
    doc = amb.servico.cadastrar_texto(ctx(), cadastro())
    v1 = doc.versoes[0]
    assert v1.status == StatusVersao.PRONTO and v1.quantidade_trechos >= 2

    # Nao publicado: nao e recuperavel.
    assert _buscar(amb).evidencia_suficiente is False

    amb.servico.publicar(ctx(), v1.id)
    resultado = _buscar(amb)
    assert resultado.evidencia_suficiente
    topo = resultado.trechos[0]
    assert topo.ref == "C1" and topo.secao == "Canais de apoio" and "Programa Escuta" in topo.texto

    # Resposta com citacao validada.
    gerador = GeradorFalso("O Programa Escuta oferece apoio psicologico gratuito [C1].")
    resposta = amb.respondedor(gerador).responder(
        ctx(), PerguntaRequest(pergunta="Qual o canal de apoio psicologico?")
    )
    assert resposta.resposta_segura is False
    assert [c.ref for c in resposta.citacoes] == ["C1"]
    assert resposta.citacoes[0].versao_rotulo == "v1"

    # Nova versao: enquanto nao publicada, a v1 continua valendo.
    doc = amb.servico.adicionar_versao_texto(
        ctx(),
        doc.id,
        NovaVersaoTextoRequest(
            texto=POLITICA_APOIO_V2,
            vigencia_inicio=date(2026, 1, 1),
            confirma_sem_dados_sensiveis=True,
        ),
    )
    v2 = doc.versoes[1]
    assert "Programa Escuta" in _buscar(amb).trechos[0].texto

    # Publicada a v2, o conteudo da v1 nunca mais aparece.
    doc = amb.servico.publicar(ctx(), v2.id)
    assert {v.numero: v.status for v in doc.versoes}[1] == StatusVersao.SUBSTITUIDA
    textos = " ".join(
        t.texto for t in _buscar(amb, texto="Programa Escuta apoio psicologico").trechos
    )
    assert "Programa Cuidar" in textos and "Programa Escuta oferece" not in textos

    # Exclusao efetiva: nada no indice nem no armazenamento; auditoria sem titulo.
    amb.servico.excluir(ctx(), doc.id)
    assert list(amb.repo.todos_os_trechos()) == []
    assert amb.armazenamento.quantidade() == 0
    assert _buscar(amb).evidencia_suficiente is False
    excluido = [e for e in amb.repo.eventos if e.acao == "EXCLUIDO"]
    assert excluido and "titulo" not in excluido[0].detalhe


def test_isolamento_entre_empresas() -> None:
    amb = Ambiente()
    doc = amb.servico.cadastrar_texto(ctx(), cadastro())
    amb.servico.publicar(ctx(), doc.versoes[0].id)
    assert _buscar(amb, ctx(EMPRESA_B)).trechos == []
    with pytest.raises(ErroConhecimento) as erro:
        amb.servico.obter(ctx(EMPRESA_B), doc.id)
    assert erro.value.codigo == "DOCUMENTO_NAO_ENCONTRADO"


def test_vigencia_e_despublicacao() -> None:
    amb = Ambiente()
    vencido = amb.servico.cadastrar_texto(
        ctx(), cadastro(vigencia_inicio=date(2025, 1, 1), vigencia_fim=date(2026, 1, 1))
    )
    amb.servico.publicar(ctx(), vencido.versoes[0].id)
    assert _buscar(amb).evidencia_suficiente is False

    futuro = amb.servico.cadastrar_texto(
        ctx(), cadastro(texto=POLITICA_APOIO_V2, vigencia_inicio=date(2027, 1, 1))
    )
    amb.servico.publicar(ctx(), futuro.versoes[0].id)
    assert _buscar(amb).evidencia_suficiente is False

    atual = amb.servico.cadastrar_texto(
        ctx(), cadastro(texto="# Canais de apoio\n\nApoio psicologico pelo Programa Ouvir.")
    )
    amb.servico.publicar(ctx(), atual.versoes[0].id)
    assert _buscar(amb).evidencia_suficiente
    amb.servico.despublicar(ctx(), atual.versoes[0].id)
    assert _buscar(amb).evidencia_suficiente is False


def test_sem_evidencia_nao_chama_o_modelo() -> None:
    amb = Ambiente()
    gerador = GeradorFalso("qualquer coisa [C1]")
    resposta = amb.respondedor(gerador).responder(
        ctx(), PerguntaRequest(pergunta="Qual o canal de apoio?")
    )
    assert resposta.resposta_segura and resposta.citacoes == [] and gerador.chamadas == []


def test_modelo_fora_do_ar_usa_resposta_extrativa_com_citacao() -> None:
    amb = Ambiente()
    doc = amb.servico.cadastrar_texto(ctx(), cadastro())
    amb.servico.publicar(ctx(), doc.versoes[0].id)
    resposta = amb.respondedor(GeradorFalso(falhar=True)).responder(
        ctx(), PerguntaRequest(pergunta="apoio psicologico")
    )
    assert resposta.citacoes and "[C1]" in resposta.texto
    assert any("nao respondeu" in a for a in resposta.avisos)
