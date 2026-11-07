"""Caso de uso para deliberacao humana do RH e registro no PGR da NR-1 (Etapa 8 do Pulso)."""

from typing import Protocol
from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO
from app.domain.repositories.interfaces import (
    PgrInventoryRepository,
    RiskCardRepository,
    SurveyRepository,
)


class DevolutivaDraftingService(Protocol):
    """Protocolo para redacao da devolutiva de escuta ('Voce falou, a empresa fez')."""

    def generate_devolutiva_text(
        self, area_name: str, action_description: str
    ) -> str:
        """Redige o comunicado transparente para a equipe informando a mudanca acordada."""
        ...


class RegisterPgrActionUseCase:
    """Executa a Etapa 8 do Ciclo do Pulso:

    Etapa 8 - Registrar (Apos Aprovacao Humana):
        Apos a aprovacao ou ajuste pelo analista de RH, inclui formalmente o risco
        no inventario do PGR e estabelece o plano de acao com responsavel e prazo.
        Opcionalmente, redige o comunicado de devolutiva para o time.
    """

    def __init__(
        self,
        risk_card_repository: RiskCardRepository,
        pgr_repository: PgrInventoryRepository,
        survey_repository: SurveyRepository,
        devolutiva_service: DevolutivaDraftingService,
    ) -> None:
        """Inicializa o caso de uso.

        Argumentos:
            risk_card_repository: Repositorio de cards para atualizar status.
            pgr_repository: Repositorio do inventario formal do PGR.
            survey_repository: Repositorio para gravar a devolutiva a equipe.
            devolutiva_service: Servico de redacao do comunicado de devolutiva.
        """
        self.risk_card_repository = risk_card_repository
        self.pgr_repository = pgr_repository
        self.survey_repository = survey_repository
        self.devolutiva_service = devolutiva_service

    def execute(self, card_id: str, request: ResolveRiskCardRequestDTO) -> PgrInventoryItemDTO:
        """Efetiva a decisao do RH, atualiza o card e registra no PGR da empresa.

        Argumentos:
            card_id: Identificador do card sob analise.
            request: Payload com a decisao (Aprovar, Ajustar ou Descartar), responsavel e prazo.

        Retorna:
            PgrInventoryItemDTO: Item documentado no inventario de riscos ocupacionais do PGR.
        """
        raise NotImplementedError(
            "RegisterPgrActionUseCase.execute e um stub de interface estrutural."
        )
