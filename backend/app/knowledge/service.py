"""Casos de uso do cadastro documental: cadastrar, versionar, processar, publicar, excluir."""

import hashlib
import unicodedata
from collections.abc import Callable
from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4, uuid5

from app.knowledge.chunking import dividir_em_trechos
from app.knowledge.domain import (
    PAPEL_RH,
    CategoriaDocumento,
    ContextoAutorizado,
    Documento,
    DocumentoTrecho,
    DocumentoVersao,
    ErroConhecimento,
    EventoDocumento,
    OrigemVersao,
    StatusVersao,
)
from app.knowledge.dtos import (
    LIMITE_CARACTERES_TEXTO,
    AtualizarMetadadosRequest,
    CadastroTextoRequest,
    DocumentoDTO,
    NovaVersaoTextoRequest,
    VersaoDTO,
)
from app.knowledge.repository import ArmazenamentoOriginal, RepositorioConhecimento
from app.knowledge.screening import parece_injecao, triar_conteudo_sensivel

LOCK_PROCESSAMENTO = timedelta(minutes=10)
MAX_TENTATIVAS = 5


def _normalizar_para_hash(texto: str) -> str:
    texto = unicodedata.normalize("NFC", texto).replace("\r\n", "\n")
    return "\n".join(linha.strip() for linha in texto.split("\n")).strip()


def _sha256(texto: str) -> str:
    return hashlib.sha256(_normalizar_para_hash(texto).encode("utf-8")).hexdigest()


