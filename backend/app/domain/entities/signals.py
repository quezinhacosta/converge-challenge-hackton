"""Entidades de dominio para sinais operacionais agregados e eventos de contexto organizacional."""

from dataclasses import dataclass
from datetime import date
from enum import Enum


class ContextEventType(str, Enum):
    """Categorias de eventos corporativos de contexto que impactam os times."""

    NOVA_META = "NOVA_META"
    TROCA_GESTOR = "TROCA_GESTOR"
    REESTRUTURACAO = "REESTRUTURACAO"
    CONTRATACOES = "CONTRATACOES"
    MUDANCA_SISTEMA = "MUDANCA_SISTEMA"


@dataclass
class ContextEvent:
    """Evento organizacional de contexto associado a uma area e periodo.

    Atributos:
        id: Identificador unico do evento.
        area_id: Area impactada pelo evento.
        event_date: Data de ocorrencia ou implementacao.
        event_type: Categoria do evento de contexto.
        description: Detalhes publicos do evento (ex.: Nova meta de atendimentos/hora implantada em agosto).
    """

    id: str
    area_id: str
    event_date: date
    event_type: ContextEventType
    description: str


@dataclass
class AreaMonthlyMetrics:
    """Metricas agregadas mensais de uma area para monitoramento de sinais de risco a saude mental.

    Diretrizes Estritas de Privacidade (Guardrails LGPD & NR-1):
        - Nunca contem dados individuais (sem nomes, sem matriculas).
        - Nunca le CID, diagnostico ou nome de medico (apenas quantidade e dias de atestados).
        - Nunca le o conteudo ou envolvidos de denuncias (apenas contagem agregada).
        - Nunca le motivos pessoais de faltas nem respostas individuais de pesquisas.

    Atributos:
        id: Identificador do registro mensal.
        area_id: Identificador da area monitorada.
        competence_period: Competencia de referencia (ex.: 2026-10-01).
        certificate_days_count: Total de dias de atestado acumulados pela equipe no mes.
        certificate_cases_count: Quantidade total de atestados entregues no mes.
        unexcused_absences_count: Total de faltas e desfalques operacionais.
        shift_coverages_count: Coberturas de escala realizadas por colegas.
        resignation_requests_count: Pedidos voluntarios de demissao ocorridos no mes.
        turnover_rate: Taxa de turnover calculada para o time no periodo (%).
        overtime_hours_avg: Media de horas extras realizadas por pessoa na area.
        unfulfilled_break_intervals_count: Intervalos intra-jornada nao cumpridos.
        harassment_complaints_count: Contagem de denuncias registradas para o setor no canal de compliance.
        sesmt_long_term_absences_count: Contagem agregada de afastamentos longos por saude (SESMT).
        pulse_survey_workload_score: Nota media de carga de trabalho na pesquisa pulso (escala 1 a 5).
    """

    id: str
    area_id: str
    competence_period: date
    certificate_days_count: int
    certificate_cases_count: int
    unexcused_absences_count: int
    shift_coverages_count: int
    resignation_requests_count: int
    turnover_rate: float
    overtime_hours_avg: float
    unfulfilled_break_intervals_count: int
    harassment_complaints_count: int
    sesmt_long_term_absences_count: int
    pulse_survey_workload_score: float | None = None
