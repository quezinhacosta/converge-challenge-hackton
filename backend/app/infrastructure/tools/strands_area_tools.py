"""Ferramentas Strands do agente de chat. Todas trabalham por AREA e respeitam o minimo de 5.

Essas mesmas funcoes podem ser expostas depois num servidor MCP (parte B), sem mudar regras.
"""

import unicodedata
from typing import Any

from app.application.use_cases.collect_and_aggregate_signals_use_case import (
    CollectAndAggregateSignalsUseCase,
)
from app.domain.repositories.interfaces import AreaRepository


def _normalize(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return stripped.lower().strip()


def _to_dict(dto: Any) -> dict[str, Any]:
    if hasattr(dto, "model_dump"):
        return dict(dto.model_dump(mode="json"))
    return dict(vars(dto))


def build_area_tools(
    area_repository: AreaRepository,
    collect_signals_use_case: CollectAndAggregateSignalsUseCase,
) -> list[Any]:
    """Cria as ferramentas do chat. Devolve lista vazia se o strands nao estiver instalado."""
    try:
        from strands import tool
    except ImportError:
        return []

    def resolve_area_id(area: str) -> str | None:
        wanted = _normalize(area)
        for item in area_repository.list_all():
            if wanted in {_normalize(item.id), _normalize(item.name)}:
                return item.id
        for item in area_repository.list_all():
            if wanted in _normalize(item.name):
                return item.id
        return None

    @tool
    def listar_areas() -> list[dict[str, Any]]:
        """Lista as areas monitoradas com numero de pessoas e se os dados estao ocultos (LGPD)."""
        return [
            {
                "area_id": a.id,
                "nome": a.name,
                "pessoas": a.headcount,
                "dados_ocultos_lgpd": not a.is_eligible_for_analytics,
            }
            for a in area_repository.list_all()
        ]

    @tool
    def sinais_da_area(area: str) -> dict[str, Any]:
        """Indicadores agregados de uma area (variacao de atestados, horas extras, demissoes,
        nota de carga e eventos de contexto). Aceita o id ou o nome da area.

        Args:
            area: Id ou nome da area, por exemplo "Logistica" ou "area_log".
        """
        area_id = resolve_area_id(area)
        if area_id is None:
            return {"erro": f"Area '{area}' nao encontrada. Use listar_areas."}
        data = _to_dict(collect_signals_use_case.execute(area_id))
        if data.get("is_anonymized"):
            return {
                "area": data.get("area_name"),
                "dados_ocultos_lgpd": True,
                "motivo": "Area com menos de 5 pessoas; dados agregados ao nivel superior.",
            }
        return data

    return [listar_areas, sinais_da_area]
