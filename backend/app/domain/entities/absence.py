"""Entidade de dominio representando afastamentos medicos, licencas e regras do INSS."""

from dataclasses import dataclass
from datetime import date
from enum import Enum
from typing import Optional


class AbsenceType(str, Enum):
    """Classificacao do tipo de ausencia do colaborador."""

    MEDICAL = "MEDICAL"
    MATERNITY = "MATERNITY"
    BEREAVEMENT = "BEREAVEMENT"
    VACATION = "VACATION"
    UNEXCUSED = "UNEXCUSED"


class AbsenceStatus(str, Enum):
    """Estado de processamento e encaminhamento do afastamento."""

    PENDING_VALIDATION = "PENDING_VALIDATION"
    APPROVED_COMPANY = "APPROVED_COMPANY"
    FORWARDED_TO_INSS = "FORWARDED_TO_INSS"
    REJECTED = "REJECTED"


@dataclass
class Absence:
    """Representa um afastamento medico ou licenca trabalhista.

    Regras de Negocio:
        - CLT Art. 476: Os primeiros 15 dias consecutivos de incapacidade sao pagos
          diretamente pelo empregador.
        - Os dias que excederem o 15º dia transferem o encargo financeiro para a Previdencia Social (INSS).
        - Valida sobreposicoes com periodos de ferias agendadas ou atestados duplicados.

    Atributos:
        id: Identificador unico do evento de afastamento.
        employee_id: Identificador do colaborador afastado.
        absence_type: Tipo de afastamento (ex.: medico, ferias).
        start_date: Data de inicio do afastamento.
        end_date: Data final do periodo de afastamento.
        duration_days: Duracao total em dias indicada no atestado.
        company_paid_days: Quantidade de dias sob responsabilidade da empresa (maximo 15).
        inss_paid_days: Quantidade de dias encaminhados ao INSS (apos o 15º dia).
        status: Estado atual de validacao e encaminhamento.
        icd_code: Codigo de Classificacao Internacional de Doencas (CID), quando disponivel.
        document_url: URL ou caminho do comprovante ou atestado anexado.
        requires_inss_scheduling: Indica se o colaborador deve agendar pericia presencial no INSS.
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
