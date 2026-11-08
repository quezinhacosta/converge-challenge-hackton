"""Tarefas do digital worker apoiadas na base de conhecimento (sem LLM, deterministicas).

1. investigar: antes de montar um caso, levanta o que a empresa ja oferece (programas, canais,
   procedimentos), o que ja foi tentado (planos anteriores) e o que a politica diz.
2. catalogo de acoes: so recomenda/executa acoes que existem em documento publicado.
3. cuidar da base: vencimentos, vencidos ainda publicados, prontos sem publicar, erros,
   bloqueios e lacunas por fator de risco. Cada pendencia vira tarefa para o responsavel.
4. memoria de decisoes: a decisao do RH vira documento citavel (PLANO_ACAO_ANTERIOR), sem
   dados de pessoas, para orientar casos futuros. Nao e treino de modelo.

Nada aqui altera score, nivel, fator ou indicadores.
"""

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Literal

from app.knowledge.domain import CategoriaDocumento, ContextoAutorizado, StatusVersao
from app.knowledge.dtos import CadastroTextoRequest, ConsultaRecuperacao, TrechoRecuperado
from app.knowledge.repository import RepositorioConhecimento
from app.knowledge.retrieval import RecuperadorConhecimento
from app.knowledge.service import ServicoConhecimento
from app.knowledge.text_search import EXPANSAO_POR_FATOR

CATEGORIAS_DE_ACAO = (
    CategoriaDocumento.PROGRAMA_BENEFICIO,
    CategoriaDocumento.CANAL_APOIO,
    CategoriaDocumento.PROCEDIMENTO_ACOLHIMENTO,
)
JANELA_VENCIMENTO_DIAS = 30
DIAS_PRONTO_SEM_PUBLICAR = 7

TipoPendencia = Literal[
    "VENCENDO",
    "VENCIDO_PUBLICADO",
    "PRONTO_SEM_PUBLICAR",
    "ERRO_PROCESSAMENTO",
    "BLOQUEADO_SENSIVEL",
    "LACUNA_FATOR",
    "SEM_CANAL_DE_APOIO",
]


@dataclass(frozen=True)
class AcaoDisponivel:
    """Acao que a empresa oferece, com o trecho que a sustenta."""

    categoria: CategoriaDocumento
    titulo_documento: str
    trecho: TrechoRecuperado


@dataclass(frozen=True)
class InvestigacaoDocumental:
    fator: str | None
    acoes_disponiveis: list[AcaoDisponivel]
    planos_anteriores: list[TrechoRecuperado]
    politicas: list[TrechoRecuperado]
    lacunas: list[str]

    @property
    def tem_acao_da_empresa(self) -> bool:
        return bool(self.acoes_disponiveis)

    def trechos(self) -> list[TrechoRecuperado]:
        """Todos os trechos com refs unicas (C1..Cn), prontos para o prompt/citacoes."""
        todos = [a.trecho for a in self.acoes_disponiveis] + self.planos_anteriores + self.politicas
        vistos: dict[str, TrechoRecuperado] = {}
        for t in todos:
            if str(t.trecho_id) not in vistos:
                vistos[str(t.trecho_id)] = t.model_copy(update={"ref": f"C{len(vistos) + 1}"})
        return list(vistos.values())


@dataclass(frozen=True)
class PendenciaBase:
    tipo: TipoPendencia
    mensagem: str
    responsavel: str | None = None
    documento_id: str | None = None
    versao_id: str | None = None
    prazo: date | None = None
    fator: str | None = None


@dataclass
class RelatorioBase:
    gerado_em: date
    pendencias: list[PendenciaBase] = field(default_factory=list)

    def por_tipo(self, tipo: TipoPendencia) -> list[PendenciaBase]:
        return [p for p in self.pendencias if p.tipo == tipo]


