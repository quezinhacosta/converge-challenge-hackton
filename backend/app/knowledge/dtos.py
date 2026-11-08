"""DTOs da API de conhecimento e do contrato de recuperacao/citacao (camelCase na API)."""

from datetime import date, datetime
from typing import Literal
from uuid import UUID

from pydantic import Field

from app.application.dtos.citation_dto import CitacaoDTO
from app.application.dtos.compat import ApiModel
from app.knowledge.domain import CategoriaDocumento, OrigemVersao, StatusVersao

LIMITE_CARACTERES_TEXTO = 500_000


class CadastroTextoRequest(ApiModel):
    titulo: str = Field(min_length=3, max_length=200)
    categoria: CategoriaDocumento
    responsavel: str = Field(min_length=2, max_length=120)
    fonte: str | None = Field(default=None, max_length=200)
    escopo_acesso: Literal["RH"] = "RH"  # MVP: so RH
    texto: str = Field(max_length=LIMITE_CARACTERES_TEXTO)
    rotulo_versao: str | None = Field(default=None, max_length=60)
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    confirma_sem_dados_sensiveis: bool = False


class NovaVersaoTextoRequest(ApiModel):
    texto: str = Field(max_length=LIMITE_CARACTERES_TEXTO)
    rotulo_versao: str | None = Field(default=None, max_length=60)
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    confirma_sem_dados_sensiveis: bool = False


class CadastroArquivoMetadados(ApiModel):
    """Campos do formulario multipart que acompanham o arquivo (o texto vem do arquivo)."""

    titulo: str = Field(min_length=3, max_length=200)
    categoria: CategoriaDocumento
    responsavel: str = Field(min_length=2, max_length=120)
    fonte: str | None = Field(default=None, max_length=200)
    escopo_acesso: Literal["RH"] = "RH"
    rotulo_versao: str | None = Field(default=None, max_length=60)
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    confirma_sem_dados_sensiveis: bool = False


class NovaVersaoArquivoMetadados(ApiModel):
    rotulo_versao: str | None = Field(default=None, max_length=60)
    vigencia_inicio: date | None = None
    vigencia_fim: date | None = None
    confirma_sem_dados_sensiveis: bool = False


class AtualizarMetadadosRequest(ApiModel):
    titulo: str | None = Field(default=None, min_length=3, max_length=200)
    categoria: CategoriaDocumento | None = None
    responsavel: str | None = Field(default=None, min_length=2, max_length=120)
    fonte: str | None = Field(default=None, max_length=200)


class VersaoDTO(ApiModel):
    id: UUID
    numero: int
    rotulo: str
    origem: OrigemVersao
    status: StatusVersao
    publicada: bool
    vigencia_inicio: date
    vigencia_fim: date | None
    tamanho_bytes: int
    nome_arquivo: str | None
    erro_codigo: str | None
    erro_mensagem: str | None
    achados_sensiveis: list[str]
    tentativas: int
    criado_em: datetime
    processado_em: datetime | None
    publicada_em: datetime | None
    quantidade_trechos: int = 0


class DocumentoDTO(ApiModel):
    id: UUID
    titulo: str
    categoria: CategoriaDocumento
    responsavel: str
    fonte: str | None
    escopo_acesso: str
    criado_em: datetime
    atualizado_em: datetime
    versao_publicada: VersaoDTO | None
    versoes: list[VersaoDTO]


# -- contrato de recuperacao ----------------------------------------------------------------


class ConsultaRecuperacao(ApiModel):
    texto: str = Field(min_length=3, max_length=500)
    categorias: list[CategoriaDocumento] | None = None
    fator_nr1: str | None = None  # so para expansao de consulta
    area_id: str | None = None  # so telemetria; nunca filtro de acesso
    max_trechos: int = Field(default=5, ge=1, le=8)
    max_caracteres: int = Field(default=6000, ge=500, le=12000)
    data_referencia: date | None = None


class TrechoRecuperado(ApiModel):
    ref: str  # "C1", "C2"... usado nas citacoes da resposta
    trecho_id: UUID
    documento_id: UUID
    versao_id: UUID
    titulo: str
    categoria: CategoriaDocumento
    versao_numero: int
    versao_rotulo: str
    vigencia_inicio: date
    vigencia_fim: date | None
    pagina: int | None
    secao: str | None
    texto: str
    score: float
    suspeito_injecao: bool


class ResultadoRecuperacao(ApiModel):
    trechos: list[TrechoRecuperado]
    evidencia_suficiente: bool
    motivo_insuficiencia: str | None = None
    possivel_conflito: list[list[str]] = Field(default_factory=list)  # pares de refs
    metodo: Literal["texto_bm25", "fts_postgres"] = "texto_bm25"
    config: dict[str, float | int | str] = Field(default_factory=dict)
    latencia_ms: int = 0


class PerguntaRequest(ApiModel):
    pergunta: str = Field(min_length=3, max_length=500)
    categorias: list[CategoriaDocumento] | None = None
    max_trechos: int = Field(default=5, ge=1, le=8)


class RespostaFundamentadaDTO(ApiModel):
    texto: str
    citacoes: list[CitacaoDTO]
    evidencia_suficiente: bool
    resposta_segura: bool  # True quando o backend devolveu a resposta padrao de falta de evidencia
    avisos: list[str] = Field(default_factory=list)
    modelo: str | None = None
    latencia_recuperacao_ms: int = 0
    latencia_total_ms: int = 0
