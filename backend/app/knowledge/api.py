"""Rotas /api/v1/conhecimento (o registro em main.py e a composicao em deps.py ficam com a
integracao).

Pontos de injecao (sobrescritos pela integracao via app.dependency_overrides ou deps.py):
- obter_contexto_conhecimento: ContextoAutorizado vindo da autenticacao. Por padrao: 401.
- obter_servico_conhecimento / obter_recuperador_conhecimento / obter_respondedor_conhecimento:
  componentes compostos. Por padrao: 503.
"""

from collections.abc import Callable
from typing import NoReturn, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.knowledge.domain import PAPEL_RH, CategoriaDocumento, ContextoAutorizado, ErroConhecimento
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
from app.knowledge.grounding import RespondedorFundamentado
from app.knowledge.retrieval import RecuperadorConhecimento
from app.knowledge.service import ServicoConhecimento

T = TypeVar("T")
router = APIRouter()


def obter_contexto_conhecimento() -> ContextoAutorizado:
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"codigo": "NAO_AUTENTICADO", "mensagem": "Autenticacao necessaria."},
    )


def _nao_configurado() -> NoReturn:
    raise HTTPException(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        detail={"codigo": "NAO_CONFIGURADO", "mensagem": "Base de conhecimento indisponivel."},
    )


def obter_servico_conhecimento() -> ServicoConhecimento:
    _nao_configurado()


def obter_recuperador_conhecimento() -> RecuperadorConhecimento:
    _nao_configurado()


def obter_respondedor_conhecimento() -> RespondedorFundamentado:
    _nao_configurado()


def _executar(acao: Callable[[], T]) -> T:
    try:
        return acao()
    except ErroConhecimento as erro:
        raise HTTPException(status_code=erro.status_http, detail=erro.como_dict()) from erro


def _exigir_rh(ctx: ContextoAutorizado) -> None:
    if PAPEL_RH not in ctx.papeis:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"codigo": "NAO_AUTORIZADO", "mensagem": "Acesso restrito ao RH."},
        )


Ctx = Depends(obter_contexto_conhecimento)
Svc = Depends(obter_servico_conhecimento)


@router.post("/documentos", response_model=DocumentoDTO, status_code=status.HTTP_201_CREATED)
def cadastrar_documento_texto(
    payload: CadastroTextoRequest, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> DocumentoDTO:
    """Cadastra um documento a partir de texto colado e ja processa a versao 1."""
    return _executar(lambda: svc.cadastrar_texto(ctx, payload))


@router.get("/documentos", response_model=list[DocumentoDTO])
def listar_documentos(
    categoria: CategoriaDocumento | None = Query(default=None),
    ctx: ContextoAutorizado = Ctx,
    svc: ServicoConhecimento = Svc,
) -> list[DocumentoDTO]:
    return _executar(lambda: svc.listar(ctx, categoria))


@router.get("/documentos/{documento_id}", response_model=DocumentoDTO)
def obter_documento(
    documento_id: UUID, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> DocumentoDTO:
    return _executar(lambda: svc.obter(ctx, documento_id))


@router.patch("/documentos/{documento_id}", response_model=DocumentoDTO)
def atualizar_metadados(
    documento_id: UUID,
    payload: AtualizarMetadadosRequest,
    ctx: ContextoAutorizado = Ctx,
    svc: ServicoConhecimento = Svc,
) -> DocumentoDTO:
    return _executar(lambda: svc.atualizar_metadados(ctx, documento_id, payload))


@router.post(
    "/documentos/{documento_id}/versoes",
    response_model=DocumentoDTO,
    status_code=status.HTTP_201_CREATED,
)
def adicionar_versao_texto(
    documento_id: UUID,
    payload: NovaVersaoTextoRequest,
    ctx: ContextoAutorizado = Ctx,
    svc: ServicoConhecimento = Svc,
) -> DocumentoDTO:
    """Substituicao: cria a versao seguinte. A anterior continua publicada ate a nova ser publicada."""
    return _executar(lambda: svc.adicionar_versao_texto(ctx, documento_id, payload))


@router.post("/versoes/{versao_id}/publicar", response_model=DocumentoDTO)
def publicar_versao(
    versao_id: UUID, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> DocumentoDTO:
    return _executar(lambda: svc.publicar(ctx, versao_id))


@router.post("/versoes/{versao_id}/despublicar", response_model=DocumentoDTO)
def despublicar_versao(
    versao_id: UUID, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> DocumentoDTO:
    return _executar(lambda: svc.despublicar(ctx, versao_id))


@router.post("/versoes/{versao_id}/reprocessar", response_model=VersaoDTO)
def reprocessar_versao(
    versao_id: UUID, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> VersaoDTO:
    return _executar(lambda: svc.reprocessar(ctx, versao_id))


@router.delete("/documentos/{documento_id}", status_code=status.HTTP_204_NO_CONTENT)
def excluir_documento(
    documento_id: UUID, ctx: ContextoAutorizado = Ctx, svc: ServicoConhecimento = Svc
) -> None:
    """Exclusao efetiva e irreversivel: original, versoes e trechos."""
    _executar(lambda: svc.excluir(ctx, documento_id))


@router.post("/buscar", response_model=ResultadoRecuperacao)
def buscar_trechos(
    payload: ConsultaRecuperacao,
    ctx: ContextoAutorizado = Ctx,
    recuperador: RecuperadorConhecimento = Depends(obter_recuperador_conhecimento),
) -> ResultadoRecuperacao:
    """Pre-visualizacao para o RH conferir o que o agente recuperaria."""
    _exigir_rh(ctx)
    return _executar(lambda: recuperador.buscar(ctx, payload))


@router.post("/responder", response_model=RespostaFundamentadaDTO)
def responder_com_fontes(
    payload: PerguntaRequest,
    ctx: ContextoAutorizado = Ctx,
    respondedor: RespondedorFundamentado = Depends(obter_respondedor_conhecimento),
) -> RespostaFundamentadaDTO:
    """Resposta com citacoes validadas (sem indicadores; o card/chat passam indicadores)."""
    _exigir_rh(ctx)
    return _executar(lambda: respondedor.responder(ctx, payload))
