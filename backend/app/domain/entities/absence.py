"""Domain entity representing leaves, medical absences, and INSS split rules."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class AbsenceType(str, Enum):
    """Categorization of employee absence."""

    MEDICAL = "MEDICAL"
    MATERNITY = "MATERNITY"
    BEREAVEMENT = "BEREAVEMENT"
    VACATION = "VACATION"
    UNEXCUSED = "UNEXCUSED"


class AbsenceStatus(str, Enum):
    """Current processing status of the absence request."""

    PENDING_VALIDATION = "PENDING_VALIDATION"
    APPROVED_COMPANY = "APPROVED_COMPANY"
    FORWARDED_TO_INSS = "FORWARDED_TO_INSS"
    REJECTED = "REJECTED"


@dataclass
class Absence:
    """Represents a medical or statutory absence episode.

    Business Rules:
        - Brazilian Labor Law (CLT Art. 476): First 15 consecutive days of illness
          are paid directly by the employer.
        - Days exceeding the 15-day threshold transfer payment responsibility to INSS.
        - Checks for overlapping pre-scheduled vacations or duplicate medical certificates.

    Attributes:
        id: Unique absence event identifier.
        employee_id: Identifier of the absent employee.
        absence_type: Categorization of absence (e.g., medical, vacation).
        start_date: Initial date of the leave period.
        end_date: Final date of the leave period.
        duration_days: Total number of days granted in the medical certificate.
        company_paid_days: Portion of days funded by the employer (capped at 15 for illness).
        inss_paid_days: Portion of days directed to Social Security (INSS) after day 15.
        status: Current validation and routing status.
        icd_code: International Classification of Diseases code (optional/confidential).
        document_url: Remote storage URL for the uploaded medical certificate image or PDF.
        requires_inss_scheduling: Indicates whether the employee must schedule an INSS medical exam.
    """

    id: str
    employee_id: str
    absence_type: AbsenceType
    start_date: date
    end_date: date
    duration_days: int
    company_paid_days: int
    inss_paid_days: int
    status: AbsenceStatus
    icd_code: Optional[str] = None
    document_url: Optional[str] = None
    requires_inss_scheduling: bool = False