class AssistenteDocumental:
    """Instancia por requisicao (recebe o contexto em cada chamada; nao guarda empresa)."""

    def __init__(
        self,
        recuperador: RecuperadorConhecimento,
        repositorio: RepositorioConhecimento,
        servico: ServicoConhecimento,
    ) -> None:
        self.recuperador = recuperador
        self.repo = repositorio
        self.servico = servico

    # -- 1 e 2: investigacao e catalogo de acoes --------------------------------------------

    def _buscar(
        self,
        ctx: ContextoAutorizado,
        texto: str,
        categorias: tuple[CategoriaDocumento, ...],
        fator: str | None,
        dia: date,
        maximo: int,
    ) -> list[TrechoRecuperado]:
        resultado = self.recuperador.buscar(
            ctx,
            ConsultaRecuperacao(
                texto=texto[:500],
                categorias=list(categorias),
                fator_nr1=fator,
                max_trechos=maximo,
                data_referencia=dia,
            ),
        )
        return resultado.trechos

    def investigar(
        self,
        ctx: ContextoAutorizado,
        fator: str | None,
        area_nome: str | None = None,
        eventos: list[str] | None = None,
        dia: date | None = None,
    ) -> InvestigacaoDocumental:
        """Consulta a base ANTES de montar o caso. Deterministica: nao chama LLM."""
        dia = dia or date.today()
        termos = " ".join(EXPANSAO_POR_FATOR.get(fator or "", ()))
        base = " ".join(filter(None, [termos, area_nome or "", " ".join(eventos or [])])) or "apoio"
        acoes: list[AcaoDisponivel] = []
        for categoria in CATEGORIAS_DE_ACAO:
            for t in self._buscar(ctx, base, (categoria,), fator, dia, 2):
                acoes.append(AcaoDisponivel(categoria, t.titulo, t))
        planos = self._buscar(ctx, base, (CategoriaDocumento.PLANO_ACAO_ANTERIOR,), fator, dia, 3)
        politicas = self._buscar(ctx, base, (CategoriaDocumento.POLITICA,), fator, dia, 2)
        lacunas = []
        if not acoes:
            lacunas.append("Nenhum programa, canal ou procedimento publicado cobre este fator.")
        if not politicas:
            lacunas.append("Nenhuma politica publicada sobre este fator.")
        return InvestigacaoDocumental(fator, acoes, planos, politicas, lacunas)

    # -- 3: cuidar da base ------------------------------------------------------------------

    def revisar_base(self, ctx: ContextoAutorizado, dia: date | None = None) -> RelatorioBase:
        """Pendencias da base, cada uma com responsavel e prazo sugerido."""
        dia = dia or date.today()
        relatorio = RelatorioBase(gerado_em=dia)
        add = relatorio.pendencias.append
        for doc in self.repo.listar_documentos(ctx.empresa_id):
            versoes = self.repo.versoes_do_documento(ctx.empresa_id, doc.id)
            publicada = next((v for v in versoes if v.publicada), None)
            ultima = versoes[-1] if versoes else None
            ids = {"responsavel": doc.responsavel, "documento_id": str(doc.id)}
            if publicada and publicada.vigencia_fim:
                if publicada.vigencia_fim <= dia:
                    add(
                        PendenciaBase(
                            "VENCIDO_PUBLICADO",
                            f'"{doc.titulo}" venceu em {publicada.vigencia_fim:%d/%m/%Y} e saiu das '
                            "respostas. Publique uma versao atualizada.",
                            versao_id=str(publicada.id),
                            prazo=dia,
                            **ids,
                        )
                    )
                elif publicada.vigencia_fim <= dia + timedelta(days=JANELA_VENCIMENTO_DIAS):
                    add(
                        PendenciaBase(
                            "VENCENDO",
                            f'"{doc.titulo}" vence em {publicada.vigencia_fim:%d/%m/%Y}. Revise e '
                            "publique a nova versao antes disso.",
                            versao_id=str(publicada.id),
                            prazo=publicada.vigencia_fim,
                            **ids,
                        )
                    )
            if ultima is None or ultima.publicada:
                continue
            if (
                ultima.status == StatusVersao.PRONTO
                and (dia - ultima.criado_em.date()).days >= DIAS_PRONTO_SEM_PUBLICAR
            ):
                add(
                    PendenciaBase(
                        "PRONTO_SEM_PUBLICAR",
                        f'"{doc.titulo}" ({ultima.rotulo}) esta pronto ha mais de '
                        f"{DIAS_PRONTO_SEM_PUBLICAR} dias e ainda nao foi publicado.",
                        versao_id=str(ultima.id),
                        prazo=dia + timedelta(days=3),
                        **ids,
                    )
                )
            elif ultima.status == StatusVersao.ERRO:
                add(
                    PendenciaBase(
                        "ERRO_PROCESSAMENTO",
                        f'"{doc.titulo}" ({ultima.rotulo}) falhou: {ultima.erro_mensagem}',
                        versao_id=str(ultima.id),
                        prazo=dia + timedelta(days=3),
                        **ids,
                    )
                )
            elif ultima.status == StatusVersao.BLOQUEADO:
                add(
                    PendenciaBase(
                        "BLOQUEADO_SENSIVEL",
                        f'"{doc.titulo}" ({ultima.rotulo}) foi bloqueado por dados sensiveis '
                        f"({', '.join(ultima.achados_sensiveis)}). Envie uma versao sem esses dados.",
                        versao_id=str(ultima.id),
                        prazo=dia + timedelta(days=3),
                        **ids,
                    )
                )
        for fator in EXPANSAO_POR_FATOR:
            if fator == "ASSEDIO":
                continue  # tratado pelo compliance; nao exige programa no catalogo
            if not self.investigar(ctx, fator, dia=dia).tem_acao_da_empresa:
                add(
                    PendenciaBase(
                        "LACUNA_FATOR",
                        f"Nao ha programa, canal ou procedimento publicado para {fator}. "
                        "Sem isso o VytAI so consegue sugerir medidas genericas.",
                        fator=fator,
                        prazo=dia + timedelta(days=15),
                    )
                )
        # Estrutural (nao lexical): basta um documento de canal publicado e vigente.
        if not self.repo.trechos_elegiveis(
            ctx.empresa_id,
            ctx.escopos_permitidos,
            dia,
            frozenset({CategoriaDocumento.CANAL_APOIO}),
        ):
            add(
                PendenciaBase(
                    "SEM_CANAL_DE_APOIO",
                    "Nenhum canal de apoio psicologico publicado. E a primeira informacao que o "
                    "VytAI precisa para orientar casos de risco.",
                    prazo=dia + timedelta(days=7),
                )
            )
        return relatorio

    # -- 4: memoria de decisoes -------------------------------------------------------------

    def registrar_decisao(
        self,
        ctx: ContextoAutorizado,
        *,
        area_nome: str,
        fator: str,
        periodo: str,
        decisao: Literal["APROVADA", "AJUSTADA", "DESCARTADA"],
        acao: str,
        justificativa: str | None = None,
        resultado: str | None = None,
    ) -> None:
        """Transforma a decisao do RH em documento publicado e citavel.

        Passa pela mesma triagem de conteudo sensivel; texto com dado de pessoa e bloqueado.
        """
        linhas = [
            f"# Decisao do RH - {fator} - {area_nome} - {periodo}",
            "",
            f"Decisao: {decisao.lower()}.",
            f"Acao: {acao.strip()}",
        ]
        if justificativa:
            linhas.append(f"Justificativa: {justificativa.strip()}")
        if resultado:
            linhas.append(f"Resultado observado: {resultado.strip()}")
        doc = self.servico.cadastrar_texto(
            ctx,
            CadastroTextoRequest(
                titulo=f"Decisao {fator} - {area_nome} - {periodo}"[:200],
                categoria=CategoriaDocumento.PLANO_ACAO_ANTERIOR,
                responsavel="RH (registro automatico do VytAI)",
                fonte="Decisao registrada no VytAI",
                texto="\n".join(linhas),
                confirma_sem_dados_sensiveis=True,
            ),
        )
        versao = doc.versoes[-1]
        if versao.status == StatusVersao.PRONTO:
            self.servico.publicar(ctx, versao.id)
