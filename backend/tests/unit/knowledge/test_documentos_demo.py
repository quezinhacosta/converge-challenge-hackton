"""A base da demonstracao cobre todos os fatores: nenhuma lacuna aparece no ciclo."""

from datetime import date

from app.digital_worker.demo import DOCUMENTOS
from app.knowledge.domain import StatusVersao
from app.knowledge.dtos import CadastroTextoRequest
from app.knowledge.text_search import EXPANSAO_POR_FATOR
from app.knowledge.worker import AssistenteDocumental

from .fixtures import Ambiente, ctx

DIA = date(2026, 11, 8)


def _base_demo() -> tuple[Ambiente, AssistenteDocumental]:
    amb = Ambiente()
    for titulo, categoria, texto in DOCUMENTOS:
        doc = amb.servico.cadastrar_texto(
            ctx(),
            CadastroTextoRequest(
                titulo=titulo,
                categoria=categoria,
                responsavel="RH Corporativo (demo)",
                texto=texto,
                vigencia_inicio=date(2026, 1, 1),
                confirma_sem_dados_sensiveis=True,
            ),
        )
        versao = doc.versoes[-1]
        assert versao.status == StatusVersao.PRONTO, (titulo, versao.erro_mensagem)
        amb.servico.publicar(ctx(), versao.id)
    return amb, AssistenteDocumental(amb.recuperador, amb.repo, amb.servico)


def test_todo_fator_tem_acao_e_politica_na_demo() -> None:
    _, assistente = _base_demo()
    for fator in EXPANSAO_POR_FATOR:
        if fator == "ASSEDIO":
            continue  # assedio segue o fluxo de compliance, fora da fila do RH
        inv = assistente.investigar(ctx(), fator, dia=DIA)
        assert inv.tem_acao_da_empresa, fator
        assert not inv.lacunas, (fator, inv.lacunas)


def test_revisao_da_base_demo_sem_pendencias() -> None:
    _, assistente = _base_demo()
    pendencias = assistente.revisar_base(ctx(), DIA).pendencias
    assert [p.tipo for p in pendencias] == []
