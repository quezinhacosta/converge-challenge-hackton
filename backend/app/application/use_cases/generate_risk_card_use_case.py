"""Caso de uso para redigir o Ponto Focal de Atencao e escalar para o RH (Etapas 6 e 7 do Pulso)."""

from typing import Protocol
from app.application.dtos.risk_card_dto import RiskCardDTO
from app.domain.entities.risk_card import RiskCard
from app.domain.repositories.interfaces import AreaRepository, RiskCardRepository


class CardContentGenerator(Protocol):
    """Protocolo da LLM encarregada de redigir o card em linguagem clara e direta."""

    def draft_focus_card(
        self,
        area_name: str,
        headcount: int,
        metrics_summary: str,
        context_summary: str,
        factor: str,
    ) -> tuple[str, str]:
        """Escreve a hipotese explicativa e a proposta de acao sugerida ao RH."""
        ...


class GenerateRiskCardUseCase:
    """Executa as Etapas 6 e 7 do Ciclo do Pulso:

    Etapa 6 - Gerar o Ponto Focal:
        Escreve o card de atencao em linguagem simples, compilando evidencias quantitativas,
        contexto organizacional, hipotese de fator de risco e proposta de acao.
    Etapa 7 - Escalar e Parar:
        Envia o card ao painel do RH responsavel e interrompe a automacao.
        Nada e registrado como decisao formal sem aprovacao previa humana.
    """

    def __init__(
        self,
        area_repository: AreaRepository,
        risk_card_repository: RiskCardRepository,
        content_generator: CardContentGenerator,
    ) -> None:
        """Inicializa o caso de uso.

        Argumentos:
            area_repository: Repositorio de consulta a area.
            risk_card_repository: Repositorio de armazenamento de cards.
            content_generator: Gerador textual com base em LLM.
        """
        self.area_repository = area_repository
        self.risk_card_repository = risk_card_repository
        self.content_generator = content_generator

    def execute(self, area_id: str, analysis_result: dict) -> RiskCardDTO:
        """Gera o ponto focal e disponibiliza para apreciacao do RH.

        Argumentos:
            area_id: Identificador da area.
            analysis_result: Resultado das etapas de comparacao e classificacao.

        Retorna:
            RiskCardDTO: Card estruturado aguardando deliberacao humana.
        """
        raise NotImplementedError(
            "GenerateRiskCardUseCase.execute e um stub de interface estrutural."
        )
