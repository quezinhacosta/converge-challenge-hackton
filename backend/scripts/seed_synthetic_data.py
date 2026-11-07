"""Script de geracao e populacao de dados sinteticos da empresa ficticia para o Pulso.

Empresa Ficticia:
    - 7 areas corporativas: Atendimento, Logistica, Vendas, Financeiro, Design, Engenharia, RH
    - 154 colaboradores ativos
    - 6 meses de historico operacional (ponto, folha, atestados, desligamentos, pesquisas, eventos)
    - Cobre com precisao cirurgica os 7 casos de demonstracao do pitch.
"""

from datetime import date, datetime, timezone
from typing import Any, Dict, List

from app.domain.entities.area import Area
from app.domain.entities.pgr_inventory import PgrRiskItem
from app.domain.entities.risk_card import CardStatus, RiskCard
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.domain.entities.signals import (
    AreaMonthlyMetrics,
    ContextEvent,
    ContextEventType,
)
from app.domain.entities.survey import SurveySummary, SurveyType
from app.infrastructure.repositories.in_memory_pulso_repositories import (
    InMemoryAreaRepository,
    InMemoryPgrInventoryRepository,
    InMemoryRiskCardRepository,
    InMemorySignalRepository,
    InMemorySurveyRepository,
)


def get_synthetic_areas() -> List[Area]:
    """Retorna o cadastro das 7 areas da empresa ficticia."""
    return [
        Area(
            id="area_fin",
            name="Financeiro",
            headcount=18,
            manager_name="Roberto Prado",
            description="Controladoria, contas a pagar e receber.",
        ),
        Area(
            id="area_atend",
            name="Atendimento ao Cliente",
            headcount=32,
            manager_name="Juliana Costa",
            description="Operacao de suporte e SAC multicanal.",
        ),
        Area(
            id="area_log",
            name="Logistica",
            headcount=28,
            manager_name="Fernando Dias",
            description="Distribuicao, armazem e gestao de rotas.",
        ),
        Area(
            id="area_vend",
            name="Vendas",
            headcount=35,
            manager_name="Marcos Valente",
            description="Comercial B2B e expansao de clientes.",
        ),
        Area(
            id="area_des",
            name="Design de Produto",
            headcount=3,
            manager_name="Luciana Mello",
            description="UX/UI e design visual de produtos digitais.",
        ),
        Area(
            id="area_eng",
            name="Engenharia de Software",
            headcount=30,
            manager_name="Beatriz Neves",
            description="Desenvolvimento, infraestrutura e produto.",
        ),
        Area(
            id="area_rh",
            name="Recursos Humanos",
            headcount=8,
            manager_name="Camila Guimaraes",
            description="Gente, gestao, DP e departamento de SST.",
        ),
    ]


def get_synthetic_context_events() -> List[ContextEvent]:
    """Retorna eventos corporativos de contexto que justificam as variacoes nos times."""
    return [
        # Caso 2: Nova meta de atendimentos implantada em agosto
        ContextEvent(
            id="evt_01",
            area_id="area_atend",
            event_date=date(2026, 8, 15),
            event_type=ContextEventType.NOVA_META,
            description="Implantacao de nova meta agressiva de atendimentos por hora (+35%).",
        ),
        # Caso 3: Troca de gestor da logistica em setembro
        ContextEvent(
            id="evt_02",
            area_id="area_log",
            event_date=date(2026, 9, 5),
            event_type=ContextEventType.TROCA_GESTOR,
            description="Entrada de nova lideranca operacional na gestao do armazem.",
        ),
        # Evento de contratacao no comercial
        ContextEvent(
            id="evt_03",
            area_id="area_vend",
            event_date=date(2026, 7, 1),
            event_type=ContextEventType.CONTRATACOES,
            description="Entrada de 8 novos executivos de contas para ciclo de vendas.",
        ),
    ]


