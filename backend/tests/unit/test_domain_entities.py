"""Unit test suite for domain entity construction and structural integrity."""

from datetime import date
from app.domain.entities.absence import Absence, AbsenceStatus, AbsenceType
from app.domain.entities.anomaly import Anomaly, AnomalyCategory, RiskSeverity
from app.domain.entities.employee import Employee
from app.domain.entities.paystub import Paystub, PaystubItem


def test_employee_entity_initialization() -> None:
    """Validate Employee entity creation with standard contracts."""
    employee = Employee(
        id="emp_01",
        registration_number="REG-10023",
        name="Carlos Silva",
        department="Operations",
        role="Machine Operator",
        base_salary=4200.0,
        hire_date=date(2022, 5, 10),
    )
    assert employee.id == "emp_01"
    assert employee.base_salary == 4200.0
    assert employee.is_active is True


def test_absence_entity_rules() -> None:
    """Validate Absence entity attributes under INSS 15-day distribution rule."""
    absence = Absence(
        id="abs_01",
        employee_id="emp_01",
        absence_type=AbsenceType.MEDICAL,
        start_date=date(2026, 10, 1),
        end_date=date(2026, 10, 20),
        duration_days=20,
        company_paid_days=15,
        inss_paid_days=5,
        status=AbsenceStatus.FORWARDED_TO_INSS,
        requires_inss_scheduling=True,
    )
    assert absence.duration_days == 20
    assert absence.company_paid_days == 15
    assert absence.inss_paid_days == 5
    assert absence.requires_inss_scheduling is True


def test_paystub_and_anomaly_entities() -> None:
    """Validate Paystub line item and Anomaly score tracking."""
    item = PaystubItem(
        code="HE_050",
        description="Horas Extras 50%",
        reference_units=30.0,
        amount=1250.0,
    )
    paystub = Paystub(
        id="ps_01",
        employee_id="emp_01",
        competence_period=date(2026, 10, 1),
        base_salary=4200.0,
        overtime_hours_current_month=30.0,
        overtime_hours_3m_average=8.0,
        sector_overtime_standard_deviation=18.5,
        substitution_salary_differential=0.0,
        gross_total=5450.0,
        net_total=4350.0,
        items=[item],
    )
    anomaly = Anomaly(
        id="anom_01",
        paystub_id=paystub.id,
        employee_id="emp_01",
        category=AnomalyCategory.OVERTIME_SPIKE,
        severity=RiskSeverity.HIGH,
        paytrust_score=94.5,
        explanation="Overtime spike of 275% compared to 3-month rolling average.",
        suggested_action="Hold overtime disbursement and review timecards.",
    )
    assert anomaly.paytrust_score == 94.5
    assert anomaly.severity == RiskSeverity.HIGH
    assert anomaly.is_resolved is False