class ServicoConhecimento:
    def __init__(
        self,
        repositorio: RepositorioConhecimento,
        armazenamento: ArmazenamentoOriginal,
        relogio: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.repo = repositorio
        self.armazenamento = armazenamento
        self.agora = relogio

    # -- autorizacao e buscas por empresa ---------------------------------------------------

    @staticmethod
    def _exigir_rh(ctx: ContextoAutorizado) -> None:
        if PAPEL_RH not in ctx.papeis:
            raise ErroConhecimento(
                "NAO_AUTORIZADO", "Somente o RH pode gerenciar a base de conhecimento."
            )

    def _documento(self, ctx: ContextoAutorizado, documento_id: UUID) -> Documento:
        doc = self.repo.obter_documento(ctx.empresa_id, documento_id)
        if doc is None:  # documento de outra empresa responde igual a inexistente
            raise ErroConhecimento("DOCUMENTO_NAO_ENCONTRADO", "Documento nao encontrado.")
        return doc

    def _versao(self, ctx: ContextoAutorizado, versao_id: UUID) -> DocumentoVersao:
        versao = self.repo.obter_versao(ctx.empresa_id, versao_id)
        if versao is None:
            raise ErroConhecimento("VERSAO_NAO_ENCONTRADA", "Versao nao encontrada.")
        return versao

    def _evento(
        self,
        ctx: ContextoAutorizado,
        documento_id: UUID,
        acao: str,
        versao_id: UUID | None = None,
        **detalhe: object,
    ) -> None:
        self.repo.registrar_evento(
            EventoDocumento(
                uuid4(),
                ctx.empresa_id,
                documento_id,
                acao,
                ctx.usuario_id,
                self.agora(),
                versao_id,
                dict(detalhe),
            )
        )

    # -- validacoes comuns ------------------------------------------------------------------

    @staticmethod
    def _validar_texto_e_vigencia(
        texto: str, confirmado: bool, inicio: date | None, fim: date | None
    ) -> tuple[date, date | None]:
        if not confirmado:
            raise ErroConhecimento(
                "CONFIRMACAO_OBRIGATORIA",
                "Confirme que o documento nao contem dados pessoais sensiveis, prontuarios "
                "ou atestados nominativos.",
            )
        if not texto.strip():
            raise ErroConhecimento("TEXTO_VAZIO", "O conteudo do documento esta vazio.")
        if len(texto) > LIMITE_CARACTERES_TEXTO:
            raise ErroConhecimento(
                "TEXTO_MUITO_LONGO",
                f"O texto passa de {LIMITE_CARACTERES_TEXTO} caracteres. Divida o documento.",
            )
        inicio = inicio or date.today()
        if fim is not None and fim <= inicio:
            raise ErroConhecimento(
                "VIGENCIA_INVALIDA", "O fim da vigencia precisa ser depois do inicio."
            )
        return inicio, fim

    def _checar_duplicado(self, ctx: ContextoAutorizado, sha: str) -> None:
        existente = self.repo.versao_com_hash_valido(ctx.empresa_id, sha)
        if existente is not None:
            raise ErroConhecimento(
                "DUPLICADO",
                "Ja existe uma versao com exatamente este conteudo.",
                {"documentoId": str(existente.documento_id), "versaoId": str(existente.id)},
            )

    # -- cadastro e versoes -----------------------------------------------------------------

    def cadastrar_texto(self, ctx: ContextoAutorizado, req: CadastroTextoRequest) -> DocumentoDTO:
        self._exigir_rh(ctx)
        inicio, fim = self._validar_texto_e_vigencia(
            req.texto, req.confirma_sem_dados_sensiveis, req.vigencia_inicio, req.vigencia_fim
        )
        sha = _sha256(req.texto)
        self._checar_duplicado(ctx, sha)
        agora = self.agora()
        doc = Documento(
            id=uuid4(),
            empresa_id=ctx.empresa_id,
            titulo=req.titulo.strip(),
            categoria=req.categoria,
            responsavel=req.responsavel.strip(),
            escopo_acesso=req.escopo_acesso,
            criado_por=ctx.usuario_id,
            criado_em=agora,
            atualizado_em=agora,
            fonte=req.fonte,
        )
        self.repo.salvar_documento(doc)
        self._evento(ctx, doc.id, "CRIADO", categoria=doc.categoria.value)
        versao = self._criar_versao(ctx, doc, req.texto, sha, req.rotulo_versao, inicio, fim)
        self.processar(ctx, versao.id)
        return self.obter(ctx, doc.id)

    def adicionar_versao_texto(
        self, ctx: ContextoAutorizado, documento_id: UUID, req: NovaVersaoTextoRequest
    ) -> DocumentoDTO:
        self._exigir_rh(ctx)
        doc = self._documento(ctx, documento_id)
        inicio, fim = self._validar_texto_e_vigencia(
            req.texto, req.confirma_sem_dados_sensiveis, req.vigencia_inicio, req.vigencia_fim
        )
        sha = _sha256(req.texto)
        self._checar_duplicado(ctx, sha)
        versao = self._criar_versao(ctx, doc, req.texto, sha, req.rotulo_versao, inicio, fim)
        self.processar(ctx, versao.id)
        return self.obter(ctx, doc.id)

    def _criar_versao(
        self,
        ctx: ContextoAutorizado,
        doc: Documento,
        texto: str,
        sha: str,
        rotulo: str | None,
        inicio: date,
        fim: date | None,
    ) -> DocumentoVersao:
        existentes = self.repo.versoes_do_documento(ctx.empresa_id, doc.id)
        numero = (max((v.numero for v in existentes), default=0)) + 1
        conteudo = texto.encode("utf-8")
        versao = DocumentoVersao(
            id=uuid4(),
            documento_id=doc.id,
            empresa_id=ctx.empresa_id,
            numero=numero,
            rotulo=rotulo or f"v{numero}",
            origem=OrigemVersao.TEXTO,
            sha256_conteudo=sha,
            vigencia_inicio=inicio,
            vigencia_fim=fim,
            criado_por=ctx.usuario_id,
            criado_em=self.agora(),
            tamanho_bytes=len(conteudo),
            mime="text/plain",
        )
        self.repo.salvar_versao(versao)
        self.armazenamento.salvar(ctx.empresa_id, versao.id, conteudo)
        self._evento(ctx, doc.id, "VERSAO_ADICIONADA", versao.id, numero=numero)
        return versao

    # -- processamento (idempotente, retomavel) ---------------------------------------------

    def processar(self, ctx: ContextoAutorizado, versao_id: UUID) -> VersaoDTO:
        agora = self.agora()
        versao = self.repo.reivindicar_processamento(
            ctx.empresa_id, versao_id, agora, agora - LOCK_PROCESSAMENTO
        )
        if versao is None:
            atual = self._versao(ctx, versao_id)
            raise ErroConhecimento(
                "PROCESSAMENTO_EM_ANDAMENTO"
                if atual.status == StatusVersao.PROCESSANDO
                else "VERSAO_NAO_PRONTA",
                f"A versao esta em {atual.status.value} e nao pode ser processada agora.",
            )
        try:
            original = self.armazenamento.ler(ctx.empresa_id, versao.id)
            if original is None:
                raise ErroConhecimento(
                    "ARQUIVO_CORROMPIDO", "O original desta versao nao esta disponivel."
                )
            paginas = self._extrair(versao, original)
            achados = triar_conteudo_sensivel(paginas)
            if achados:
                return self._bloquear(ctx, versao, [a.codigo for a in achados])
            brutos = dividir_em_trechos(paginas)
            if not brutos:
                raise ErroConhecimento(
                    "SEM_TEXTO_EXTRAIVEL", "Nao foi possivel extrair texto deste documento."
                )
            trechos = [
                DocumentoTrecho(
                    id=uuid5(versao.id, str(b.ordem)),
                    versao_id=versao.id,
                    empresa_id=ctx.empresa_id,
                    ordem=b.ordem,
                    texto=b.texto,
                    pagina=b.pagina,
                    secao=b.secao,
                    suspeito_injecao=parece_injecao(b.texto),
                )
                for b in brutos
            ]
            self.repo.substituir_trechos(ctx.empresa_id, versao.id, trechos)
            versao.status = StatusVersao.PRONTO
            versao.erro_codigo = versao.erro_mensagem = None
            versao.processado_em = self.agora()
            self.repo.salvar_versao(versao)
            self._evento(
                ctx,
                versao.documento_id,
                "PROCESSADO",
                versao.id,
                trechos=len(trechos),
                suspeitos=sum(t.suspeito_injecao for t in trechos),
            )
        except ErroConhecimento as erro:
            self._falhar(ctx, versao, erro.codigo, erro.mensagem)
        except Exception:  # noqa: BLE001 - qualquer falha vira ERRO reprocessavel
            self._falhar(
                ctx,
                versao,
                "ERRO_PROCESSAMENTO",
                "Falha inesperada ao processar. Tente reprocessar.",
            )
        return self._versao_dto(ctx, self._versao(ctx, versao_id))

    @staticmethod
    def _extrair(versao: DocumentoVersao, original: bytes) -> list[tuple[int | None, str]]:
        if versao.origem == OrigemVersao.TEXTO:
            return [(None, original.decode("utf-8"))]
        raise ErroConhecimento("FORMATO_NAO_SUPORTADO", "Formato ainda nao suportado.")

    def _falhar(
        self, ctx: ContextoAutorizado, versao: DocumentoVersao, codigo: str, mensagem: str
    ) -> None:
        versao.status = StatusVersao.ERRO
        versao.erro_codigo, versao.erro_mensagem = codigo, mensagem
        self.repo.salvar_versao(versao)
        self._evento(ctx, versao.documento_id, "ERRO", versao.id, codigo=codigo)

    def _bloquear(
        self, ctx: ContextoAutorizado, versao: DocumentoVersao, codigos: list[str]
    ) -> VersaoDTO:
        """Conteudo sensivel: remove original e trechos; guarda so os codigos dos achados."""
        self.repo.substituir_trechos(ctx.empresa_id, versao.id, [])
        self.armazenamento.apagar(ctx.empresa_id, versao.id)
        versao.status = StatusVersao.BLOQUEADO
        versao.achados_sensiveis = tuple(sorted(set(codigos)))
        versao.erro_codigo = "CONTEUDO_SENSIVEL_DETECTADO"
        versao.erro_mensagem = (
            "O documento parece conter dados sensiveis ("
            + ", ".join(versao.achados_sensiveis)
            + "). Ele foi descartado; remova esses dados e envie de novo."
        )
        versao.processado_em = self.agora()
        self.repo.salvar_versao(versao)
        self._evento(
            ctx, versao.documento_id, "BLOQUEADO", versao.id, achados=list(versao.achados_sensiveis)
        )
        return self._versao_dto(ctx, versao)

    def reprocessar(self, ctx: ContextoAutorizado, versao_id: UUID) -> VersaoDTO:
        self._exigir_rh(ctx)
        versao = self._versao(ctx, versao_id)
        if versao.tentativas >= MAX_TENTATIVAS:
            raise ErroConhecimento(
                "VERSAO_NAO_PRONTA", "Limite de tentativas atingido. Envie uma nova versao."
            )
        return self.processar(ctx, versao_id)

    # -- publicacao -------------------------------------------------------------------------

    def publicar(self, ctx: ContextoAutorizado, versao_id: UUID) -> DocumentoDTO:
        self._exigir_rh(ctx)
        versao = self._versao(ctx, versao_id)
        if versao.status != StatusVersao.PRONTO:
            raise ErroConhecimento(
                "VERSAO_NAO_PRONTA",
                f"So versoes prontas podem ser publicadas (atual: {versao.status.value}).",
            )
        self.repo.publicar_versao(ctx.empresa_id, versao_id, ctx.usuario_id, self.agora())
        self._evento(ctx, versao.documento_id, "PUBLICADO", versao_id)
        return self.obter(ctx, versao.documento_id)

    def despublicar(self, ctx: ContextoAutorizado, versao_id: UUID) -> DocumentoDTO:
        self._exigir_rh(ctx)
        versao = self._versao(ctx, versao_id)
        versao.publicada = False
        self.repo.salvar_versao(versao)
        self._evento(ctx, versao.documento_id, "DESPUBLICADO", versao_id)
        return self.obter(ctx, versao.documento_id)

    # -- metadados, consulta e exclusao -----------------------------------------------------

    def atualizar_metadados(
        self, ctx: ContextoAutorizado, documento_id: UUID, req: AtualizarMetadadosRequest
    ) -> DocumentoDTO:
        self._exigir_rh(ctx)
        doc = self._documento(ctx, documento_id)
        for campo in ("titulo", "categoria", "responsavel", "fonte"):
            valor = getattr(req, campo)
            if valor is not None:
                setattr(doc, campo, valor.strip() if isinstance(valor, str) else valor)
        doc.atualizado_em = self.agora()
        self.repo.salvar_documento(doc)
        self._evento(ctx, doc.id, "METADADOS_ATUALIZADOS")
        return self.obter(ctx, doc.id)

    def excluir(self, ctx: ContextoAutorizado, documento_id: UUID) -> None:
        """Exclusao efetiva: original, versoes e trechos. Fica so o evento sem conteudo."""
        self._exigir_rh(ctx)
        doc = self._documento(ctx, documento_id)
        for versao in self.repo.versoes_do_documento(ctx.empresa_id, doc.id):
            self.armazenamento.apagar(ctx.empresa_id, versao.id)
        self.repo.excluir_documento(ctx.empresa_id, doc.id)
        self._evento(ctx, doc.id, "EXCLUIDO")

    def listar(
        self, ctx: ContextoAutorizado, categoria: CategoriaDocumento | None = None
    ) -> list[DocumentoDTO]:
        self._exigir_rh(ctx)
        docs = self.repo.listar_documentos(ctx.empresa_id, categoria)
        return [
            self.obter(ctx, d.id) for d in sorted(docs, key=lambda d: d.atualizado_em, reverse=True)
        ]

    def obter(self, ctx: ContextoAutorizado, documento_id: UUID) -> DocumentoDTO:
        self._exigir_rh(ctx)
        doc = self._documento(ctx, documento_id)
        versoes = [
            self._versao_dto(ctx, v) for v in self.repo.versoes_do_documento(ctx.empresa_id, doc.id)
        ]
        publicada = next((v for v in versoes if v.publicada), None)
        return DocumentoDTO(
            id=doc.id,
            titulo=doc.titulo,
            categoria=doc.categoria,
            responsavel=doc.responsavel,
            fonte=doc.fonte,
            escopo_acesso=doc.escopo_acesso,
            criado_em=doc.criado_em,
            atualizado_em=doc.atualizado_em,
            versao_publicada=publicada,
            versoes=versoes,
        )

    def _versao_dto(self, ctx: ContextoAutorizado, v: DocumentoVersao) -> VersaoDTO:
        quantidade = self.repo.contar_trechos(ctx.empresa_id, v.id)
        return VersaoDTO(
            id=v.id,
            numero=v.numero,
            rotulo=v.rotulo,
            origem=v.origem,
            status=v.status,
            publicada=v.publicada,
            vigencia_inicio=v.vigencia_inicio,
            vigencia_fim=v.vigencia_fim,
            tamanho_bytes=v.tamanho_bytes,
            nome_arquivo=v.nome_arquivo,
            erro_codigo=v.erro_codigo,
            erro_mensagem=v.erro_mensagem,
            achados_sensiveis=list(v.achados_sensiveis),
            tentativas=v.tentativas,
            criado_em=v.criado_em,
            processado_em=v.processado_em,
            publicada_em=v.publicada_em,
            quantidade_trechos=quantidade,
        )
