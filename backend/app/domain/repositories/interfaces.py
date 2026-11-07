"""Interfaces abstratas de repositorio definindo contratos de dados do Pulso (Clean Architecture)."""

from abc import ABC, abstractmethod
from datetime import date

from app.domain.entities.area import Area
from app.domain.entities.pgr_inventory import PgrRiskItem
from app.domain.entities.risk_card import RiskCard
from app.domain.entities.signals import AreaMonthlyMetrics, ContextEvent
from app.domain.entities.survey import SurveySummary, TeamDevolutivaMessage


class AreaRepository(ABC):
    """Interface abstrata para consulta de areas e contagem de colaboradores."""

    @abstractmethod
    def get_by_id(self, area_id: str) -> Area | None:
        """Recupera os dados cadastrais da area."""
        pass

    @abstractmethod
    def list_all(self) -> list[Area]:
        """Lista todas as areas da organizacao."""
        pass


class SignalRepository(ABC):
    """Interface abstrata para consulta de sinais operacionais agregados e eventos de contexto."""

    @abstractmethod
    def get_metrics_history(self, area_id: str, months: int = 6) -> list[AreaMonthlyMetrics]:
        """Recupera o historico recente de metricas agregadas da area (ultimos 3 a 6 meses)."""
        pass

    @abstractmethod
    def get_company_average_metrics(self, period: date) -> AreaMonthlyMetrics | None:
        """Calcula ou recupera a media consolidada da empresa para comparativo relativo."""
        pass

    @abstractmethod
    def get_context_events(self, area_id: str) -> list[ContextEvent]:
        """Recupera eventos organizacionais (troca de gestor, nova meta) associados a area."""
        pass


class RiskCardRepository(ABC):
    """Interface abstrata para persistencia e consulta dos pontos focais de atencao do RH."""

    @abstractmethod
    def save(self, card: RiskCard) -> RiskCard:
        """Salva ou atualiza um card de risco emitido pelo agente."""
        pass

    @abstractmethod
    def get_by_id(self, card_id: str) -> RiskCard | None:
        """Recupera um card pelo seu identificador unico."""
        pass

    @abstractmethod
    def list_active(self) -> list[RiskCard]:
        """Lista todos os cards abertos aguardando analise humana do RH."""
        pass


class PgrInventoryRepository(ABC):
    """Interface abstrata para controle do inventario de riscos do PGR e plano de acao da NR-1."""

    @abstractmethod
    def save(self, item: PgrRiskItem) -> PgrRiskItem:
        """Salva novo registro formal no inventario do PGR."""
        pass

    @abstractmethod
    def list_all(self) -> list[PgrRiskItem]:
        """Lista todos os itens registrados no inventario de riscos ocupacionais."""
        pass

    @abstractmethod
    def get_by_id(self, item_id: str) -> PgrRiskItem | None:
        """Recupera um item do PGR por identificador."""
        pass


class SurveyRepository(ABC):
    """Interface abstrata para sintese de pesquisas pulso e comunicados de devolutiva."""

    @abstractmethod
    def get_latest_summary(self, area_id: str) -> SurveySummary | None:
        """Recupera a sintese anonima mais recente da pesquisa pulso da area."""
        pass

    @abstractmethod
    def save_summary(self, summary: SurveySummary) -> SurveySummary:
        """Salva a consolidacao anonimizada de uma pesquisa pulso."""
        pass

    @abstractmethod
    def save_devolutiva(self, devolutiva: TeamDevolutivaMessage) -> TeamDevolutivaMessage:
        """Registra a devolutiva ('Voce falou, a empresa fez') destinada a equipe."""
        pass
