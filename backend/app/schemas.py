"""Contratos de dados e schemas Pydantic do Pulso (vitAI) para integracao backend.

Define os modelos de dados trocados entre a camada de dados/regras (Pessoa A),
o frontend Angular e as integracoes de canais e agentes externos como Slack Bot e MCP (Pessoa B).
"""

from typing import Any, Dict, List, Optional
from app.application.dtos.compat import BaseModel, Field


class AreaData(BaseModel):
    """Dados agregados e operacionais de uma area corporativa."""

    area_id: str
    area_name: str
    headcount: int
    manager_name: str
    variacao_dias_atestado_pct: float
    variacao_horas_extras_pct: float
    pedidos_demissao_periodo: int
    media_empresa_pedidos_demissao: float
    nota_clima_atual: float
    nota_clima_anterior: float
    eventos_contexto: List[str] = Field(default_factory=list)
    is_blocked_privacy: bool = False
    status_privacidade: str = "ELIGIBLE"


class CasoRiskCard(BaseModel):
    """Estrutura analitica e juridica completa de um Card de Risco Psicossocial (NR-1)."""

    caso_id: str
    area_id: str
    area_name: str
    headcount: int
    score_risco: float
    nivel_risco: str
    fator_nr1: str
    pesos_explicabilidade: Dict[str, float] = Field(default_factory=dict)
    narrativa_explicabilidade: Optional[str] = None
    hipotese_contexto: str
    medida_nr1_sugerida: str
    artigo_nr1: Optional[str] = None
    responsavel_sugerido: Optional[str] = None
    prazo_dias_sugerido: Optional[int] = 60
    comunicacao_time: Optional[str] = None
    perguntas_escuta_gestor: Optional[List[str]] = Field(default_factory=list)
    status: str = "ABERTO"
    fontes: List[str] = Field(default_factory=list)
    data_geracao: Optional[str] = None
    decisao_rh: Optional[Dict[str, Any]] = None


class DecisaoRequest(BaseModel):
    """Payload de deliberacao humana do RH/SESMT para acoes do PGR (NR-1)."""

    acao: str
    revisor_nome: str = "RH / SESMT"
    acao_ajustada_texto: Optional[str] = None
    justificativa: Optional[str] = None
    prazo_dias: int = 60


class DecisaoResponse(BaseModel):
    """Resposta com status da deliberacao e registro formal no GRO/PGR."""

    caso_id: str
    status_anterior: str
    novo_status: str
    registrado_no_pgr: bool
    mensagem: str
    protocolo_gro: str


class ChatQueryRequest(BaseModel):
    """Payload de requisicao para consulta ao copiloto vitAI no chat corporativo."""

    pergunta: str
    user_id: Optional[str] = "rh_user"
    context_filter_area: Optional[str] = None


class ChatQueryResponse(BaseModel):
    """Resposta estruturada do chat com avaliacao de guardrails de privacidade e LGPD."""

    resposta: str
    recusado_lgpd: bool = False
    motivo_recusa: Optional[str] = None
    areas_citadas: List[str] = Field(default_factory=list)
    fontes_consultadas: List[str] = Field(default_factory=list)


class FechamentoSummaryResponse(BaseModel):
    """Sumario executivo da esteira de fechamento mensal dos riscos psicossociais."""

    total_areas: int
    areas_elegiveis: int
    areas_bloqueadas: int
    casos_gerados: List[CasoRiskCard] = Field(default_factory=list)
    mensagem: str
