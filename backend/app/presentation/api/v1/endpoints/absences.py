"""Absence processing, OCR validation, and Súmula 159 substitution endpoints."""

from fastapi import APIRouter, HTTPException, status

from app.application.dtos.absence_dto import (
    MedicalCertificateUploadDTO,
    ProcessAbsenceResultDTO,
    SubstitutionCalculationRequestDTO,
    SubstitutionCalculationResponseDTO,
)

router = APIRouter()


@router.post(
    "/process-certificate",
    response_model=ProcessAbsenceResultDTO,
    status_code=status.HTTP_200_OK,
)
def process_medical_certificate(
    payload: MedicalCertificateUploadDTO,
) -> ProcessAbsenceResultDTO:
    """Submit a medical certificate for OCR parsing and CLT/INSS statutory split.

    Parameters:
        payload: Metadata and document URL of the uploaded doctor note.

    Returns:
        ProcessAbsenceResultDTO: Document validity, company vs INSS breakdown, and conflict alerts.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint is a structural stub pending application use case binding.",
    )


@router.post(
    "/calculate-substitution",
    response_model=SubstitutionCalculationResponseDTO,
    status_code=status.HTTP_200_OK,
)
def calculate_substitution(
    payload: SubstitutionCalculationRequestDTO,
) -> SubstitutionCalculationResponseDTO:
    """Calculate the wage differential under Súmula 159 do TST for non-occasional replacements.

    Parameters:
        payload: Parameters defining substitute employee, replaced employee, and dates.

    Returns:
        SubstitutionCalculationResponseDTO: Wage difference calculation and legal basis.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint is a structural stub pending application use case binding.",
    )
