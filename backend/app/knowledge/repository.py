"""Contratos de persistencia da base de conhecimento e implementacao em memoria.

A implementacao Postgres (Supabase) segue o mesmo Protocol; o esquema fica nas migrations
da integracao. O original fica num armazenamento separado (tabela documento_arquivo), para
listagem e recuperacao nunca carregarem o binario.
"""

import threading
from collections.abc import Iterator
from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import Protocol
from uuid import UUID

from app.knowledge.domain import (
    STATUS_VALIDOS_PARA_DEDUP,
    CategoriaDocumento,
    Documento,
    DocumentoTrecho,
    DocumentoVersao,
    EventoDocumento,
    StatusVersao,
)


@dataclass(frozen=True)
class TrechoElegivel:
    """Trecho que ja passou por todos os filtros de acesso, com os metadados para citar."""

    trecho: DocumentoTrecho
    versao: DocumentoVersao
    documento: Documento


class ArmazenamentoOriginal(Protocol):
    def salvar(self, empresa_id: UUID, versao_id: UUID, conteudo: bytes) -> None: ...
    def ler(self, empresa_id: UUID, versao_id: UUID) -> bytes | None: ...
    def apagar(self, empresa_id: UUID, versao_id: UUID) -> None: ...


class RepositorioConhecimento(Protocol):
    def salvar_documento(self, documento: Documento) -> None: ...
    def obter_documento(self, empresa_id: UUID, documento_id: UUID) -> Documento | None: ...
    def listar_documentos(
        self, empresa_id: UUID, categoria: CategoriaDocumento | None = None
    ) -> list[Documento]: ...
    def salvar_versao(self, versao: DocumentoVersao) -> None: ...
    def obter_versao(self, empresa_id: UUID, versao_id: UUID) -> DocumentoVersao | None: ...
    def versoes_do_documento(
        self, empresa_id: UUID, documento_id: UUID
    ) -> list[DocumentoVersao]: ...
    def versao_com_hash_valido(self, empresa_id: UUID, sha256: str) -> DocumentoVersao | None: ...
    def reivindicar_processamento(
        self, empresa_id: UUID, versao_id: UUID, agora: datetime, lock_vencido_antes: datetime
    ) -> DocumentoVersao | None: ...
    def substituir_trechos(
        self, empresa_id: UUID, versao_id: UUID, trechos: list[DocumentoTrecho]
    ) -> None: ...
    def publicar_versao(
        self, empresa_id: UUID, versao_id: UUID, usuario_id: UUID, agora: datetime
    ) -> DocumentoVersao: ...
    def excluir_documento(self, empresa_id: UUID, documento_id: UUID) -> None: ...
    def trechos_elegiveis(
        self,
        empresa_id: UUID,
        escopos: frozenset[str],
        dia: date,
        categorias: frozenset[CategoriaDocumento] | None = None,
    ) -> list[TrechoElegivel]: ...
    def registrar_evento(self, evento: EventoDocumento) -> None: ...
    def contar_trechos(self, empresa_id: UUID, versao_id: UUID) -> int: ...


class ArmazenamentoOriginalEmMemoria:
    def __init__(self) -> None:
        self._dados: dict[tuple[UUID, UUID], bytes] = {}

    def salvar(self, empresa_id: UUID, versao_id: UUID, conteudo: bytes) -> None:
        self._dados[(empresa_id, versao_id)] = conteudo

    def ler(self, empresa_id: UUID, versao_id: UUID) -> bytes | None:
        return self._dados.get((empresa_id, versao_id))

    def apagar(self, empresa_id: UUID, versao_id: UUID) -> None:
        self._dados.pop((empresa_id, versao_id), None)

    def quantidade(self) -> int:
        return len(self._dados)


