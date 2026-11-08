"""Calculos deterministas: ausente e baseline zero nunca se tornam variacao zero."""

from decimal import Decimal

from app.application.contracts.indicators import VariacaoIndicador


def calculate_change(
    code: str,
    current: Decimal | None,
    baseline: Decimal | None,
    unit: str,
    *,
    complete: bool = True,
) -> VariacaoIndicador:
    status = "VALIDO"
    delta = None
    pct = None
    if current is None:
        status = "INDISPONIVEL"
    elif not complete:
        status = "INCOMPLETO"
    elif baseline is None or baseline <= 0:
        status = "SEM_BASELINE"
        delta = current - baseline if baseline is not None else None
    else:
        delta = current - baseline
        pct = (delta / baseline * 100).quantize(Decimal("0.1"))
    return VariacaoIndicador(
        codigo=code,
        atual=current,
        baseline=baseline,
        delta_absoluto=delta,
        delta_percentual=pct,
        unidade=unit,
        qualidade=status,
    )
