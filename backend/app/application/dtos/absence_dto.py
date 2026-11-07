"""Objetos de transferencia de dados para processamento de afastamentos e atestados."""

from datetime import date
from pydantic import BaseModel, Field


class MedicalCertificateUploadDTO(BaseModel):
    """Payload representando o envio de um atestado para extracao OCR e validacao trabalhista.

    Atributos:
        employee_id: Identificador do colaborador que enviou o atestado.
        file_url: URL ou caminho para a imagem ou documento PDF do atestado.
        submission_date: Data do envio do documento.
    """

    employee_id: str
    file_url: str
    submission_date: date = Field(default_factory=date.today)


class ProcessAbsenceResultDTO(BaseModel):
    """DTO de resposta contendo o resultado da extracao OCR e a divisao legal da responsabilidade.

    Atributos:
        absence_id: Identificador do registro de afastamento gerado.
        employee_id: Identificador do colaborador correspondente.
        is_legible: Indicador se o OCR conseguiu ler e extrair os campos fundamentais com confianca.
        total_days_granted: Duracao total concedida no atestado.
        company_paid_days: Dias sob responsabilidade de pagamento da empresa (teto de 15 dias CLT).
        inss_paid_days: Dias que excedem o 15º dia e devem ser custeados pela Previdencia Social.
        requires_inss_scheduling: Indica se ha necessidade de agendar pericia medica junto ao INSS.
        has_vacation_conflict: Indicador de sobreposicao com ferias previamente cadastradas.
        compliance_message: Justificativa humanizada com embasamento nas regras da CLT.
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
    """Payload para calculo de diferenca salarial por substituicao sob a Sumula 159 do TST.

    Atributos:
        substitute_employee_id: Colaborador substituto que assume a funcao temporaria.
        replaced_employee_id: Colaborador substituido que esta temporariamente afastado.
        start_date: Data inicial da substituicao.
        end_date: Data final da substituicao.
    """

    substitute_employee_id: str
    replaced_employee_id: str
    start_date: date
    end_date: date


class SubstitutionCalculationResponseDTO(BaseModel):
    """Resultado do calculo de diferenca salarial fundamentado na Sumula 159 do TST.

    Atributos:
        is_eligible_sumula_159: Indica se a substituicao possui carater nao-eventual.
        duration_days: Total de dias corridos em que durou a substituicao.
        substitute_base_salary: Salario base mensal do colaborador substituto.
        replaced_base_salary: Salario base mensal do colaborador substituido.
        proportional_differential_amount: Valor monetario proporcional a ser acrescido na folha.
        legal_rationale: Fundamentacao juridica referenciando a Sumula 159 do TST para auditoria.
    """

    is_eligible_sumula_159: bool
    duration_days: int
    substitute_base_salary: float
    replaced_base_salary: float
    proportional_differential_amount: float
    legal_rationale: str
