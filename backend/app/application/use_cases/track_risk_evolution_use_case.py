"""Caso de uso para medicao de eficacia e acompanhamento pos-acao (Etapa 9 do Pulso)."""

from app.application.dtos.pgr_dto import ReassessmentEvaluationDTO
from app.domain.repositories.interfaces import (
    PgrInventoryRepository,
    RiskCardRepository,
    SignalRepository,
)


class TrackRiskEvolutionUseCase:
    """Executa a Etapa 9 do Ciclo do Pulso:

    Etapa 9 - Acompanhar:
        Nos meses seguintes a implementacao da acao (ex.: 60 dias), reavalia os indicadores
        da area para medir se houve melhora efetiva.
        - Se melhoraram: atualiza o registro do PGR e fecha o ciclo com sucesso.
        - Se nao melhoraram: reabre o card no painel do RH para nova intervencao.
    """

    def __init__(
        self,
        pgr_repository: PgrInventoryRepository,
        risk_card_repository: RiskCardRepository,
        signal_repository: SignalRepository,
    ) -> None:
        """Inicializa o caso de uso de acompanhamento.

        Argumentos:
            pgr_repository: Repositorio do inventario do PGR.
            risk_card_repository: Repositorio de cards para eventual reabertura.
            signal_repository: Repositorio de sinais para checar a evolucao pos-intervencao.
        """
        self.pgr_repository = pgr_repository
        self.risk_card_repository = risk_card_repository
        self.signal_repository = signal_repository

    def execute(self, pgr_item_id: str) -> ReassessmentEvaluationDTO:
        """Avalia os resultados alcancados pela acao apos o periodo de reavaliacao.

        Argumentos:
            pgr_item_id: Identificador do registro do PGR em monitoramento.

        Retorna:
            ReassessmentEvaluationDTO: Parecer de encerramento do ciclo ou reabertura do caso.
        """
        raise NotImplementedError(
            "TrackRiskEvolutionUseCase.execute e um stub de interface estrutural."
        )
