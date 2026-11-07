"""Entidades de dominio para pesquisas pulso curtas, escuta anonima e devolutivas."""

from dataclasses import dataclass, field
from datetime import date
from enum import Enum


class SurveyType(str, Enum):
    """Classificacao da pesquisa pulso aplicada aos colaboradores."""

    CHECKIN_MENSAL = "CHECKIN_MENSAL"  # Escuta curta recorrente de 3 perguntas
    DIRECIONADA_AREA = "DIRECIONADA_AREA"  # Disparada pontualmente quando um sinal acende na area


@dataclass
class SurveyQuestion:
    """Questao de pesquisa pulso focada em percepcao de carga, lideranca ou suporte."""

    id: str
    text: str
    dimension: str  # Ex.: CARGA_TRABALHO, CLAREZA, RELACIONAMENTO


@dataclass
class SurveySummary:
    """Resultado agregado e anonimizado de uma pesquisa pulso por area.

    Diretrizes de Protecao:
        - Nunca armazena respostas vinculadas ao nome ou identificador do colaborador.
        - Comentarios abertos sao sumarizados por tema sem identificacao de autoria.
        - Se identificar indicio de sofrimento grave ou assedio, dispara alerta de ajuda.

    Atributos:
        id: Identificador unico da sintese da pesquisa.
        area_id: Identificador da area participante.
        survey_type: Tipo de escuta (mensal ou direcionada).
        competence_period: Mes de aplicacao.
        respondents_count: Quantidade de pessoas que responderam.
        participation_rate: Percentual de adesao do time (%).
        average_score: Nota media geral obtida (escala 1.0 a 5.0).
        workload_score: Nota especifica atribuida a dimensao de carga de trabalho.
        summarized_themes: Sintese dos principais temas apontados nos comentarios livres.
        urgent_help_flags_count: Ocorrencias direcionadas para canal de apoio ou acolhimento.
    """

    id: str
    area_id: str
    survey_type: SurveyType
    competence_period: date
    respondents_count: int
    participation_rate: float
    average_score: float
    workload_score: float
    summarized_themes: list[str] = field(default_factory=list)
    urgent_help_flags_count: int = 0


@dataclass
class TeamDevolutivaMessage:
    """Mensagem de devolutiva ('Voce falou, a empresa fez') gerada pelo Pulso para o time.

    Atributos:
        id: Identificador da devolutiva.
        area_id: Area destinataria do comunicado.
        risk_card_id: Card de atencao que motivou a intervencao do RH.
        summary_of_listening: Resumo do que a equipe apontou nas pesquisas e sinais.
        approved_action_plan: Explicacao em linguagem acessivel do que a empresa vai mudar.
        publication_date: Data de envio aos colaboradores via chat corporativo.
    """

    id: str
    area_id: str
    risk_card_id: str
    summary_of_listening: str
    approved_action_plan: str
    publication_date: date | None = None
