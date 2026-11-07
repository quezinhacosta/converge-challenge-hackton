"""Endpoints para analise de atestados medicos, regras de afastamento e Sumula 159 TST."""

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
    """Recebe atestado medico para leitura OCR e aplicacao da divisao legal de dias (CLT/INSS).

    Parametros:
        payload: Metadados e URL do atestado medico anexado pelo colaborador.

    Retorna:
        ProcessAbsenceResultDTO: Resultado da leitura, reparticao de dias e alertas de conflito.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando implementacao do caso de uso.",
    )


@router.post(
    "/calculate-substitution",
    response_model=SubstitutionCalculationResponseDTO,
    status_code=status.HTTP_200_OK,
)
def calculate_substitution(
    payload: SubstitutionCalculationRequestDTO,
) -> SubstitutionCalculationResponseDTO:
    """Calcula a diferenca salarial sob a Sumula 159 do TST para substituicoes temporarias.

    Parametros:
        payload: Parametros com identificacao do substituto, substituido e periodo.

    Retorna:
        SubstitutionCalculationResponseDTO: Valor apurado e embasamento na legislacao trabalhista.
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Endpoint e um stub estrutural aguardando implementacao do caso de uso.",
    )