def get_synthetic_metrics() -> List[AreaMonthlyMetrics]:
    """Retorna a serie historica de 6 meses para todas as areas."""
    metrics: List[AreaMonthlyMetrics] = []

    # Competencias: Maio a Outubro de 2026
    periods = [
        date(2026, 5, 1),
        date(2026, 6, 1),
        date(2026, 7, 1),
        date(2026, 8, 1),
        date(2026, 9, 1),
        date(2026, 10, 1),
    ]

    # 1. Caso 1: Financeiro (18 pessoas) - Totalmente Estavel
    for p in periods:
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_fin_{p.month}",
                area_id="area_fin",
                competence_period=p,
                certificate_days_count=12,
                certificate_cases_count=3,
                unexcused_absences_count=1,
                shift_coverages_count=0,
                resignation_requests_count=0,
                turnover_rate=0.0,
                overtime_hours_avg=3.5,
                unfulfilled_break_intervals_count=0,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=4.2,
            )
        )

    # 2. Caso 2: Atendimento ao Cliente (32 pessoas) - Sobrecarga & Meta (Pico em Outubro)
    atend_data = [
        # Mai: baseline
        (22, 6, 2, 8.0, 0, 4.1),
        # Jun: baseline
        (21, 5, 3, 8.5, 1, 4.0),
        # Jul: baseline
        (22, 6, 3, 9.0, 0, 3.9),
        # Ago: Nova meta entra em vigor no dia 15
        (25, 7, 5, 10.5, 1, 3.5),
        # Set: Indicadores subindo
        (29, 8, 7, 12.0, 2, 3.0),
        # Out: Salto critico (dias atestado +45% vs baseline 22 -> 32 dias; horas extras +60% vs baseline 9 -> 14.4h)
        (32, 10, 10, 14.4, 4, 2.4),
    ]
    for idx, (days, cases, coverages, he, resignations, score) in enumerate(atend_data):
        p = periods[idx]
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_atend_{p.month}",
                area_id="area_atend",
                competence_period=p,
                certificate_days_count=days,
                certificate_cases_count=cases,
                unexcused_absences_count=coverages,
                shift_coverages_count=coverages,
                resignation_requests_count=resignations,
                turnover_rate=round((resignations / 32) * 100, 1),
                overtime_hours_avg=he,
                unfulfilled_break_intervals_count=coverages * 2,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=1 if idx >= 4 else 0,
                pulse_survey_workload_score=score,
            )
        )

    # 3. Caso 3: Logistica (28 pessoas) - Troca de Gestor em Setembro -> 5 pedidos de demissao
    log_data = [
        # Mai a Ago: rotina normal
        (15, 4, 2, 6.0, 0, 3.9),
        (16, 4, 2, 6.2, 1, 3.8),
        (15, 3, 1, 5.8, 0, 4.0),
        (16, 4, 2, 6.0, 0, 3.9),
        # Set: Troca de gestor
        (18, 5, 4, 7.5, 2, 3.3),
        # Out: Repercussao -> 5 pedidos de demissao
        (20, 5, 6, 8.0, 5, 2.7),
    ]
    for idx, (days, cases, coverages, he, resignations, score) in enumerate(log_data):
        p = periods[idx]
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_log_{p.month}",
                area_id="area_log",
                competence_period=p,
                certificate_days_count=days,
                certificate_cases_count=cases,
                unexcused_absences_count=coverages,
                shift_coverages_count=coverages,
                resignation_requests_count=resignations,
                turnover_rate=round((resignations / 28) * 100, 1),
                overtime_hours_avg=he,
                unfulfilled_break_intervals_count=2,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=score,
            )
        )

    # 4. Caso 4: Vendas (35 pessoas) - 3 Denuncias de Assedio em 2 Meses
    for idx, p in enumerate(periods):
        denuncias = 0
        if p.month == 9:
            denuncias = 1
        elif p.month == 10:
            denuncias = 2

        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_vend_{p.month}",
                area_id="area_vend",
                competence_period=p,
                certificate_days_count=18 + idx,
                certificate_cases_count=4,
                unexcused_absences_count=2,
                shift_coverages_count=1,
                resignation_requests_count=1 if idx >= 4 else 0,
                turnover_rate=2.8 if idx >= 4 else 0.0,
                overtime_hours_avg=8.0,
                unfulfilled_break_intervals_count=1,
                harassment_complaints_count=denuncias,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=3.2 if idx >= 4 else 3.8,
            )
        )

    # 5. Caso 6: Design (3 pessoas) - Menos de 5 pessoas (dados anonimizados por exclusao)
    for p in periods:
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_des_{p.month}",
                area_id="area_des",
                competence_period=p,
                certificate_days_count=2,
                certificate_cases_count=1,
                unexcused_absences_count=0,
                shift_coverages_count=0,
                resignation_requests_count=0,
                turnover_rate=0.0,
                overtime_hours_avg=4.0,
                unfulfilled_break_intervals_count=0,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=4.0,
            )
        )

    # Engenharia e RH: operacao estavel
    for p in periods:
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_eng_{p.month}",
                area_id="area_eng",
                competence_period=p,
                certificate_days_count=14,
                certificate_cases_count=3,
                unexcused_absences_count=1,
                shift_coverages_count=0,
                resignation_requests_count=1 if p.month == 8 else 0,
                turnover_rate=3.3 if p.month == 8 else 0.0,
                overtime_hours_avg=5.5,
                unfulfilled_break_intervals_count=0,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=4.1,
            )
        )
        metrics.append(
            AreaMonthlyMetrics(
                id=f"met_rh_{p.month}",
                area_id="area_rh",
                competence_period=p,
                certificate_days_count=4,
                certificate_cases_count=1,
                unexcused_absences_count=0,
                shift_coverages_count=0,
                resignation_requests_count=0,
                turnover_rate=0.0,
                overtime_hours_avg=2.0,
                unfulfilled_break_intervals_count=0,
                harassment_complaints_count=0,
                sesmt_long_term_absences_count=0,
                pulse_survey_workload_score=4.5,
            )
        )

    return metrics


