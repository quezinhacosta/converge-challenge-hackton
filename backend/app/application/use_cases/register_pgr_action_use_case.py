"""Caso de uso para deliberacao humana do RH e registro no PGR da NR-1 (Etapa 8 do Pulso)."""

from datetime import UTC, date, datetime, timedelta
from typing import Protocol

from app.application.dtos.pgr_dto import PgrInventoryItemDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO
from app.domain.entities.pgr_inventory import PgrRiskItem
from app.domain.entities.risk_card import CardStatus
from app.domain.entities.survey import TeamDevolutivaMessage
from app.domain.repositories.interfaces import (
    PgrInventoryRepository,
    RiskCardRepository,
    SurveyRepository,
)


class DevolutivaDraftingService(Protocol):
    """Protocolo para redacao da devolutiva de escuta ('Voce falou, a empresa fez')."""

    def generate_devolutiva_text(self, area_name: str, action_description: str) -> str:
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
        """Inicializa o caso de uso."""
        self.risk_card_repository = risk_card_repository
        self.pgr_repository = pgr_repository
        self.survey_repository = survey_repository
        self.devolutiva_service = devolutiva_service

    def execute(self, card_id: str, request: ResolveRiskCardRequestDTO) -> PgrInventoryItemDTO:
        """Efetiva a decisao do RH, atualiza o card e registra no PGR da empresa."""
        card = self.risk_card_repository.get_by_id(card_id)
        if not card:
            raise ValueError(f"Card com ID '{card_id}' nao encontrado.")

        # Tratamento da decisao
        if request.action_type == "DESCARTAR":
            card.status = CardStatus.DESCARTADO
            card.reviewer_name = request.reviewer_name
            card.resolution_notes = request.justification_notes or "Descartado pelo RH."
            card.resolved_at = datetime.now(UTC)
            self.risk_card_repository.save(card)

            # Retorna item simbolico arquivado
            return PgrInventoryItemDTO(
                item_id=f"pgr_dismissed_{card.id}",
                area_id=card.area_id,
                area_name=card.area_name,
                fator_psicossocial=card.probable_risk_factor.value,
                nivel_severidade=card.risk_level.value,
                descricao_plano_acao=f"Descartado pelo RH: {card.resolution_notes}",
                responsavel=request.reviewer_name,
                prazo_limite=date.today(),
                intervalo_reavaliacao_dias=0,
                data_registro=datetime.now(UTC),
                is_reaberto=False,
                data_encerramento=date.today(),
                parecer_encerramento="Descartado na triagem inicial do RH.",
                rastro_auditoria=[
                    f"Descartado por {request.reviewer_name} em {datetime.now().isoformat()}"
                ],
            )

        # APROVAR_PGR ou AJUSTAR_ACAO
        if request.action_type == "AJUSTAR_ACAO" and request.adjusted_action_text:
            card.status = CardStatus.AJUSTADO
            action_text = request.adjusted_action_text
        else:
            card.status = CardStatus.APROVADO_PGR
            action_text = card.suggested_action

        card.reviewer_name = request.reviewer_name
        card.resolved_at = datetime.now(UTC)
        self.risk_card_repository.save(card)

        responsible = request.responsible_person or request.reviewer_name
        deadline = date.today() + timedelta(days=request.deadline_days)

        audit_entry = (
            f"Decisao '{request.action_type}' homologada por {request.reviewer_name} em "
            f"{datetime.now().strftime('%d/%m/%Y %H:%M')}. Card de origem: {card.id}."
        )

        pgr_item = PgrRiskItem(
            id=f"pgr_{card.area_id}_{int(datetime.now().timestamp())}",
            risk_card_id=card.id,
            area_id=card.area_id,
            area_name=card.area_name,
            factor=card.probable_risk_factor,
            severity_level=card.risk_level,
            action_plan_description=action_text,
            responsible_person=responsible,
            deadline_date=deadline,
            reassessment_interval_days=request.deadline_days,
            registered_at=datetime.now(UTC),
            is_reopened=False,
            audit_log=[audit_entry],
        )

        saved_item = self.pgr_repository.save(pgr_item)

        # Emissao da Devolutiva ("Voce falou, a empresa fez")
        devolutiva_text = self.devolutiva_service.generate_devolutiva_text(
            card.area_name, action_text
        )
        devolutiva_msg = TeamDevolutivaMessage(
            id=f"dev_{saved_item.id}",
            area_id=card.area_id,
            risk_card_id=card.id,
            summary_of_listening=card.evidence_summary,
            approved_action_plan=devolutiva_text,
            publication_date=date.today(),
        )
        self.survey_repository.save_devolutiva(devolutiva_msg)

        return PgrInventoryItemDTO(
            item_id=saved_item.id,
            area_id=saved_item.area_id,
            area_name=saved_item.area_name,
            fator_psicossocial=saved_item.factor.value,
            nivel_severidade=saved_item.severity_level.value,
            descricao_plano_acao=saved_item.action_plan_description,
            responsavel=saved_item.responsible_person,
            prazo_limite=saved_item.deadline_date,
            intervalo_reavaliacao_dias=saved_item.reassessment_interval_days,
            data_registro=saved_item.registered_at,
            is_reaberto=saved_item.is_reopened,
            data_encerramento=saved_item.closure_date,
            parecer_encerramento=saved_item.closure_notes,
            rastro_auditoria=saved_item.audit_log,
        )
