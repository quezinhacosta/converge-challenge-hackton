"""Implementacoes concretas dos repositorios de infraestrutura."""

from app.infrastructure.repositories.in_memory_repositories import (
    InMemoryAbsenceRepository,
    InMemoryAnomalyRepository,
    InMemoryEmployeeRepository,
    InMemoryPayrollRepository,
)

__all__ = [
    "InMemoryEmployeeRepository",
    "InMemoryPayrollRepository",
    "InMemoryAbsenceRepository",
    "InMemoryAnomalyRepository",
]