def get_synthetic_surveys() -> List[SurveySummary]:
    """Retorna os resultados sumarizados das pesquisas pulso anonimas."""
    return [
        SurveySummary(
            id="surv_atend_10",
            area_id="area_atend",
            survey_type=SurveyType.CHECKIN_MENSAL,
            competence_period=date(2026, 10, 1),
            respondents_count=29,
            participation_rate=90.6,
            average_score=2.6,
            workload_score=2.4,
            summarized_themes=[
                "Metas de atendimento por hora consideradas irreais",
                "Sensacao de esgotamento e ritmo acelerado sem pausas",
                "Inseguranca quanto ao atingimento de bonificacao",
            ],
            urgent_help_flags_count=1,
        ),
        SurveySummary(
            id="surv_log_10",
            area_id="area_log",
            survey_type=SurveyType.DIRECIONADA_AREA,
            competence_period=date(2026, 10, 1),
            respondents_count=24,
            participation_rate=85.7,
            average_score=2.9,
            workload_score=3.2,
            summarized_themes=[
                "Falta de comunicacao clara da nova gestao sobre escalas",
                "Clima de tensao em reunioes de alinhamento",
            ],
            urgent_help_flags_count=0,
        ),
    ]


def get_synthetic_initial_cards() -> List[RiskCard]:
    """Retorna os cards que o Pulso emite para demonstracao no pitch."""
    return [
        # Caso 2: Atendimento ao Cliente (Card Vermelho)
        RiskCard(
            id="card_atend_01",
            area_id="area_atend",
            area_name="Atendimento ao Cliente",
            area_headcount=32,
            risk_level=RiskLevel.VERMELHO,
            probable_risk_factor=PsychosocialRiskFactor.SOBRECARGA_METAS,
            evidence_summary=(
                "dias de atestado +45%, horas extras +60%, 4 pedidos de demissao "
                "(media da empresa: 1), nota de carga de trabalho na pesquisa pulso caiu de 3,9 para 2,4."
            ),
            context_description=(
                "a alta comeca 2 semanas depois da nova meta de atendimentos por hora "
                "(implantada em agosto)."
            ),
            suggested_action=(
                "revisar a meta com a lideranca, conversa de escuta com o time mediada pelo RH, "
                "incluir o risco no inventario do PGR com reavaliacao em 60 dias."
            ),
            consulted_sources=[
                "ponto",
                "folha",
                "desligamentos",
                "pesquisa pulso de outubro",
            ],
            status=CardStatus.ABERTO,
            created_at=datetime.now(timezone.utc),
            risk_score=92.4,
            shap_breakdown=[
                {
                    "feature_name": "delta_atestados",
                    "display_name": "Aumento em Dias de Atestado (+45%)",
                    "contribution_pct": 38.0,
                    "observed_value": "+45% vs historico trimestral",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "queda_nota_clima",
                    "display_name": "Queda na Avaliacao de Carga / Clima",
                    "contribution_pct": 27.0,
                    "observed_value": "Queda de 3.9 para 2.4",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "delta_horas_extras",
                    "display_name": "Sobrecarga em Horas Extras (+60%)",
                    "contribution_pct": 24.0,
                    "observed_value": "+60% vs media basal",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "razao_turnover",
                    "display_name": "Pedidos de Demissao Voluntaria",
                    "contribution_pct": 11.0,
                    "observed_value": "4 saidas (media empresa: 1)",
                    "direction": "AGRAVANTE",
                },
            ],
            ai_provider_used="xgboost+gemini-1.5-pro",
            ai_fallback_triggered=False,
        ),
        # Caso 3: Logistica (Card Amarelo)
        RiskCard(
            id="card_log_01",
            area_id="area_log",
            area_name="Logistica",
            area_headcount=28,
            risk_level=RiskLevel.AMARELO,
            probable_risk_factor=PsychosocialRiskFactor.LIDERANCA_CONFLITO,
            evidence_summary=(
                "5 pedidos de demissao em 30 dias apos meses de estabilidade turnover zero; "
                "queda na nota de suporte da lideranca de 3,9 para 2,7."
            ),
            context_description=(
                "pico de saidas comeca logo apos mudanca de gestor da area ocorrida em setembro."
            ),
            suggested_action=(
                "disparar pesquisa direcionada a area sobre lideranca e alinhamento com a nova gestao."
            ),
            consulted_sources=["desligamentos", "pesquisa direcionada", "eventos_contexto"],
            status=CardStatus.ABERTO,
            created_at=datetime.now(timezone.utc),
            risk_score=68.0,
            shap_breakdown=[
                {
                    "feature_name": "razao_turnover",
                    "display_name": "Concentracao de Pedidos de Demissao",
                    "contribution_pct": 65.0,
                    "observed_value": "5 pedidos apos troca de lideranca",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "queda_suporte_lideranca",
                    "display_name": "Queda no Suporte da Lideranca (Pesquisa)",
                    "contribution_pct": 25.0,
                    "observed_value": "Queda de 3.9 para 2.7",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "variacao_atestados",
                    "display_name": "Variacao Residual em Atestados",
                    "contribution_pct": 10.0,
                    "observed_value": "+5%",
                    "direction": "AGRAVANTE",
                },
            ],
            ai_provider_used="xgboost+gemini-1.5-pro",
            ai_fallback_triggered=False,
        ),
        # Caso 4: Vendas (Escalonamento para Compliance)
        RiskCard(
            id="card_vend_01",
            area_id="area_vend",
            area_name="Vendas",
            area_headcount=35,
            risk_level=RiskLevel.VERMELHO,
            probable_risk_factor=PsychosocialRiskFactor.ASSEDIO,
            evidence_summary=(
                "3 denuncias registradas no canal de compliance nos ultimos 2 meses para a mesma area."
            ),
            context_description=(
                "reincidencia de apontamentos no canal confidencial apos contratacoes recentes."
            ),
            suggested_action=(
                "escalonar imediatamente para o comite de compliance; o Pulso nao acessa conteudo "
                "nem envolvidos das denuncias."
            ),
            consulted_sources=["canal_denuncias_contagem"],
            status=CardStatus.ESCALADO_COMPLIANCE,
            created_at=datetime.now(timezone.utc),
            risk_score=96.0,
            shap_breakdown=[
                {
                    "feature_name": "denuncias_compliance",
                    "display_name": "Concentracao de Denuncias no Canal de Etica",
                    "contribution_pct": 85.0,
                    "observed_value": "3 denuncias em 2 meses",
                    "direction": "AGRAVANTE",
                },
                {
                    "feature_name": "impacto_secundario",
                    "display_name": "Impacto Secundario em Atestados",
                    "contribution_pct": 15.0,
                    "observed_value": "+12% atestados",
                    "direction": "AGRAVANTE",
                },
            ],
            ai_provider_used="xgboost+rule-based-compliance",
            ai_fallback_triggered=False,
        ),
    ]


