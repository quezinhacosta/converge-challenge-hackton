"""Entidades, estados e erros da base de conhecimento da empresa (RAG)."""

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import StrEnum
from typing import Any
from uuid import UUID

# Contrato compartilhado (Codex): identidade resolvida no servidor, nunca pelo body.
from app.application.contracts.identity import ContextoAutorizado as ContextoAutorizado

PAPEL_RH = "RH"
ESCOPO_RH = "RH"


class CategoriaDocumento(StrEnum):
    POLITICA = "POLITICA"
    PROCEDIMENTO_ACOLHIMENTO = "PROCEDIMENTO_ACOLHIMENTO"
    CANAL_APOIO = "CANAL_APOIO"
    PROGRAMA_BENEFICIO = "PROGRAMA_BENEFICIO"
    PLANO_ACAO_ANTERIOR = "PLANO_ACAO_ANTERIOR"
    CONTEXTO_ORGANIZACIONAL = "CONTEXTO_ORGANIZACIONAL"
    REFERENCIA_APROVADA = "REFERENCIA_APROVADA"


class StatusVersao(StrEnum):
    RECEBIDO = "RECEBIDO"
    PROCESSANDO = "PROCESSANDO"
    PRONTO = "PRONTO"
    ERRO = "ERRO"
    BLOQUEADO = "BLOQUEADO"
    SUBSTITUIDA = "SUBSTITUIDA"


# Versoes que ocupam o hash de conteudo (deduplicacao). Erro/bloqueio nao impedem recadastro.
STATUS_VALIDOS_PARA_DEDUP = frozenset(
    {StatusVersao.RECEBIDO, StatusVersao.PROCESSANDO, StatusVersao.PRONTO}
)


class OrigemVersao(StrEnum):
    TEXTO = "TEXTO"
    UPLOAD = "UPLOAD"


@dataclass
class Documento:
    id: UUID
    empresa_id: UUID
    titulo: str
    categoria: CategoriaDocumento
    responsavel: str
    escopo_acesso: str
    criado_por: UUID
    criado_em: datetime
    atualizado_em: datetime
    fonte: str | None = None


@dataclass
class DocumentoVersao:
    id: UUID
    documento_id: UUID
    empresa_id: UUID
    numero: int
    rotulo: str
    origem: OrigemVersao
    sha256_conteudo: str
    vigencia_inicio: date
    criado_por: UUID
    criado_em: datetime
    status: StatusVersao = StatusVersao.RECEBIDO
    vigencia_fim: date | None = None
    nome_arquivo: str | None = None
    mime: str | None = None
    tamanho_bytes: int = 0
    erro_codigo: str | None = None
    erro_mensagem: str | None = None
    achados_sensiveis: tuple[str, ...] = ()
    tentativas: int = 0
    iniciado_em: datetime | None = None
    processado_em: datetime | None = None
    publicada: bool = False
    publicada_em: datetime | None = None
    publicada_por: UUID | None = None

    def vigente_em(self, dia: date) -> bool:
        return self.vigencia_inicio <= dia and (
            self.vigencia_fim is None or dia < self.vigencia_fim
        )


@dataclass
class DocumentoTrecho:
    id: UUID
    versao_id: UUID
    empresa_id: UUID
    ordem: int
    texto: str
    pagina: int | None = None
    secao: str | None = None
    suspeito_injecao: bool = False


@dataclass
class EventoDocumento:
    """Auditoria sem conteudo nem titulo: so ids, acao e codigos."""

    id: UUID
    empresa_id: UUID
    documento_id: UUID
    acao: str
    usuario_id: UUID
    em: datetime
    versao_id: UUID | None = None
    detalhe: dict[str, Any] = field(default_factory=dict)


class ErroConhecimento(Exception):
    """Erro de negocio com codigo estavel, mensagem legivel para o RH e status HTTP."""

    STATUS_HTTP: dict[str, int] = {
        "NAO_AUTORIZADO": 403,
        "DOCUMENTO_NAO_ENCONTRADO": 404,
        "VERSAO_NAO_ENCONTRADA": 404,
        "DUPLICADO": 409,
        "VERSAO_NAO_PRONTA": 409,
        "PROCESSAMENTO_EM_ANDAMENTO": 409,
        "VIGENCIA_INVALIDA": 422,
        "CONFIRMACAO_OBRIGATORIA": 422,
        "TEXTO_VAZIO": 422,
        "SEM_TEXTO_EXTRAIVEL": 422,
        "TEXTO_MUITO_LONGO": 422,
        "FORMATO_NAO_SUPORTADO": 415,
        "ARQUIVO_GRANDE": 413,
        "ARQUIVO_CORROMPIDO": 422,
        "CONTEUDO_SENSIVEL_DETECTADO": 422,
    }

    def __init__(self, codigo: str, mensagem: str, detalhes: dict[str, Any] | None = None):
        super().__init__(mensagem)
        self.codigo = codigo
        self.mensagem = mensagem
        self.detalhes = detalhes or {}

    @property
    def status_http(self) -> int:
        return self.STATUS_HTTP.get(self.codigo, 400)

    def como_dict(self) -> dict[str, Any]:
        return {"codigo": self.codigo, "mensagem": self.mensagem, "detalhes": self.detalhes}
