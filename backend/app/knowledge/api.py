"""Rotas /api/v1/conhecimento.

Identidade e transacao vem da base compartilhada (Codex):
- `require_authorized_context`: ContextoAutorizado resolvido no servidor (nunca pelo body).
- `request_session`: a mesma Session (com empresa no RLS) em toda a requisicao.
- `get_knowledge_services`: chama a factory registrada no KnowledgeIntegration.
Sem binding registrado, as rotas respondem 503.
"""

from collections.abc import Callable
from dataclasses import asdict
from datetime import date
from typing import Any, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session

from app.knowledge.domain import (
    PAPEL_RH,
    CategoriaDocumento,
    ContextoAutorizado,
    ErroConhecimento,
    StatusVersao,
)
from app.knowledge.dtos import (
    AtualizarMetadadosRequest,
    CadastroTextoRequest,
    ConsultaRecuperacao,
    DocumentoDTO,
    NovaVersaoTextoRequest,
    PerguntaRequest,
    RespostaFundamentadaDTO,
    ResultadoRecuperacao,
    VersaoDTO,
)
from app.knowledge.integration import ServicosDocumentais
from app.presentation.knowledge_integration import get_knowledge_services
from app.presentation.security import request_session, require_authorized_context

T = TypeVar("T")
router = APIRouter()


def servicos_da_requisicao(
    request: Request,
    ctx: ContextoAutorizado = Depends(require_authorized_context),
    session: Session | None = Depends(request_session, scope="function"),
) -> ServicosDocumentais:
    servicos = get_knowledge_services(request, ctx, session)
    if not isinstance(servicos, ServicosDocumentais):
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"codigo": "NAO_CONFIGURADO", "mensagem": "Base de conhecimento indisponivel."},
        )
    if PAPEL_RH not in servicos.ctx.papeis:
        raise HTTPException(
            status.HTTP_403_FORBIDDEN,
            {"codigo": "NAO_AUTORIZADO", "mensagem": "Acesso restrito ao RH."},
        )
    return servicos


S = Depends(servicos_da_requisicao)


def _executar(acao: Callable[[], T]) -> T:
    try:
        return acao()
    except ErroConhecimento as erro:
        raise HTTPException(status_code=erro.status_http, detail=erro.como_dict()) from erro


@router.get("/status")
def status_da_base(s: ServicosDocumentais = S) -> dict[str, Any]:
    docs = _executar(lambda: s.servico.listar(s.ctx))
    return {
        "disponivel": True,
        "documentos": len(docs),
        "publicados": sum(1 for d in docs if d.versao_publicada),
        "comErroOuBloqueio": sum(
            1
            for d in docs
            if d.versoes and d.versoes[-1].status in (StatusVersao.ERRO, StatusVersao.BLOQUEADO)
        ),
    }


@router.post("/documentos", response_model=DocumentoDTO, status_code=status.HTTP_201_CREATED)
def cadastrar_documento_texto(
    payload: CadastroTextoRequest, s: ServicosDocumentais = S
) -> DocumentoDTO:
    """Cadastra um documento a partir de texto colado e ja processa a versao 1."""
    return _executar(lambda: s.servico.cadastrar_texto(s.ctx, payload))


@router.get("/documentos", response_model=list[DocumentoDTO])
def listar_documentos(
    categoria: CategoriaDocumento | None = Query(default=None), s: ServicosDocumentais = S
) -> list[DocumentoDTO]:
    return _executar(lambda: s.servico.listar(s.ctx, categoria))


@router.get("/documentos/{documento_id}", response_model=DocumentoDTO)
def obter_documento(documento_id: UUID, s: ServicosDocumentais = S) -> DocumentoDTO:
    return _executar(lambda: s.servico.obter(s.ctx, documento_id))


@router.patch("/documentos/{documento_id}", response_model=DocumentoDTO)
def atualizar_metadados(
    documento_id: UUID, payload: AtualizarMetadadosRequest, s: ServicosDocumentais = S
) -> DocumentoDTO:
    return _executar(lambda: s.servico.atualizar_metadados(s.ctx, documento_id, payload))


@router.post(
    "/documentos/{documento_id}/versoes",
    response_model=DocumentoDTO,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_versao_texto(
    documento_id: UUID, payload: NovaVersaoTextoRequest, s: ServicosDocumentais = S
) -> DocumentoDTO:
    """Substituicao: cria a versao seguinte; a anterior vale ate a nova ser publicada."""
    return _executar(lambda: s.servico.adicionar_versao_texto(s.ctx, documento_id, payload))


@router.post("/versoes/{versao_id}/publicar", response_model=DocumentoDTO)
def publicar_versao(versao_id: UUID, s: ServicosDocumentais = S) -> DocumentoDTO:
    return _executar(lambda: s.servico.publicar(s.ctx, versao_id))


@router.post("/versoes/{versao_id}/despublicar", response_model=DocumentoDTO)
def despublicar_versao(versao_id: UUID, s: ServicosDocumentais = S) -> DocumentoDTO:
    return _executar(lambda: s.servico.despublicar(s.ctx, versao_id))


@router.post("/versoes/{versao_id}/reprocessar", response_model=VersaoDTO)
def reprocessar_versao(versao_id: UUID, s: ServicosDocumentais = S) -> VersaoDTO:
    return _executar(lambda: s.servico.reprocessar(s.ctx, versao_id))


@router.delete("/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(documento_id: UUID, s: ServicosDocumentais = S) -> None:
    """Exclusao efetiva e irreversivel: original, versoes e trechos."""
    _executar(lambda: s.servico.excluir(s.ctx, documento_id))


@router.post("/buscar", response_model=ResultadoRecuperacao)
def buscar_trechos(
    payload: ConsultaRecuperacao, s: ServicosDocumentais = S
) -> ResultadoRecuperacao:
    """Pre-visualizacao para o RH conferir o que o agente recuperaria."""
    return _executar(lambda: s.recuperador.buscar(s.ctx, payload))


@router.post("/responder", response_model=RespostaFundamentadaDTO)
def responder_com_fontes(
    payload: PerguntaRequest, s: ServicosDocumentais = S
) -> RespostaFundamentadaDTO:
    return _executar(lambda: s.respondedor.responder(s.ctx, payload))


@router.get("/pendencias")
def pendencias_da_base(
    dia: date | None = Query(default=None), s: ServicosDocumentais = S
) -> dict[str, Any]:
    """Tarefas de manutencao da base que o worker gera para os responsaveis."""
    relatorio = _executar(lambda: s.assistente.revisar_base(s.ctx, dia))
    return {
        "geradoEm": relatorio.gerado_em.isoformat(),
        "pendencias": [
            {k: (v.isoformat() if isinstance(v, date) else v) for k, v in asdict(p).items()}
            for p in relatorio.pendencias
        ],
    }


@router.get("/investigar")
def investigar_fator(
    fator: str = Query(min_length=3, max_length=40),
    area: str | None = Query(default=None, max_length=120),
    s: ServicosDocumentais = S,
) -> dict[str, Any]:
    """O que a empresa oferece, ja tentou e define para um fator de risco (com referencias)."""
    inv = _executar(lambda: s.assistente.investigar(s.ctx, fator, area))
    trechos = inv.trechos()
    return {
        "fator": inv.fator,
        "temAcaoDaEmpresa": inv.tem_acao_da_empresa,
        "lacunas": inv.lacunas,
        "trechos": [t.model_dump(mode="json", by_alias=True) for t in trechos],
    }
