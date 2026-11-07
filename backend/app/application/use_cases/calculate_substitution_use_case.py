"""Caso de uso para calculo de diferenca salarial por substituicao temporaria (Sumula 159 TST)."""

from app.application.dtos.absence_dto import (
    SubstitutionCalculationRequestDTO,
    SubstitutionCalculationResponseDTO,
)
from app.domain.repositories.interfaces import EmployeeRepository


class CalculateSubstitutionUseCase:
    """Calcula diferencas salariais devidas quando um colaborador assume posto de colega ausente.

    Fundamentacao Juridica (Sumula 159 do TST - Item I):
        "Enquanto perdurar a substituicao que nao tenha cargo vago e nao seja meramente eventual,
        inclusive nas ferias, o empregado substituto fara jus ao salario contratual do substituido."

    Fluxo de Execucao:
        1. Consulta o salario base mensal do colaborador substituto e do colaborador substituido.
        2. Avalia se o periodo de cobertura configura substituicao nao-eventual.
        3. Realiza o calculo da diferenca diaria proporcional: ((Salario_Substituido - Salario_Substituto) / 30) * Dias.
        4. Formula a justificativa legal para inclusao automatica da rubrica no holerite.
    """

    def __init__(self, employee_repository: EmployeeRepository) -> None:
        """Inicializa o caso de uso com o repositorio de colaboradores.

        Argumentos:
            employee_repository: Repositorio para obtencao dos cargos e faixas salariais.
        """
        self.employee_repository = employee_repository

    def execute(
        self, request: SubstitutionCalculationRequestDTO
    ) -> SubstitutionCalculationResponseDTO:
        """Calcula a diferenca salarial proporcional devida ao colaborador substituto.

        Argumentos:
            request: DTO contendo identificadores dos envolvidos e datas da substituicao.

        Retorna:
            SubstitutionCalculationResponseDTO: Valor apurado e embasamento na Sumula 159 do TST.
        """
        raise NotImplementedError(
            "CalculateSubstitutionUseCase.execute e um stub de interface estrutural."
        )
