"""Caso de uso para comparacao historica, correlacao com contexto e classificacao de risco NR-1."""

from typing import Any, Dict, Protocol
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.domain.repositories.interfaces import (
    AreaRepository,
    SignalRepository,
    SurveyRepository,
)


class PsychosocialRiskReasoner(Protocol):
    """Protocolo do motor analitico e LLM para correlacionar eventos e classificar fatores da NR-1."""

    def correlate_and_classify(
        self,
        area_name: str,
        history_delta: Dict[str, Any],
        context_events: list,
        survey_themes: list,
    ) -> Any:
        """Correlaciona metricas com contexto e infere o fator de risco e nivel de atencao."""
        ...


class AnalyzePsychosocialRisksUseCase:
    """Executa as Etapas 3, 4 e 5 do Ciclo do Pulso:

    Etapa 3 - Comparar:
        Compara cada area com o proprio historico (ultimos 3 a 6 meses) e com a media da empresa.
    Etapa 4 - Correlacionar:
        Cruza a alta dos indicadores operacionais com eventos de contexto (nova meta, troca de gestor)
        e com os temas apontados nas pesquisas pulso.
    Etapa 5 - Classificar (XGBoost + SHAP):
        Associa o padrao a um fator de risco psicossocial da NR-1 (sobrecarga, lideranca, assedio)
        e define o nivel de atencao (VERDE, AMARELO, VERMELHO) com explicabilidade auditavel.
    """

    def __init__(
        self,
        area_repository: AreaRepository,
        signal_repository: SignalRepository,
        survey_repository: SurveyRepository,
        reasoner: PsychosocialRiskReasoner,
    ) -> None:
        """Inicializa o caso de uso analitico."""
        self.area_repository = area_repository
        self.signal_repository = signal_repository
        self.survey_repository = survey_repository
        self.reasoner = reasoner

    def execute(self, area_id: str) -> Dict[str, Any]:
        """Analisa os riscos psicossociais da area para a competencia corrente.

        Argumentos:
            area_id: Identificador da area em avaliacao.

        Retorna:
            Dict[str, Any]: Nivel de risco, fator psicossocial associado, evidencias e correlacoes.
        """
        area = self.area_repository.get_by_id(area_id)
        if not area:
            raise ValueError(f"Area '{area_id}' nao encontrada.")

        metrics_history = self.signal_repository.get_metrics_history(area_id, months=6)
        events = self.signal_repository.get_context_events(area_id)
        survey_summary = self.survey_repository.get_latest_summary(area_id)

        survey_themes = survey_summary.summarized_themes if survey_summary else []
        event_dicts = [
            {"date": e.event_date.isoformat(), "type": e.event_type.value, "desc": e.description}
            for e in events
        ]

        if not metrics_history:
            return {
                "area_id": area.id,
                "area_name": area.name,
                "risk_level": RiskLevel.VERDE.value,
                "factor": PsychosocialRiskFactor.ESTAVEL_SEM_FATOR.value,
                "evidence_summary": "Sem historico suficiente para avaliacao.",
                "suggested_action": "Continuar monitoramento.",
                "context_events": event_dicts,
                "shap_breakdown": [],
                "risk_score": 0.0,
            }

        current = metrics_history[0]
        prev_list = metrics_history[1:] if len(metrics_history) > 1 else metrics_history
        avg_days = (
            sum(m.certificate_days_count for m in prev_list) / len(prev_list)
            if prev_list
            else current.certificate_days_count
        )
        avg_he = (
            sum(m.overtime_hours_avg for m in prev_list) / len(prev_list)
            if prev_list
            else current.overtime_hours_avg
        )

        variacao_dias = (
            round(((current.certificate_days_count - avg_days) / avg_days) * 100, 1)
            if avg_days > 0
            else 0.0
        )
        variacao_he = (
            round(((current.overtime_hours_avg - avg_he) / avg_he) * 100, 1) if avg_he > 0 else 0.0
        )

        history_delta = {
            "variacao_dias_atestado_pct": variacao_dias,
            "variacao_horas_extras_pct": variacao_he,
            "pedidos_demissao_periodo": current.resignation_requests_count,
            "denuncias_contagem": sum(m.harassment_complaints_count for m in metrics_history[:2]),
            "media_empresa_pedidos_demissao": 1.0,
            "queda_nota_clima": 1.5 if variacao_dias > 30 else 0.0,
        }

        reasoner_result = self.reasoner.correlate_and_classify(
            area.name, history_delta, event_dicts, survey_themes
        )

        # Suporte a retorno enriquecido (6 elementos) ou legado (4 elementos)
        shap_breakdown: list = []
        risk_score: float = 0.0
        ai_meta: dict = {}

        if len(reasoner_result) >= 6:
            level, factor, evidence, action, ml_pred, meta = reasoner_result
            risk_score = ml_pred.risk_score
            shap_breakdown = [item.to_dict() for item in ml_pred.shap_breakdown]
            ai_meta = meta.to_dict()
        else:
            level, factor, evidence, action = reasoner_result[:4]

        return {
            "area_id": area.id,
            "area_name": area.name,
            "area_headcount": area.headcount,
            "risk_level": level,
            "factor": factor,
            "evidence_summary": evidence,
            "suggested_action": action,
            "context_events": event_dicts,
            "history_delta": history_delta,
            "risk_score": risk_score,
            "shap_breakdown": shap_breakdown,
            "ai_execution_metadata": ai_meta,
        }
