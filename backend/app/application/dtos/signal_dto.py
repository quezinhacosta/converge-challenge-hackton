"""Objetos de Transferencia de Dados (DTOs) para sinais agregados e eventos de contexto."""

from datetime import date
from typing import List, Optional
from app.application.dtos.compat import BaseModel, Field


class AreaMetricsDTO(BaseModel):
    """Metricas operacionais agregadas de um setor em uma competencia.

    Atributos:
        area_id: Identificador da area.
        area_name: Nome do setor.
        competence_period: Data de competencia (YYYY-MM-DD).
        dias_atestado: Total de dias de afastamento somados no mes.
        casos_atestado: Quantidade de atestados medicos entregues.
        faltas_desfalques: Total de faltas e desfalques de escala.
        horas_extras_media: Media de horas extras por pessoa.
        turnover_pedidos_demissao: Quantidade de pedidos voluntarios de demissao.
        denuncias_contagem: Total de registros no canal de compliance.
        nota_pesquisa_pulso: Nota media de carga de trabalho (1 a 5).
    """

    area_id: str
    area_name: str
    competence_period: date
    dias_atestado: int = Field(ge=0)
    casos_atestado: int = Field(ge=0)
    faltas_desfalques: int = Field(ge=0)
    horas_extras_media: float = Field(ge=0.0)
    turnover_pedidos_demissao: int = Field(ge=0)
    denuncias_contagem: int = Field(ge=0)
    nota_pesquisa_pulso: Optional[float] = None


class AreaHistoryComparisonDTO(BaseModel):
    """Comparativo entre os indicadores recentes da area e a media corporativa."""

    area_id: str
    area_name: str
    headcount: int
    is_anonymized: bool
    variacao_dias_atestado_pct: float
    variacao_horas_extras_pct: float
    pedidos_demissao_periodo: int
    media_empresa_pedidos_demissao: float
    nota_carga_trabalho_atual: Optional[float]
    nota_carga_trabalho_anterior: Optional[float]
    eventos_contexto_recentes: List[str]
