"""Use case for processing medical certificates, applying CLT/INSS rules, and detecting conflicts."""

from typing import Protocol

from app.application.dtos.absence_dto import (
    MedicalCertificateUploadDTO,
    ProcessAbsenceResultDTO,
)
from app.domain.repositories.interfaces import AbsenceRepository, EmployeeRepository


class MedicalCertificateOcrService(Protocol):
    """Protocol for OCR and document vision extraction service."""

    def extract_certificate_data(self, file_url: str) -> dict:
        """Extract structured fields (doctor name, CRM, CID, duration, date) from certificate image."""
        ...


class ProcessAbsenceUseCase:
    """Orchestrates validation and statutory splitting of employee leaves.

    Business Rules:
        - Case 1 (Simple Sick Leave <= 15 days): 100% paid by company under CLT Art. 476.
        - Case 2 (Long Leave > 15 days): First 15 days paid by company; subsequent days routed to INSS.
        - Case 3 (Illegible Document): Immediate refusal requesting clear resubmission.
        - Case 4 (Vacation Overlap): Detect conflicts between sick leave and scheduled vacations.
    """

    def __init__(
        self,
        ocr_service: MedicalCertificateOcrService,
        absence_repository: AbsenceRepository,
        employee_repository: EmployeeRepository,
    ) -> None:
        """Initialize the use case with dependencies.

        Args:
            ocr_service: Adapter for document parsing and OCR vision extraction.
            absence_repository: Persistence gateway for absences.
            employee_repository: Access gateway for employee profile and schedule data.
        """
        self.ocr_service = ocr_service
        self.absence_repository = absence_repository
        self.employee_repository = employee_repository

    def execute(self, request: MedicalCertificateUploadDTO) -> ProcessAbsenceResultDTO:
        """Process an uploaded medical certificate document.

        Args:
            request: The uploaded certificate details.

        Returns:
            ProcessAbsenceResultDTO: Document validity, company vs INSS day distribution,
                and conflict alerts.
        """
        raise NotImplementedError("ProcessAbsenceUseCase.execute is a structural interface stub.")
