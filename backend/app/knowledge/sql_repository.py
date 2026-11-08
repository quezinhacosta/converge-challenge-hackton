"""Repositorio PostgreSQL da base de conhecimento (schema da migration 0001_shared_foundation).

Usa a Session da requisicao (transacao aberta pela integracao, com vytai.empresa_id no RLS).
Nunca faz commit: a transacao e da requisicao. Toda consulta tambem filtra empresa_id
explicitamente (defesa em profundidade alem do RLS).
"""

import json
from datetime import date, datetime
from typing import Any
from uuid import UUID

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.knowledge.domain import (
    CategoriaDocumento,
    Documento,
    DocumentoTrecho,
    DocumentoVersao,
    EventoDocumento,
    OrigemVersao,
    StatusVersao,
)
from app.knowledge.repository import TrechoElegivel
from app.knowledge.text_search import normalizar

MAX_CANDIDATOS = 400
_COLS_VERSAO = (
    "id, documento_id, empresa_id, numero, rotulo, origem, sha256_conteudo, vigencia_inicio, "
    "criado_por, criado_em, status, vigencia_fim, nome_arquivo, mime, tamanho_bytes, erro_codigo, "
    "erro_mensagem, achados_sensiveis, tentativas, iniciado_em, processado_em, publicada, "
    "publicada_em, publicada_por"
)
_COLS_DOC = (
    "id, empresa_id, titulo, categoria, responsavel, escopo_acesso, criado_por, criado_em, "
    "atualizado_em, fonte"
)


def _doc(r: Any) -> Documento:
    return Documento(
        id=r.id,
        empresa_id=r.empresa_id,
        titulo=r.titulo,
        categoria=CategoriaDocumento(r.categoria),
        responsavel=r.responsavel,
        escopo_acesso=r.escopo_acesso,
        criado_por=r.criado_por,
        criado_em=r.criado_em,
        atualizado_em=r.atualizado_em,
        fonte=r.fonte,
    )


def _versao(r: Any) -> DocumentoVersao:
    achados = r.achados_sensiveis or []
    if isinstance(achados, str):
        achados = json.loads(achados)
    return DocumentoVersao(
        id=r.id,
        documento_id=r.documento_id,
        empresa_id=r.empresa_id,
        numero=r.numero,
        rotulo=r.rotulo or f"v{r.numero}",
        origem=OrigemVersao(r.origem),
        sha256_conteudo=r.sha256_conteudo,
        vigencia_inicio=r.vigencia_inicio,
        criado_por=r.criado_por,
        criado_em=r.criado_em,
        status=StatusVersao(r.status),
        vigencia_fim=r.vigencia_fim,
        nome_arquivo=r.nome_arquivo,
        mime=r.mime,
        tamanho_bytes=r.tamanho_bytes or 0,
        erro_codigo=r.erro_codigo,
        erro_mensagem=r.erro_mensagem,
        achados_sensiveis=tuple(achados),
        tentativas=r.tentativas,
        iniciado_em=r.iniciado_em,
        processado_em=r.processado_em,
        publicada=r.publicada,
        publicada_em=r.publicada_em,
        publicada_por=r.publicada_por,
    )


