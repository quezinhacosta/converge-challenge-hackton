"""Digital worker (investigacao, catalogo, cuidado da base, memoria) e integracao com o chat."""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from uuid import uuid4

from app.application.contracts.indicators import IndicadoresArea, PeriodoAnalise, VariacaoIndicador
from app.application.dtos.chat_dto import ChatQueryResponseDTO
from app.knowledge.domain import CategoriaDocumento, StatusVersao
from app.knowledge.indicadores import indicadores_para_prompt
from app.knowledge.integration import fabrica_em_memoria
from app.knowledge.worker import AssistenteDocumental

from .fixtures import EMPRESA_B, POLITICA_APOIO, Ambiente, cadastro, ctx

HOJE = date(2026, 11, 7)

PROGRAMA = """# Programa Escuta

Atendimento psicologico gratuito para colaboradores, com apoio em casos de sobrecarga e
ansiedade. Agendamento pelo canal interno de apoio.
"""
PLANO_2025 = """# Plano Atendimento 2025

Em 2025 a revisao de metas com a lideranca reduziu a sobrecarga do atendimento; a troca de
escala nao teve efeito.
"""


def _publicar(amb: Ambiente, texto: str, categoria: CategoriaDocumento, **extra: object) -> str:
    doc = amb.servico.cadastrar_texto(
        ctx(),
        cadastro(
            texto=texto,
            titulo=extra.pop("titulo", f"Doc {categoria}"),
            categoria=categoria,
            **extra,
        ),
    )
    amb.servico.publicar(ctx(), doc.versoes[0].id)
    return str(doc.id)


def _assistente(amb: Ambiente) -> AssistenteDocumental:
    return AssistenteDocumental(amb.recuperador, amb.repo, amb.servico)


def test_investigacao_traz_o_que_a_empresa_oferece_e_ja_tentou() -> None:
    amb = Ambiente()
    _publicar(amb, PROGRAMA, CategoriaDocumento.PROGRAMA_BENEFICIO, titulo="Programa Escuta")
    _publicar(amb, PLANO_2025, CategoriaDocumento.PLANO_ACAO_ANTERIOR, titulo="Plano 2025")
    inv = _assistente(amb).investigar(ctx(), "SOBRECARGA_METAS", "Atendimento", dia=HOJE)
    assert inv.tem_acao_da_empresa
    assert inv.acoes_disponiveis[0].titulo_documento == "Programa Escuta"
    assert inv.planos_anteriores and "2025" in inv.planos_anteriores[0].texto
    assert "Nenhuma política publicada sobre este fator." in inv.lacunas
    refs = [t.ref for t in inv.trechos()]
    assert refs == [f"C{i}" for i in range(1, len(refs) + 1)]
    # Outra empresa nao ve nada disso.
    assert (
        not _assistente(amb)
        .investigar(ctx(EMPRESA_B), "SOBRECARGA_METAS", dia=HOJE)
        .acoes_disponiveis
    )


def test_cuidado_da_base_gera_pendencias_com_responsavel() -> None:
    amb = Ambiente()
    _publicar(
        amb,
        POLITICA_APOIO,
        CategoriaDocumento.CANAL_APOIO,
        titulo="Canal de apoio",
        vigencia_inicio=date(2026, 1, 1),
        vigencia_fim=HOJE + timedelta(days=10),
    )
    _publicar(
        amb,
        PLANO_2025,
        CategoriaDocumento.POLITICA,
        titulo="Politica antiga",
        vigencia_inicio=date(2025, 1, 1),
        vigencia_fim=date(2026, 1, 1),
    )
    sensivel = amb.servico.cadastrar_texto(
        ctx(), cadastro(texto="Laudo do Joao anexado.", titulo="Laudo")
    )
    assert sensivel.versoes[0].status == StatusVersao.BLOQUEADO

    relatorio = _assistente(amb).revisar_base(ctx(), HOJE)
    tipos = {p.tipo for p in relatorio.pendencias}
    assert {"VENCENDO", "VENCIDO_PUBLICADO", "BLOQUEADO_SENSIVEL", "LACUNA_FATOR"} <= tipos
    vencendo = relatorio.por_tipo("VENCENDO")[0]
    assert vencendo.responsavel == "RH Corporativo" and vencendo.prazo == HOJE + timedelta(days=10)
    assert "Joao" not in relatorio.por_tipo("BLOQUEADO_SENSIVEL")[0].mensagem


def test_base_vazia_aponta_falta_de_canal_de_apoio() -> None:
    relatorio = _assistente(Ambiente()).revisar_base(ctx(), HOJE)
    assert relatorio.por_tipo("SEM_CANAL_DE_APOIO")


