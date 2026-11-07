"""Caso de uso para processamento de atestados, aplicacao de regras CLT/INSS e deteccao de conflitos."""

from typing import Protocol

from app.application.dtos.absence_dto import (
    MedicalCertificateUploadDTO,
    ProcessAbsenceResultDTO,
)
from app.domain.repositories.interfaces import AbsenceRepository, EmployeeRepository


class MedicalCertificateOcrService(Protocol):
    """Protocolo definindo o servico de OCR e extracao visual de campos em atestados medicos."""

    def extract_certificate_data(self, file_url: str) -> dict:
        """Extrai dados estruturados (medico, CRM, CID, periodo de repouso) da imagem ou PDF."""
        ...


class ProcessAbsenceUseCase:
    """Orquestra a validacao e o direcionamento legal de afastamentos e licencas.

    Cenarios Cobertos:
        - Caso 1 (Atestado simples ate 15 dias): Integralmente pago pela empresa (CLT Art. 476).
        - Caso 2 (Atestado longo acima de 15 dias): Divisao automatica: 15 dias pela empresa e
          excedente encaminhado ao INSS com instrucao de pericia.
        - Caso 3 (Documento ilegivel): Recusa imediata solicitando reenvio de foto legivel.
        - Caso 4 (Sobreposicao de ferias): Deteccao de conflito entre atestado e periodo de ferias.
    """

    def __init__(
        self,
        ocr_service: MedicalCertificateOcrService,
        absence_repository: AbsenceRepository,
        employee_repository: EmployeeRepository,
    ) -> None:
        """Inicializa o caso de uso com suas dependencias de infraestrutura e persistencia.

        Argumentos:
            ocr_service: Adaptador para OCR Vision e parsing de atestados.
            absence_repository: Repositorio para persistencia e consulta de afastamentos.
            employee_repository: Repositorio para consulta de dados funcionais do colaborador.
        """
        self.ocr_service = ocr_service
        self.absence_repository = absence_repository
        self.employee_repository = employee_repository

    def execute(self, request: MedicalCertificateUploadDTO) -> ProcessAbsenceResultDTO:
        """Processa o documento de atestado medico submetido.

        Argumentos:
            request: Detalhes do atestado enviado e identificacao do colaborador.

        Retorna:
            ProcessAbsenceResultDTO: Legibilidade, divisao de dias empresa vs. INSS e alertas de choque.
        """
        raise NotImplementedError(
            "ProcessAbsenceUseCase.execute e um stub de interface estrutural."
        )