class RepositorioConhecimentoSQL:
    """Implementa RepositorioConhecimento e ArmazenamentoOriginal sobre a mesma Session."""

    def __init__(self, session: Session) -> None:
        self.s = session

    def _exec(self, sql: str, **params: Any) -> Any:
        return self.s.execute(text(sql), params)

    # -- documentos -------------------------------------------------------------------------

    def salvar_documento(self, d: Documento) -> None:
        self._exec(
            f"""INSERT INTO documento ({_COLS_DOC})
            VALUES (:id, :empresa_id, :titulo, :categoria, :responsavel, :escopo_acesso,
                    :criado_por, :criado_em, :atualizado_em, :fonte)
            ON CONFLICT (id) DO UPDATE SET titulo=EXCLUDED.titulo, categoria=EXCLUDED.categoria,
              responsavel=EXCLUDED.responsavel, fonte=EXCLUDED.fonte,
              atualizado_em=EXCLUDED.atualizado_em
            WHERE documento.empresa_id = EXCLUDED.empresa_id""",
            id=d.id,
            empresa_id=d.empresa_id,
            titulo=d.titulo,
            categoria=d.categoria.value,
            responsavel=d.responsavel,
            escopo_acesso=d.escopo_acesso,
            criado_por=d.criado_por,
            criado_em=d.criado_em,
            atualizado_em=d.atualizado_em,
            fonte=d.fonte,
        )

    def obter_documento(self, empresa_id: UUID, documento_id: UUID) -> Documento | None:
        r = self._exec(
            f"SELECT {_COLS_DOC} FROM documento WHERE empresa_id=:e AND id=:d",
            e=empresa_id,
            d=documento_id,
        ).first()
        return _doc(r) if r else None

    def listar_documentos(
        self, empresa_id: UUID, categoria: CategoriaDocumento | None = None
    ) -> list[Documento]:
        rows = self._exec(
            f"""SELECT {_COLS_DOC} FROM documento WHERE empresa_id=:e
            AND (CAST(:c AS text) IS NULL OR categoria=:c) ORDER BY atualizado_em DESC""",
            e=empresa_id,
            c=categoria.value if categoria else None,
        )
        return [_doc(r) for r in rows]

    # -- versoes ----------------------------------------------------------------------------

    def salvar_versao(self, v: DocumentoVersao) -> None:
        self._exec(
            f"""INSERT INTO documento_versao ({_COLS_VERSAO})
            VALUES (:id, :documento_id, :empresa_id, :numero, :rotulo, :origem, :sha, :vi,
              :criado_por, :criado_em, :status, :vf, :nome_arquivo, :mime, :tamanho, :ecod,
              :emsg, CAST(:achados AS jsonb), :tentativas, :iniciado_em, :processado_em,
              :publicada, :publicada_em, :publicada_por)
            ON CONFLICT (id) DO UPDATE SET status=EXCLUDED.status, erro_codigo=EXCLUDED.erro_codigo,
              erro_mensagem=EXCLUDED.erro_mensagem, achados_sensiveis=EXCLUDED.achados_sensiveis,
              tentativas=EXCLUDED.tentativas, iniciado_em=EXCLUDED.iniciado_em,
              processado_em=EXCLUDED.processado_em, publicada=EXCLUDED.publicada,
              publicada_em=EXCLUDED.publicada_em, publicada_por=EXCLUDED.publicada_por
            WHERE documento_versao.empresa_id = EXCLUDED.empresa_id""",
            id=v.id,
            documento_id=v.documento_id,
            empresa_id=v.empresa_id,
            numero=v.numero,
            rotulo=v.rotulo,
            origem=v.origem.value,
            sha=v.sha256_conteudo,
            vi=v.vigencia_inicio,
            criado_por=v.criado_por,
            criado_em=v.criado_em,
            status=v.status.value,
            vf=v.vigencia_fim,
            nome_arquivo=v.nome_arquivo,
            mime=v.mime,
            tamanho=v.tamanho_bytes,
            ecod=v.erro_codigo,
            emsg=v.erro_mensagem,
            achados=json.dumps(list(v.achados_sensiveis)),
            tentativas=v.tentativas,
            iniciado_em=v.iniciado_em,
            processado_em=v.processado_em,
            publicada=v.publicada,
            publicada_em=v.publicada_em,
            publicada_por=v.publicada_por,
        )

    def obter_versao(self, empresa_id: UUID, versao_id: UUID) -> DocumentoVersao | None:
        r = self._exec(
            f"SELECT {_COLS_VERSAO} FROM documento_versao WHERE empresa_id=:e AND id=:v",
            e=empresa_id,
            v=versao_id,
        ).first()
        return _versao(r) if r else None

    def versoes_do_documento(self, empresa_id: UUID, documento_id: UUID) -> list[DocumentoVersao]:
        rows = self._exec(
            f"""SELECT {_COLS_VERSAO} FROM documento_versao
            WHERE empresa_id=:e AND documento_id=:d ORDER BY numero""",
            e=empresa_id,
            d=documento_id,
        )
        return [_versao(r) for r in rows]

    def versao_com_hash_valido(self, empresa_id: UUID, sha256: str) -> DocumentoVersao | None:
        r = self._exec(
            f"""SELECT {_COLS_VERSAO} FROM documento_versao WHERE empresa_id=:e
            AND sha256_conteudo=:h AND status IN ('RECEBIDO','PROCESSANDO','PRONTO') LIMIT 1""",
            e=empresa_id,
            h=sha256,
        ).first()
        return _versao(r) if r else None

    def reivindicar_processamento(
        self, empresa_id: UUID, versao_id: UUID, agora: datetime, lock_vencido_antes: datetime
    ) -> DocumentoVersao | None:
        r = self._exec(
            f"""UPDATE documento_versao SET status='PROCESSANDO', iniciado_em=:agora,
              tentativas=tentativas+1
            WHERE empresa_id=:e AND id=:v AND (status IN ('RECEBIDO','ERRO')
              OR (status='PROCESSANDO' AND iniciado_em < :limite))
            RETURNING {_COLS_VERSAO}""",
            e=empresa_id,
            v=versao_id,
            agora=agora,
            limite=lock_vencido_antes,
        ).first()
        return _versao(r) if r else None

    def substituir_trechos(
        self, empresa_id: UUID, versao_id: UUID, trechos: list[DocumentoTrecho]
    ) -> None:
        if any(t.empresa_id != empresa_id or t.versao_id != versao_id for t in trechos):
            raise ValueError("Trecho de outra empresa ou versao.")
        self._exec(
            "DELETE FROM documento_trecho WHERE empresa_id=:e AND versao_id=:v",
            e=empresa_id,
            v=versao_id,
        )
        for t in trechos:  # o trigger vytai_indexar_trecho preenche titulo/categoria/tsv
            self._exec(
                """INSERT INTO documento_trecho
                (id, versao_id, empresa_id, ordem, pagina, secao, texto, suspeito_injecao)
                VALUES (:id, :v, :e, :ordem, :pagina, :secao, :texto, :susp)""",
                id=t.id,
                v=versao_id,
                e=empresa_id,
                ordem=t.ordem,
                pagina=t.pagina,
                secao=t.secao,
                texto=t.texto,
                susp=t.suspeito_injecao,
            )

    def publicar_versao(
        self, empresa_id: UUID, versao_id: UUID, usuario_id: UUID, agora: datetime
    ) -> DocumentoVersao:
        # Mesma transacao: tira a anterior de circulacao antes (indice unico de publicada).
        self._exec(
            """UPDATE documento_versao o SET publicada=false, publicada_em=NULL,
              publicada_por=NULL, status='SUBSTITUIDA'
            FROM documento_versao alvo
            WHERE alvo.empresa_id=:e AND alvo.id=:v AND o.empresa_id=:e
              AND o.documento_id=alvo.documento_id AND o.id<>alvo.id
              AND (o.publicada OR (o.status='PRONTO' AND o.numero < alvo.numero))""",
            e=empresa_id,
            v=versao_id,
        )
        r = self._exec(
            f"""UPDATE documento_versao SET publicada=true, publicada_em=:agora,
              publicada_por=:u WHERE empresa_id=:e AND id=:v AND status='PRONTO'
            RETURNING {_COLS_VERSAO}""",
            e=empresa_id,
            v=versao_id,
            agora=agora,
            u=usuario_id,
        ).first()
        if r is None:
            raise KeyError(versao_id)
        return _versao(r)

    def excluir_documento(self, empresa_id: UUID, documento_id: UUID) -> None:
        # Cascade: versoes, documento_arquivo e documento_trecho.
        self._exec(
            "DELETE FROM documento WHERE empresa_id=:e AND id=:d", e=empresa_id, d=documento_id
        )

    # -- recuperacao ------------------------------------------------------------------------

    def trechos_elegiveis(
        self,
        empresa_id: UUID,
        escopos: frozenset[str],
        dia: date,
        categorias: frozenset[CategoriaDocumento] | None = None,
        consulta: str | None = None,
    ) -> list[TrechoElegivel]:
        """Filtros de acesso no SQL; com `consulta`, o indice FTS pre-seleciona candidatos."""
        termos = [p for p in normalizar(consulta or "").split() if len(p) > 2]
        filtro_fts = ""
        params: dict[str, Any] = {
            "e": empresa_id,
            "dia": dia,
            "escopos": list(escopos),
            "cats": [c.value for c in categorias] if categorias else None,
            "limite": MAX_CANDIDATOS,
        }
        if termos:
            filtro_fts = "AND t.tsv @@ to_tsquery('public.vytai_portuguese', :q)"
            params["q"] = " | ".join(p.replace("'", "") for p in termos)
        rows = self._exec(
            f"""SELECT t.id AS t_id, t.ordem, t.pagina, t.secao, t.texto, t.suspeito_injecao,
              {", ".join("v." + c + " AS v_" + c for c in _COLS_VERSAO.split(", "))},
              {", ".join("d." + c + " AS d_" + c for c in _COLS_DOC.split(", "))}
            FROM documento_trecho t
            JOIN documento_versao v ON v.empresa_id=t.empresa_id AND v.id=t.versao_id
            JOIN documento d ON d.empresa_id=v.empresa_id AND d.id=v.documento_id
            WHERE t.empresa_id=:e AND v.publicada AND v.status='PRONTO'
              AND v.vigencia_inicio <= :dia AND (v.vigencia_fim IS NULL OR :dia < v.vigencia_fim)
              AND d.escopo_acesso = ANY(:escopos)
              AND (CAST(:cats AS text[]) IS NULL OR d.categoria = ANY(:cats))
              {filtro_fts}
            LIMIT :limite""",
            **params,
        )
        return [self._elegivel(r) for r in rows]

    @staticmethod
    def _elegivel(r: Any) -> TrechoElegivel:
        class _Ns:
            def __init__(self, prefixo: str) -> None:
                for k, val in r._mapping.items():
                    if k.startswith(prefixo):
                        setattr(self, k[len(prefixo) :], val)

        versao = _versao(_Ns("v_"))
        doc = _doc(_Ns("d_"))
        trecho = DocumentoTrecho(
            id=r.t_id,
            versao_id=versao.id,
            empresa_id=versao.empresa_id,
            ordem=r.ordem,
            texto=r.texto,
            pagina=r.pagina,
            secao=r.secao,
            suspeito_injecao=r.suspeito_injecao,
        )
        return TrechoElegivel(trecho, versao, doc)

    # -- auditoria e contagem ---------------------------------------------------------------

    def registrar_evento(self, ev: EventoDocumento) -> None:
        self._exec(
            """INSERT INTO documento_evento (id, empresa_id, documento_id, versao_id, acao,
              usuario_id, em, detalhe) VALUES (:id, :e, :d, :v, :acao, :u, :em, CAST(:det AS jsonb))""",
            id=ev.id,
            e=ev.empresa_id,
            d=ev.documento_id,
            v=ev.versao_id,
            acao=ev.acao,
            u=ev.usuario_id,
            em=ev.em,
            det=json.dumps(ev.detalhe, default=str),
        )

    def contar_trechos(self, empresa_id: UUID, versao_id: UUID) -> int:
        return int(
            self._exec(
                "SELECT count(*) FROM documento_trecho WHERE empresa_id=:e AND versao_id=:v",
                e=empresa_id,
                v=versao_id,
            ).scalar_one()
        )

    # -- ArmazenamentoOriginal (tabela documento_arquivo) ------------------------------------

    def salvar(self, empresa_id: UUID, versao_id: UUID, conteudo: bytes) -> None:
        self._exec(
            """INSERT INTO documento_arquivo (empresa_id, versao_id, original) VALUES (:e, :v, :o)
            ON CONFLICT (empresa_id, versao_id) DO UPDATE SET original=EXCLUDED.original""",
            e=empresa_id,
            v=versao_id,
            o=conteudo,
        )

    def ler(self, empresa_id: UUID, versao_id: UUID) -> bytes | None:
        r = self._exec(
            "SELECT original FROM documento_arquivo WHERE empresa_id=:e AND versao_id=:v",
            e=empresa_id,
            v=versao_id,
        ).first()
        return bytes(r.original) if r else None

    def apagar(self, empresa_id: UUID, versao_id: UUID) -> None:
        self._exec(
            "DELETE FROM documento_arquivo WHERE empresa_id=:e AND versao_id=:v",
            e=empresa_id,
            v=versao_id,
        )
