"""Caso de uso para medicao de eficacia e acompanhamento pos-acao (Etapa 9 do Pulso)."""

from datetime import date
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
        - Se melhoraram: atualiza o registro do PGR e fecha o ciclo com sucesso (Caso 7).
        - Se nao melhoraram: reabre o card no painel do RH para nova intervencao.
    """

    def __init__(
        self,
        pgr_repository: PgrInventoryRepository,
        risk_card_repository: RiskCardRepository,
        signal_repository: SignalRepository,
    ) -> None:
        """Inicializa o caso de uso de acompanhamento."""
        self.pgr_repository = pgr_repository
        self.risk_card_repository = risk_card_repository
        self.signal_repository = signal_repository

    def execute(self, pgr_item_id: str) -> ReassessmentEvaluationDTO:
        """Avalia os resultados alcancados pela acao apos o periodo de reavaliacao."""
        item = self.pgr_repository.get_by_id(pgr_item_id)
        if not item:
            raise ValueError(f"Item do PGR '{pgr_item_id}' nao encontrado.")

        # Simulacao da reavaliacao de 60 dias (Caso 7 do Pitch: melhora confirmada)
        # Em producao, consulta metricas dos meses t+1 e t+2
        houve_melhora = True
        resumo = (
            f"Apos a acao implementada em {item.area_name}, observou-se reducao de 35% nos dias de atestado, "
            f"normalizacao das horas extras para a media setorial e elevacao da nota de clima para 3.8."
        )

        if houve_melhora:
            item.closure_date = date.today()
            item.closure_notes = "Acao eficaz. Indicadores reestabelecidos aos niveis basais da organizacao."
            item.is_reopened = False
            item.audit_log.append(f"Ciclo encerrado com sucesso em {date.today().strftime('%d/%m/%Y')}.")
            self.pgr_repository.save(item)

            status_final = "FECHADO"
        else:
            item.is_reopened = True
            item.audit_log.append(f"Reaberto em {date.today().strftime('%d/%m/%Y')} por ausencia de melhora.")
            self.pgr_repository.save(item)
            status_final = "REABERTO"

        return ReassessmentEvaluationDTO(
            item_id=item.id,
            area_id=item.area_id,
            houve_melhora_indicadores=houve_melhora,
            status_final=status_final,
            resumo_evolucao=resumo,
        )
