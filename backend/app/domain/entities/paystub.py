"""Entidade de dominio representando lancamentos da folha de pagamento e rubricas."""

from dataclasses import dataclass, field
from datetime import date
from typing import List


@dataclass
class PaystubItem:
    """Item individual ou rubrica do holerite do colaborador.

    Atributos:
        code: Codigo interno da rubrica ou identificador no padrao eSocial.
        description: Descricao da verba (provento ou desconto).
        reference_units: Quantidade de referencia (ex.: horas extras, dias ou percentual).
        amount: Valor monetario correspondente em BRL.
        is_discount: Indica se a rubrica e deducao (ex.: INSS, IRRF, faltas).
    """

    code: str
    description: str
    reference_units: float
    amount: float
    is_discount: bool = False


@dataclass
class Paystub:
    """Representa o holerite mensal de um colaborador para auditoria e explicabilidade.

    Atributos:
        id: Identificador unico do holerite.
        employee_id: Identificador do colaborador associado.
        competence_period: Mes e ano da competencia da folha (ex.: 2026-10-01).
        base_salary: Salario base mensal contratual.
        overtime_hours_current_month: Horas extras totais apuradas no mes corrente.
        overtime_hours_3m_average: Media movel de horas extras dos ultimos 3 meses.
        sector_overtime_standard_deviation: Desvio padrao das horas extras do setor.
        substitution_salary_differential: Diferenca salarial por substituicao (Sumula 159 TST).
        gross_total: Total de proventos brutos antes das deducoes legais.
        net_total: Salario liquido final a receber.
        items: Lista de rubricas detalhadas que compoem o holerite.
    """

    id: str
    employee_id: str
    competence_period: date
    base_salary: float
    overtime_hours_current_month: float
    overtime_hours_3m_average: float
    sector_overtime_standard_deviation: float
    substitution_salary_differential: float
    gross_total: float
    net_total: float
    items: List[PaystubItem] = field(default_factory=list)
