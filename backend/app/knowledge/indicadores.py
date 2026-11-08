"""Projecao do contrato IndicadoresArea (v1) para marcadores {{ind:...}} do prompt.

O RAG nunca recalcula nem altera indicadores: so expoe ao modelo os valores ja validados
(qualidade VALIDO), cada um com metrica, area, periodo e unidade. Sem elegibilidade/quorum,
nenhum numero da area e exposto.
"""

from decimal import Decimal

from app.application.contracts.indicators import IndicadoresArea
from app.knowledge.grounding import IndicadorReferenciavel


def _fmt(valor: Decimal) -> str:
    texto = format(valor.normalize(), "f")
    return texto if "." in texto else texto.rstrip("0").rstrip(".") or "0"


def indicadores_para_prompt(ind: IndicadoresArea, area_nome: str) -> list[IndicadorReferenciavel]:
    if ind.estado != "ELEGIVEL" or ind.quorum_ok is not True:
        return []
    periodo = f"{ind.periodo.inicio:%m/%Y}"
    saida: list[IndicadorReferenciavel] = []
    if ind.score is not None:
        saida.append(
            IndicadorReferenciavel(
                f"{ind.area_id}.score",
                "score de risco psicossocial",
                _fmt(ind.score),
                "/100",
                area_nome,
                periodo,
            )
        )
    for v in ind.variacoes:
        if v.qualidade != "VALIDO":
            continue
        if v.delta_percentual is not None:
            saida.append(
                IndicadorReferenciavel(
                    f"{ind.area_id}.{v.codigo}_var",
                    f"variacao de {v.codigo} contra a linha de base",
                    _fmt(v.delta_percentual),
                    "%",
                    area_nome,
                    periodo,
                )
            )
        if v.atual is not None:
            saida.append(
                IndicadorReferenciavel(
                    f"{ind.area_id}.{v.codigo}",
                    f"{v.codigo} no periodo",
                    _fmt(v.atual),
                    f" {v.unidade}".rstrip(),
                    area_nome,
                    periodo,
                )
            )
    return saida
