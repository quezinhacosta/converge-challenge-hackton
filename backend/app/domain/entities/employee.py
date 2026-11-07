"""Domain entity representing a company employee."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Employee:
    """Represents an employee within the organization for payroll and absence audit.

    Attributes:
        id: Unique identifier of the employee.
        registration_number: Corporate registration code or enrollment ID.
        name: Full legal name of the employee.
        department: Department or operational business unit.
        role: Current job position or title.
        base_salary: Monthly baseline compensation in BRL.
        hire_date: Date of initial employment.
        is_active: Whether the employee is actively employed.
        manager_id: Identifier of the employee's direct supervisor.
    """

    id: str
    registration_number: str
    name: str
    department: str
    role: str
    base_salary: float
    hire_date: date
    is_active: bool = True
    manager_id: Optional[str] = None
