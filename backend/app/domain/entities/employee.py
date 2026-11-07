"""Entidade de dominio representando um colaborador da empresa."""

from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class Employee:
    """Representa um colaborador da organizacao para auditoria de folha e afastamentos.

    Atributos:
        id: Identificador unico do colaborador.
        registration_number: Matricula funcional na organizacao.
        name: Nome completo do colaborador.
        department: Departamento ou setor de atuacao.
        role: Cargo ocupado atualmente.
        base_salary: Salario base mensal contratual em Reais (BRL).
        hire_date: Data de admissao.
        is_active: Indicador se o contrato de trabalho esta ativo.
        manager_id: Identificador do gestor imediato.
    """

    id: str
    registration_number: str
    name: str
    department: str
    role: str
    base_salary: float
    hire_date: date
    is_active: bool = True
    manager_id: Optional[str] = None
