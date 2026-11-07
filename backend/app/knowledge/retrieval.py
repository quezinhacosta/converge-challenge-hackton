"""Recuperacao autorizada de trechos (filtros de acesso aplicados ANTES do ranking)."""

import time
from datetime import date
from typing import Protocol

from app.knowledge.domain import ContextoAutorizado
from app.knowledge.dtos import ConsultaRecuperacao, ResultadoRecuperacao, TrechoRecuperado
from app.knowledge.repository import RepositorioConhecimento, TrechoElegivel
from app.knowledge.text_search import EXPANSAO_POR_FATOR, ranquear_bm25, termos

# Relevancia por cobertura dos termos da PERGUNTA (nao da expansao): estavel com bases pequenas,
# onde um limite absoluto de BM25 falha. O BM25 so ordena.
MIN_TERMOS_COBERTOS = 2
PESO_SECAO_TITULO = 0.5


class RecuperadorConhecimento(Protocol):
    def buscar(
        self, ctx: ContextoAutorizado, consulta: ConsultaRecuperacao
    ) -> ResultadoRecuperacao: ...


class RecuperadorTextual:
    """Ranking BM25 sobre os trechos ja autorizados. Compartilhavel entre requisicoes:
    nao guarda contexto de empresa; o contexto chega em cada chamada."""

    def __init__(self, repositorio: RepositorioConhecimento, min_termos: int = MIN_TERMOS_COBERTOS):
        self.repo = repositorio
        self.min_termos = min_termos

    def buscar(
        self, ctx: ContextoAutorizado, consulta: ConsultaRecuperacao
    ) -> ResultadoRecuperacao:
        inicio = time.perf_counter()
        dia = consulta.data_referencia or date.today()
        categorias = frozenset(consulta.categorias) if consulta.categorias else None
        candidatos = self.repo.trechos_elegiveis(
            ctx.empresa_id, ctx.escopos_permitidos, dia, categorias
        )
        config: dict[str, float | int | str] = {
            "min_termos_cobertos": self.min_termos,
            "peso_secao_titulo": PESO_SECAO_TITULO,
            "max_trechos": consulta.max_trechos,
        }
        if not candidatos:
            return self._resultado(
                [], "Nenhum documento publicado e vigente para esta consulta.", inicio, config
            )

        termos_pergunta = set(termos(consulta.texto))
        exigidos = min(self.min_termos, len(termos_pergunta)) or 1
        texto_consulta = consulta.texto
        if consulta.fator_nr1 in EXPANSAO_POR_FATOR:
            texto_consulta += " " + " ".join(EXPANSAO_POR_FATOR[consulta.fator_nr1])
        q = termos(texto_consulta)
        corpo = [termos(c.trecho.texto) for c in candidatos]
        extra = [termos(f"{c.documento.titulo} {c.trecho.secao or ''}") for c in candidatos]
        base = ranquear_bm25(q, corpo)
        bonus = ranquear_bm25(q, extra)
        pontuados = sorted(
            (
                (b + PESO_SECAO_TITULO * x, len(termos_pergunta & (set(t) | set(e))), c)
                for b, x, t, e, c in zip(base, bonus, corpo, extra, candidatos, strict=True)
            ),
            key=lambda item: item[0],
            reverse=True,
        )
        selecionados: list[tuple[float, TrechoElegivel]] = []
        orcamento = consulta.max_caracteres
        for score, cobertos, cand in pontuados:
            if len(selecionados) >= consulta.max_trechos:
                break
            if cobertos < exigidos or len(cand.trecho.texto) > orcamento:
                continue
            orcamento -= len(cand.trecho.texto)
            selecionados.append((score, cand))
        motivo = (
            None
            if selecionados
            else "Nenhum trecho relevante o suficiente nos documentos publicados."
        )
        return self._resultado(selecionados, motivo, inicio, config)

    @staticmethod
    def _resultado(
        selecionados: list[tuple[float, TrechoElegivel]],
        motivo: str | None,
        inicio: float,
        config: dict[str, float | int | str],
    ) -> ResultadoRecuperacao:
        trechos = [
            TrechoRecuperado(
                ref=f"C{i}",
                trecho_id=c.trecho.id,
                documento_id=c.documento.id,
                versao_id=c.versao.id,
                titulo=c.documento.titulo,
                categoria=c.documento.categoria,
                versao_numero=c.versao.numero,
                versao_rotulo=c.versao.rotulo,
                vigencia_inicio=c.versao.vigencia_inicio,
                vigencia_fim=c.versao.vigencia_fim,
                pagina=c.trecho.pagina,
                secao=c.trecho.secao,
                texto=c.trecho.texto,
                score=round(score, 3),
                suspeito_injecao=c.trecho.suspeito_injecao,
            )
            for i, (score, c) in enumerate(selecionados, start=1)
        ]
        # Heuristica de conflito: documentos DIFERENTES da mesma categoria entre os recuperados.
        conflitos: list[list[str]] = []
        for i, a in enumerate(trechos):
            for b in trechos[i + 1 :]:
                if a.categoria == b.categoria and a.documento_id != b.documento_id:
                    conflitos.append([a.ref, b.ref])
        return ResultadoRecuperacao(
            trechos=trechos,
            evidencia_suficiente=bool(trechos),
            motivo_insuficiencia=motivo,
            possivel_conflito=conflitos,
            metodo="texto_bm25",
            config=config,
            latencia_ms=int((time.perf_counter() - inicio) * 1000),
        )
