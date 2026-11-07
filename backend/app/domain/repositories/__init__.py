"""Domain repository interfaces."""

from app.domain.repositories.interfaces import (
    AbsenceRepository,
    AnomalyRepository,
    EmployeeRepository,
    PayrollRepository,
)

__all__ = [
    "EmployeeRepository",
    "PayrollRepository",
    "AbsenceRepository",
    "AnomalyRepository",
]
