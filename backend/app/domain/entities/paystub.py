"""Domain entity representing monthly payroll entries and wage components."""

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass
class PaystubItem:
    """Individual line item or code on an employee's paystub (holerite).

    Attributes:
        code: Internal rubric or eSocial rubric code.
        description: Description of the credit or debit entry.
        reference_units: Quantity of hours, days, or percentage (e.g., 20 overtime hours).
        amount: Monetary value in BRL.
        is_discount: True if this item reduces gross pay (e.g., INSS, IRRF, unjustified absences).
    """

    code: str
    description: str
    reference_units: float
    amount: float
    is_discount: bool = False


@dataclass
class Paystub:
    """Represents a monthly paystub record for auditing and employee transparency.

    Attributes:
        id: Unique identifier of the paystub.
        employee_id: Identifier of the employee receiving compensation.
        competence_period: Year and month of the payroll period (e.g. 2026-10-01).
        base_salary: Contracted base monthly compensation.
        overtime_hours_current_month: Total overtime hours logged in this period.
        overtime_hours_3m_average: Rolling 3-month average of overtime hours for anomaly comparison.
        sector_overtime_standard_deviation: Deviation from the departmental peer baseline.
        substitution_salary_differential: Proportional wage difference under Súmula 159 TST.
        gross_total: Total gross earnings before statutory discounts.
        net_total: Final net payable amount.
        items: List of all rubric entries composing the paystub.
    """

    id: str
    employee_id: str
    competence_period: date
    base_salary: float
    overtime_hours_current_month: float
    overtime_hours_3m_average: float
    sector_overtime_standard_deviation: float
    substitution_salary_differential: float
    gross_total: float
    net_total: float
    items: List[PaystubItem] = field(default_factory=list)
