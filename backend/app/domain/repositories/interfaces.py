"""Interfaces abstratas de repositorio definindo contratos de acesso a dados (Clean Architecture)."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.domain.entities.absence import Absence
from app.domain.entities.anomaly import Anomaly
from app.domain.entities.employee import Employee
from app.domain.entities.paystub import Paystub


class EmployeeRepository(ABC):
    """Interface abstrata para persistencia e consulta de colaboradores."""

    @abstractmethod
    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        """Recupera um colaborador pelo identificador unico."""
        pass

    @abstractmethod
    def list_all(self) -> List[Employee]:
        """Lista todos os colaboradores cadastrados na organizacao."""
        pass


class PayrollRepository(ABC):
    """Interface abstrata para armazenamento e consulta de lotes de folha e holerites."""

    @abstractmethod
    def save_paystub(self, paystub: Paystub) -> Paystub:
        """Persiste ou atualiza o holerite auditado de um colaborador."""
        pass

    @abstractmethod
    def get_by_period(self, competence_period: date) -> List[Paystub]:
        """Recupera todos os holerites de uma determinada competencia."""
        pass

    @abstractmethod
    def get_by_employee_and_period(
        self, employee_id: str, competence_period: date
    ) -> Optional[Paystub]:
        """Recupera o holerite de um colaborador especifico em uma dada competencia."""
        pass


class AbsenceRepository(ABC):
    """Interface abstrata para controle de atestados medicos, afastamentos e conflitos com ferias."""

    @abstractmethod
    def save(self, absence: Absence) -> Absence:
        """Persiste um novo registro de afastamento ou atualiza um existente."""
        pass

    @abstractmethod
    def get_by_employee(self, employee_id: str) -> List[Absence]:
        """Recupera todos os registros de afastamento associados a um colaborador."""
        pass

    @abstractmethod
    def find_overlapping_vacations(
        self, employee_id: str, start_date: date, end_date: date
    ) -> List[Absence]:
        """Verifica se existem ferias agendadas com periodo coincidente ao afastamento solicitado."""
        pass


class AnomalyRepository(ABC):
    """Interface abstrata para persistencia e consulta de anomalias detectadas na folha."""

    @abstractmethod
    def save(self, anomaly: Anomaly) -> Anomaly:
        """Salva uma nova anomalia identificada pelo motor preditivo."""
        pass

    @abstractmethod
    def list_unresolved(self) -> List[Anomaly]:
        """Lista todos os apontamentos pendentes que necessitam de analise humana do DP."""
        pass

    @abstractmethod
    def mark_as_resolved(
        self, anomaly_id: str, resolution_notes: str, approved: bool
    ) -> Optional[Anomaly]:
        """Atualiza o estado da anomalia apos a tomada de decisao em 1 clique pelo analista."""
        pass