def test_decisao_do_rh_vira_memoria_citavel() -> None:
    amb = Ambiente()
    _assistente(amb).registrar_decisao(
        ctx(),
        area_nome="Atendimento",
        fator="SOBRECARGA_METAS",
        periodo="10/2026",
        decisao="APROVADA",
        acao="Revisao das metas semanais com a lideranca.",
        resultado="Sobrecarga reduziu no ciclo seguinte.",
    )
    inv = _assistente(amb).investigar(ctx(), "SOBRECARGA_METAS", "Atendimento", dia=date.today())
    assert any("Revisao das metas" in t.texto for t in inv.planos_anteriores)


def test_decisao_com_dado_pessoal_e_bloqueada() -> None:
    amb = Ambiente()
    _assistente(amb).registrar_decisao(
        ctx(),
        area_nome="Atendimento",
        fator="SOBRECARGA_METAS",
        periodo="10/2026",
        decisao="APROVADA",
        acao="Afastar a colaboradora CPF 529.982.247-25.",
    )
    assert list(amb.repo.todos_os_trechos()) == []


def test_servicos_sao_por_requisicao_e_finalize_chat_valida_citacoes() -> None:
    fabrica = fabrica_em_memoria()
    s1 = fabrica(ctx(), None)
    _ = s1.servico.cadastrar_texto(ctx(), cadastro())
    s1.servico.publicar(ctx(), s1.servico.listar(ctx())[0].versoes[0].id)

    s2 = fabrica(ctx(), None)
    assert s2 is not s1 and s2.registro == {}
    primeira = s2.buscar_registrando("apoio psicologico")
    segunda = s2.buscar_registrando("revisar metas sobrecarga")
    refs = [t["ref"] for t in primeira["trechos"] + segunda["trechos"]]
    assert len(refs) == len(set(refs))  # refs unicas entre chamadas da mesma requisicao

    resposta = ChatQueryResponseDTO(
        reply_text=(
            "A Logistica teve 5 pedidos de demissao. "
            "O Programa Escuta atende 24 horas [C1]. "
            "Existe um bonus de 3 salarios [C9]."
        ),
        sources_used=["ponto"],
    )
    final = s2.finalize_chat(resposta)
    assert "Logistica teve 5" in final.reply_text  # frase de outra ferramenta: intacta
    assert "24 horas [C1]" in final.reply_text and "[C9]" not in final.reply_text
    assert [c.ref for c in final.citacoes] == ["C1"]
    assert "base_conhecimento" in final.sources_used

    outra_empresa = fabrica(ctx(EMPRESA_B), None)
    assert outra_empresa.buscar_registrando("apoio psicologico")["trechos"] == []


def test_finalize_chat_numero_que_nao_esta_no_trecho_remove_a_frase() -> None:
    s = fabrica_em_memoria()(ctx(), None)
    s.servico.publicar(ctx(), s.servico.cadastrar_texto(ctx(), cadastro()).versoes[0].id)
    s.buscar_registrando("apoio psicologico")
    final = s.finalize_chat(ChatQueryResponseDTO(reply_text="O programa atende 48 horas [C1]."))
    assert final.citacoes == [] and "[C1]" not in final.reply_text


def test_indicadores_viram_marcadores_so_quando_elegiveis() -> None:
    periodo = PeriodoAnalise(inicio=date(2026, 10, 1), fim=date(2026, 11, 1))
    base = dict(
        snapshot_id=uuid4(),
        empresa_id=uuid4(),
        area_id="area_atend",
        periodo=periodo,
        calculado_em=datetime.now(UTC),
        versao_calculo="rules-v1-demo",
        origem_dados="DEMONSTRACAO",
    )
    elegivel = IndicadoresArea(
        **base,
        estado="ELEGIVEL",
        quorum_ok=True,
        score=Decimal("79.8"),
        nivel="VERMELHO",
        fator="SOBRECARGA_METAS",
        variacoes=(
            VariacaoIndicador(
                codigo="atestados",
                atual=Decimal("32"),
                delta_percentual=Decimal("47.70"),
                unidade="dias",
                qualidade="VALIDO",
            ),
            VariacaoIndicador(codigo="horas_extras", unidade="h", qualidade="INCOMPLETO"),
        ),
    )
    marcadores = {i.codigo: i for i in indicadores_para_prompt(elegivel, "Atendimento")}
    assert set(marcadores) == {
        "area_atend.score",
        "area_atend.atestados_var",
        "area_atend.atestados",
    }
    assert marcadores["area_atend.atestados_var"].renderizar() == (
        "47.7% (variacao de atestados contra a linha de base, Atendimento, 10/2026)"
    )
    bloqueado = IndicadoresArea(**base, estado="BLOQUEADO_PRIVACIDADE", quorum_ok=False)
    assert indicadores_para_prompt(bloqueado, "Design") == []
