"""Suite de testes unitarios validando integridade estrutural das entidades do dominio."""

from datetime import date
from app.domain.entities.absence import Absence, AbsenceStatus, AbsenceType
from app.domain.entities.anomaly import Anomaly, AnomalyCategory, RiskSeverity
from app.domain.entities.employee import Employee
from app.domain.entities.paystub import Paystub, PaystubItem


def test_employee_entity_initialization() -> None:
    """Valida a criacao e atributos da entidade Employee."""
    employee = Employee(
        id="emp_01",
        registration_number="REG-10023",
        name="Carlos Silva",
        department="Operacoes",
        role="Operador de Maquinas",
        base_salary=4200.0,
        hire_date=date(2022, 5, 10),
    )
    assert employee.id == "emp_01"
    assert employee.base_salary == 4200.0
    assert employee.is_active is True


def test_absence_entity_rules() -> None:
    """Valida as regras de negocio de divisao legal dos 15 dias CLT vs. INSS em Absence."""
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
    """Valida os lancamentos do holerite e atributos de risco da entidade Anomaly."""
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
        explanation="Salto de horas extras de 275% em relacao a media movel dos ultimos 3 meses.",
        suggested_action="Reter desembolso de horas extras e auditar espelho de ponto.",
    )
    assert anomaly.paytrust_score == 94.5
    assert anomaly.severity == RiskSeverity.HIGH
    assert anomaly.is_resolved is False
