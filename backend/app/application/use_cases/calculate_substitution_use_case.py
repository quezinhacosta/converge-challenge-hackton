"""Use case for calculating wage differential for temporary substitutions under Súmula 159 TST."""

from app.application.dtos.absence_dto import (
    SubstitutionCalculationRequestDTO,
    SubstitutionCalculationResponseDTO,
)
from app.domain.repositories.interfaces import EmployeeRepository


class CalculateSubstitutionUseCase:
    """Calculates wage differences when an employee assumes duties of an absent colleague.

    Legal Context (Súmula 159 do TST - Item I):
        "Enquanto perdurar a substituição que não tenha cargo vago e não seja meramente eventual,
        inclusive nas férias, o empregado substituto fará jus ao salário contratual do substituído."

    Workflow:
        1. Fetch base compensation of both substitute and substituted employees.
        2. Validate if the duration exceeds the threshold of "eventual" (e.g., > 10-15 days).
        3. Calculate proportional daily differential: ((Salary_Substituted - Salary_Substitute) / 30) * Days.
        4. Generate legal rationale for automatic paystub rubric injection.
    """

    def __init__(self, employee_repository: EmployeeRepository) -> None:
        """Initialize the use case with employee repository.

        Args:
            employee_repository: Data repository for querying employee positions and salaries.
        """
        self.employee_repository = employee_repository

    def execute(
        self, request: SubstitutionCalculationRequestDTO
    ) -> SubstitutionCalculationResponseDTO:
        """Compute the proportional substitution wage differential.

        Args:
            request: DTO containing substitute, substituted, and period parameters.

        Returns:
            SubstitutionCalculationResponseDTO: Calculation result and legal compliance statement.
        """
        raise NotImplementedError(
            "CalculateSubstitutionUseCase.execute is a structural interface stub."
        )