class RepositorioConhecimentoEmMemoria:
    """Mesma semantica esperada do Postgres: tudo filtrado por empresa_id, operacoes de
    publicacao/substituicao/exclusao atomicas (um lock emula a transacao)."""

    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._documentos: dict[UUID, Documento] = {}
        self._versoes: dict[UUID, DocumentoVersao] = {}
        self._trechos: dict[UUID, list[DocumentoTrecho]] = {}
        self.eventos: list[EventoDocumento] = []

    # -- documentos -------------------------------------------------------------------------

    def salvar_documento(self, documento: Documento) -> None:
        with self._lock:
            self._documentos[documento.id] = replace(documento)

    def obter_documento(self, empresa_id: UUID, documento_id: UUID) -> Documento | None:
        doc = self._documentos.get(documento_id)
        return replace(doc) if doc and doc.empresa_id == empresa_id else None

    def listar_documentos(
        self, empresa_id: UUID, categoria: CategoriaDocumento | None = None
    ) -> list[Documento]:
        return [
            replace(d)
            for d in self._documentos.values()
            if d.empresa_id == empresa_id and (categoria is None or d.categoria == categoria)
        ]

    # -- versoes ----------------------------------------------------------------------------

    def salvar_versao(self, versao: DocumentoVersao) -> None:
        with self._lock:
            self._versoes[versao.id] = replace(versao)

    def obter_versao(self, empresa_id: UUID, versao_id: UUID) -> DocumentoVersao | None:
        versao = self._versoes.get(versao_id)
        return replace(versao) if versao and versao.empresa_id == empresa_id else None

    def versoes_do_documento(self, empresa_id: UUID, documento_id: UUID) -> list[DocumentoVersao]:
        return sorted(
            (
                replace(v)
                for v in self._versoes.values()
                if v.documento_id == documento_id and v.empresa_id == empresa_id
            ),
            key=lambda v: v.numero,
        )

    def versao_com_hash_valido(self, empresa_id: UUID, sha256: str) -> DocumentoVersao | None:
        for versao in self._versoes.values():
            if (
                versao.empresa_id == empresa_id
                and versao.sha256_conteudo == sha256
                and versao.status in STATUS_VALIDOS_PARA_DEDUP
            ):
                return replace(versao)
        return None

    def reivindicar_processamento(
        self, empresa_id: UUID, versao_id: UUID, agora: datetime, lock_vencido_antes: datetime
    ) -> DocumentoVersao | None:
        """Claim atomico: so uma execucao processa a versao por vez (equivale ao UPDATE ...
        WHERE status IN (...) RETURNING). Processamento travado ha muito tempo pode ser retomado."""
        with self._lock:
            versao = self._versoes.get(versao_id)
            if versao is None or versao.empresa_id != empresa_id:
                return None
            travada = (
                versao.status == StatusVersao.PROCESSANDO
                and versao.iniciado_em is not None
                and versao.iniciado_em < lock_vencido_antes
            )
            if versao.status not in (StatusVersao.RECEBIDO, StatusVersao.ERRO) and not travada:
                return None
            versao.status = StatusVersao.PROCESSANDO
            versao.iniciado_em = agora
            versao.tentativas += 1
            return replace(versao)

    def substituir_trechos(
        self, empresa_id: UUID, versao_id: UUID, trechos: list[DocumentoTrecho]
    ) -> None:
        """Idempotente: apaga e recria os trechos da versao numa unica operacao."""
        with self._lock:
            versao = self._versoes.get(versao_id)
            if versao is None or versao.empresa_id != empresa_id:
                raise KeyError(versao_id)
            if any(t.empresa_id != empresa_id or t.versao_id != versao_id for t in trechos):
                raise ValueError("Trecho de outra empresa ou versao.")
            if len({t.ordem for t in trechos}) != len(trechos):
                raise ValueError("Ordem duplicada nos trechos (UNIQUE versao_id, ordem).")
            self._trechos[versao_id] = [replace(t) for t in trechos]

    def publicar_versao(
        self, empresa_id: UUID, versao_id: UUID, usuario_id: UUID, agora: datetime
    ) -> DocumentoVersao:
        """Publica e marca a anterior como SUBSTITUIDA na mesma transacao."""
        with self._lock:
            versao = self._versoes[versao_id]
            for outra in self._versoes.values():
                if outra.documento_id == versao.documento_id and outra.id != versao.id:
                    if outra.publicada:
                        outra.publicada = False
                        outra.status = StatusVersao.SUBSTITUIDA
                    elif outra.status == StatusVersao.PRONTO and outra.numero < versao.numero:
                        outra.status = StatusVersao.SUBSTITUIDA
            versao.publicada = True
            versao.publicada_em = agora
            versao.publicada_por = usuario_id
            return replace(versao)

    def excluir_documento(self, empresa_id: UUID, documento_id: UUID) -> None:
        with self._lock:
            doc = self._documentos.get(documento_id)
            if doc is None or doc.empresa_id != empresa_id:
                return
            for versao_id in [
                v.id for v in self._versoes.values() if v.documento_id == documento_id
            ]:
                self._trechos.pop(versao_id, None)
                self._versoes.pop(versao_id, None)
            self._documentos.pop(documento_id, None)

    # -- recuperacao ------------------------------------------------------------------------

    def trechos_elegiveis(
        self,
        empresa_id: UUID,
        escopos: frozenset[str],
        dia: date,
        categorias: frozenset[CategoriaDocumento] | None = None,
    ) -> list[TrechoElegivel]:
        """Filtros ANTES do ranking: empresa, publicacao, PRONTO, vigencia, escopo, categoria."""
        elegiveis: list[TrechoElegivel] = []
        for versao in self._versoes.values():
            if (
                versao.empresa_id != empresa_id
                or not versao.publicada
                or versao.status != StatusVersao.PRONTO
                or not versao.vigente_em(dia)
            ):
                continue
            doc = self._documentos.get(versao.documento_id)
            if doc is None or doc.empresa_id != empresa_id or doc.escopo_acesso not in escopos:
                continue
            if categorias and doc.categoria not in categorias:
                continue
            elegiveis.extend(
                TrechoElegivel(t, versao, doc) for t in self._trechos.get(versao.id, [])
            )
        return elegiveis

    # -- auditoria e apoio a testes ---------------------------------------------------------

    def registrar_evento(self, evento: EventoDocumento) -> None:
        self.eventos.append(evento)

    def contar_trechos(self, empresa_id: UUID, versao_id: UUID) -> int:
        versao = self._versoes.get(versao_id)
        if versao is None or versao.empresa_id != empresa_id:
            return 0
        return len(self._trechos.get(versao_id, []))

    def todos_os_trechos(self) -> Iterator[DocumentoTrecho]:
        for lista in self._trechos.values():
            yield from lista
