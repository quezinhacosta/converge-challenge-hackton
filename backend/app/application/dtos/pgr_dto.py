"""DTOs para o Inventario de Riscos e Plano de Acao do PGR (NR-1)."""

from datetime import date, datetime

from app.application.dtos.compat import BaseModel


class PgrInventoryItemDTO(BaseModel):
    """Representacao formal de um item no inventario de riscos ocupacionais do PGR."""

    item_id: str
    area_id: str
    area_name: str
    fator_psicossocial: str
    nivel_severidade: str
    descricao_plano_acao: str
    responsavel: str
    prazo_limite: date
    intervalo_reavaliacao_dias: int
    data_registro: datetime
    is_reaberto: bool
    data_encerramento: date | None
    parecer_encerramento: str | None
    rastro_auditoria: list[str]


class ReassessmentEvaluationDTO(BaseModel):
    """Resultado do acompanhamento do ciclo de risco 60 dias apos a acao."""

    item_id: str
    area_id: str
    houve_melhora_indicadores: bool
    status_final: str  # 'FECHADO' ou 'REABERTO'
    resumo_evolucao: str
