"""Implementacoes de repositorios em memoria do Pulso para execucao dos 7 casos de demonstracao."""

from datetime import date

from app.domain.entities.area import Area
from app.domain.entities.pgr_inventory import PgrRiskItem
from app.domain.entities.risk_card import RiskCard
from app.domain.entities.signals import AreaMonthlyMetrics, ContextEvent
from app.domain.entities.survey import SurveySummary, TeamDevolutivaMessage
from app.domain.repositories.interfaces import (
    AreaRepository,
    PgrInventoryRepository,
    RiskCardRepository,
    SignalRepository,
    SurveyRepository,
)


class InMemoryAreaRepository(AreaRepository):
    """Repositorio em memoria de areas cadastradas."""

    def __init__(self) -> None:
        self._areas: dict[str, Area] = {}

    def save(self, area: Area) -> Area:
        self._areas[area.id] = area
        return area

    def get_by_id(self, area_id: str) -> Area | None:
        return self._areas.get(area_id)

    def list_all(self) -> list[Area]:
        return list(self._areas.values())


class InMemorySignalRepository(SignalRepository):
    """Repositorio em memoria de sinais mensais e eventos de contexto organizacional."""

    def __init__(self) -> None:
        self._metrics: list[AreaMonthlyMetrics] = []
        self._events: list[ContextEvent] = []

    def add_metrics(self, metric: AreaMonthlyMetrics) -> None:
        self._metrics.append(metric)

    def add_event(self, event: ContextEvent) -> None:
        self._events.append(event)

    def get_metrics_history(self, area_id: str, months: int = 6) -> list[AreaMonthlyMetrics]:
        records = [m for m in self._metrics if m.area_id == area_id]
        records.sort(key=lambda m: m.competence_period, reverse=True)
        return records[:months]

    def get_company_average_metrics(self, period: date) -> AreaMonthlyMetrics | None:
        period_metrics = [m for m in self._metrics if m.competence_period == period]
        if not period_metrics:
            return None
        # Stub de media consolidada
        return period_metrics[0]

    def get_context_events(self, area_id: str) -> list[ContextEvent]:
        return [e for e in self._events if e.area_id == area_id]


class InMemoryRiskCardRepository(RiskCardRepository):
    """Repositorio em memoria dos pontos focais de atencao do RH."""

    def __init__(self) -> None:
        self._cards: dict[str, RiskCard] = {}

    def save(self, card: RiskCard) -> RiskCard:
        self._cards[card.id] = card
        return card

    def get_by_id(self, card_id: str) -> RiskCard | None:
        return self._cards.get(card_id)

    def list_all(self) -> list[RiskCard]:
        return list(self._cards.values())

    def list_active(self) -> list[RiskCard]:
        return [c for c in self._cards.values() if c.status.value == "ABERTO"]


class InMemoryPgrInventoryRepository(PgrInventoryRepository):
    """Repositorio em memoria do inventario formal do PGR da NR-1."""

    def __init__(self) -> None:
        self._items: dict[str, PgrRiskItem] = {}

    def save(self, item: PgrRiskItem) -> PgrRiskItem:
        self._items[item.id] = item
        return item

    def list_all(self) -> list[PgrRiskItem]:
        return list(self._items.values())

    def get_by_id(self, item_id: str) -> PgrRiskItem | None:
        return self._items.get(item_id)


class InMemorySurveyRepository(SurveyRepository):
    """Repositorio em memoria para pesquisas pulso e devolutivas."""

    def __init__(self) -> None:
        self._summaries: dict[str, SurveySummary] = {}
        self._devolutivas: dict[str, TeamDevolutivaMessage] = {}

    def get_latest_summary(self, area_id: str) -> SurveySummary | None:
        return self._summaries.get(area_id)

    def save_summary(self, summary: SurveySummary) -> SurveySummary:
        self._summaries[summary.area_id] = summary
        return summary

    def save_devolutiva(self, devolutiva: TeamDevolutivaMessage) -> TeamDevolutivaMessage:
        self._devolutivas[devolutiva.id] = devolutiva
        return devolutiva