def seed_in_memory_repositories(
    area_repo: InMemoryAreaRepository,
    signal_repo: InMemorySignalRepository,
    risk_card_repo: InMemoryRiskCardRepository,
    pgr_repo: InMemoryPgrInventoryRepository,
    survey_repo: InMemorySurveyRepository,
) -> Dict[str, int]:
    """Popula os repositorios em memoria com a massa de dados dos 7 casos de demonstracao."""
    areas = get_synthetic_areas()
    for area in areas:
        area_repo.save(area)

    events = get_synthetic_context_events()
    for evt in events:
        signal_repo.add_event(evt)

    metrics = get_synthetic_metrics()
    for met in metrics:
        signal_repo.add_metrics(met)

    surveys = get_synthetic_surveys()
    for surv in surveys:
        survey_repo.save_summary(surv)

    cards = get_synthetic_initial_cards()
    for card in cards:
        risk_card_repo.save(card)

    return {
        "areas_seeded": len(areas),
        "events_seeded": len(events),
        "metrics_seeded": len(metrics),
        "surveys_seeded": len(surveys),
        "cards_seeded": len(cards),
    }


if __name__ == "__main__":
    a_repo = InMemoryAreaRepository()
    s_repo = InMemorySignalRepository()
    c_repo = InMemoryRiskCardRepository()
    p_repo = InMemoryPgrInventoryRepository()
    surv_repo = InMemorySurveyRepository()

    summary = seed_in_memory_repositories(a_repo, s_repo, c_repo, p_repo, surv_repo)
    print("Base sintetica do Pulso populada com sucesso!")
    print(summary)
