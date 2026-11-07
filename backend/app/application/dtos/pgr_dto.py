"""DTOs para o Inventario de Riscos e Plano de Acao do PGR (NR-1).

Os aliases seguem os nomes do modelo PgrInventoryItem do frontend Angular.
"""

from datetime import date, datetime

from app.application.dtos.compat import ApiModel, Field


class PgrInventoryItemDTO(ApiModel):
    """Representacao formal de um item no inventario de riscos ocupacionais do PGR."""

    item_id: str
    area_id: str
    area_name: str
    fator_psicossocial: str = Field(alias="factor")
    nivel_severidade: str = Field(alias="severityLevel")
    descricao_plano_acao: str = Field(alias="actionPlanDescription")
    responsavel: str = Field(alias="responsiblePerson")
    prazo_limite: date = Field(alias="deadlineDate")
    intervalo_reavaliacao_dias: int = Field(alias="reassessmentIntervalDays")
    data_registro: datetime = Field(alias="registeredAt")
    is_reaberto: bool = Field(alias="isReopened")
    data_encerramento: date | None = Field(default=None, alias="closureDate")
    parecer_encerramento: str | None = Field(default=None, alias="closureNotes")
    rastro_auditoria: list[str] = Field(alias="auditLog")


class ReassessmentEvaluationDTO(ApiModel):
    """Resultado do acompanhamento do ciclo de risco 60 dias apos a acao."""

    item_id: str
    area_id: str
    houve_melhora_indicadores: bool = Field(alias="houveMelhora")
    status_final: str  # 'FECHADO' ou 'REABERTO'
    resumo_evolucao: str = Field(alias="parecer")
    reducao_atestados_pct: float = 0.0
