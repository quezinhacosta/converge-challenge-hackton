"""Data transfer objects for absence processing and medical certificate validation."""

from datetime import date
from typing import Optional
from pydantic import BaseModel, Field


class MedicalCertificateUploadDTO(BaseModel):
    """Payload representing a medical certificate submitted for OCR extraction and compliance check.

    Attributes:
        employee_id: Identifier of the employee uploading the document.
        file_url: URL or path to the certificate image or PDF.
        submission_date: Date the certificate was submitted.
    """

    employee_id: str
    file_url: str
    submission_date: date = Field(default_factory=date.today)


class ProcessAbsenceResultDTO(BaseModel):
    """Response DTO with the result of parsing and legal split calculation.

    Attributes:
        absence_id: Generated absence identifier.
        employee_id: Associated employee identifier.
        is_legible: Flag indicating if OCR successfully extracted key certificate fields.
        total_days_granted: Total duration extracted from document.
        company_paid_days: Portion falling under 15-day employer responsibility (CLT).
        inss_paid_days: Days exceeding 15 that must be referred to INSS.
        requires_inss_scheduling: True if employee must attend an INSS medical evaluation.
        has_vacation_conflict: Flag indicating conflict with pre-scheduled annual leave.
        compliance_message: Humanized explanation of the decision and legal grounds.
    """

    absence_id: str
    employee_id: str
    is_legible: bool
    total_days_granted: int
    company_paid_days: int
    inss_paid_days: int
    requires_inss_scheduling: bool
    has_vacation_conflict: bool
    compliance_message: str


class SubstitutionCalculationRequestDTO(BaseModel):
    """Payload to compute temporary replacement wage differential under Súmula 159 TST.

    Attributes:
        substitute_employee_id: Employee temporarily assuming higher-level duties.
        replaced_employee_id: Employee currently on medical or statutory leave.
        start_date: Start date of the substitution assignment.
        end_date: End date of the substitution assignment.
    """

    substitute_employee_id: str
    replaced_employee_id: str
    start_date: date
    end_date: date


class SubstitutionCalculationResponseDTO(BaseModel):
    """Result of Súmula 159 TST wage differential computation.

    Attributes:
        is_eligible_sumula_159: True if substitution is non-occasional (não eventual).
        duration_days: Days of effective replacement.
        substitute_base_salary: Base monthly salary of the substitute.
        replaced_base_salary: Base monthly salary of the absent employee.
        proportional_differential_amount: Proportional monetary addition to be added to paystub.
        legal_rationale: Legal explanation citing Súmula 159 do TST for DP audit trail.
    """

    is_eligible_sumula_159: bool
    duration_days: int
    substitute_base_salary: float
    replaced_base_salary: float
    proportional_differential_amount: float
    legal_rationale: str
