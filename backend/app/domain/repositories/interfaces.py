"""Abstract repository protocols defining data access contracts for clean architecture."""

from abc import ABC, abstractmethod
from datetime import date
from typing import List, Optional

from app.domain.entities.absence import Absence
from app.domain.entities.anomaly import Anomaly
from app.domain.entities.employee import Employee
from app.domain.entities.paystub import Paystub


class EmployeeRepository(ABC):
    """Abstract interface for managing employee persistence and queries."""

    @abstractmethod
    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        """Retrieve an employee by their unique identifier."""
        pass

    @abstractmethod
    def list_all(self) -> List[Employee]:
        """List all registered employees in the organization."""
        pass


class PayrollRepository(ABC):
    """Abstract interface for storing and querying payroll batches and individual paystubs."""

    @abstractmethod
    def save_paystub(self, paystub: Paystub) -> Paystub:
        """Persist or update an audited paystub record."""
        pass

    @abstractmethod
    def get_by_period(self, competence_period: date) -> List[Paystub]:
        """Retrieve all paystubs belonging to a given competence period."""
        pass

    @abstractmethod
    def get_by_employee_and_period(
        self, employee_id: str, competence_period: date
    ) -> Optional[Paystub]:
        """Retrieve the paystub of a specific employee for a given period."""
        pass


class AbsenceRepository(ABC):
    """Abstract interface for tracking medical certificates, leaves, and vacation overlaps."""

    @abstractmethod
    def save(self, absence: Absence) -> Absence:
        """Persist a new or updated absence record."""
        pass

    @abstractmethod
    def get_by_employee(self, employee_id: str) -> List[Absence]:
        """Retrieve all absence records associated with a given employee."""
        pass

    @abstractmethod
    def find_overlapping_vacations(
        self, employee_id: str, start_date: date, end_date: date
    ) -> List[Absence]:
        """Check for active or scheduled vacation periods overlapping with a requested leave."""
        pass


class AnomalyRepository(ABC):
    """Abstract interface for storing and querying detected fraud risks and audit findings."""

    @abstractmethod
    def save(self, anomaly: Anomaly) -> Anomaly:
        """Save a newly detected payroll anomaly."""
        pass

    @abstractmethod
    def list_unresolved(self) -> List[Anomaly]:
        """Retrieve all pending anomalies requiring Human-in-the-Loop review from DP."""
        pass

    @abstractmethod
    def mark_as_resolved(
        self, anomaly_id: str, resolution_notes: str, approved: bool
    ) -> Optional[Anomaly]:
        """Update an anomaly status following 1-click human analyst resolution."""
        pass
