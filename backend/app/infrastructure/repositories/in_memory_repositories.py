"""In-memory repository implementations for local development and unit tests."""

from datetime import date
from typing import Dict, List, Optional

from app.domain.entities.absence import Absence
from app.domain.entities.anomaly import Anomaly
from app.domain.entities.employee import Employee
from app.domain.entities.paystub import Paystub
from app.domain.repositories.interfaces import (
    AbsenceRepository,
    AnomalyRepository,
    EmployeeRepository,
    PayrollRepository,
)


class InMemoryEmployeeRepository(EmployeeRepository):
    """In-memory store for employee test fixtures."""

    def __init__(self) -> None:
        self._employees: Dict[str, Employee] = {}

    def get_by_id(self, employee_id: str) -> Optional[Employee]:
        """Fetch employee by ID from memory store."""
        return self._employees.get(employee_id)

    def list_all(self) -> List[Employee]:
        """List all stored employees."""
        return list(self._employees.values())


class InMemoryPayrollRepository(PayrollRepository):
    """In-memory store for paystub and batch records."""

    def __init__(self) -> None:
        self._paystubs: Dict[str, Paystub] = {}

    def save_paystub(self, paystub: Paystub) -> Paystub:
        """Store paystub in memory."""
        self._paystubs[paystub.id] = paystub
        return paystub

    def get_by_period(self, competence_period: date) -> List[Paystub]:
        """Filter paystubs by period."""
        return [
            p for p in self._paystubs.values() if p.competence_period == competence_period
        ]

    def get_by_employee_and_period(
        self, employee_id: str, competence_period: date
    ) -> Optional[Paystub]:
        """Find paystub for employee in period."""
        for p in self._paystubs.values():
            if p.employee_id == employee_id and p.competence_period == competence_period:
                return p
        return None


class InMemoryAbsenceRepository(AbsenceRepository):
    """In-memory store for leaves and medical certificates."""

    def __init__(self) -> None:
        self._absences: Dict[str, Absence] = {}

    def save(self, absence: Absence) -> Absence:
        """Store absence record."""
        self._absences[absence.id] = absence
        return absence

    def get_by_employee(self, employee_id: str) -> List[Absence]:
        """List absences for an employee."""
        return [a for a in self._absences.values() if a.employee_id == employee_id]

    def find_overlapping_vacations(
        self, employee_id: str, start_date: date, end_date: date
    ) -> List[Absence]:
        """Check for vacation date range intersections."""
        overlaps: List[Absence] = []
        for a in self._absences.values():
            if a.employee_id == employee_id and a.absence_type.value == "VACATION":
                if not (end_date < a.start_date or start_date > a.end_date):
                    overlaps.append(a)
        return overlaps


class InMemoryAnomalyRepository(AnomalyRepository):
    """In-memory store for detected anomalies and review resolutions."""

    def __init__(self) -> None:
        self._anomalies: Dict[str, Anomaly] = {}

    def save(self, anomaly: Anomaly) -> Anomaly:
        """Store anomaly finding."""
        self._anomalies[anomaly.id] = anomaly
        return anomaly

    def list_unresolved(self) -> List[Anomaly]:
        """List unresolved anomaly alerts for DP."""
        return [a for a in self._anomalies.values() if not a.is_resolved]

    def mark_as_resolved(
        self, anomaly_id: str, resolution_notes: str, approved: bool
    ) -> Optional[Anomaly]:
        """Update anomaly state upon DP review."""
        anomaly = self._anomalies.get(anomaly_id)
        if anomaly:
            anomaly.is_resolved = True
            anomaly.resolution_notes = resolution_notes
        return anomaly
