"""Agente analista de riscos psicossociais baseado em LLM com regras hibridas (NR-1).

Integracao da Arquitetura em 2 Camadas:
    - Camada 1: Motor Preditivo Tabular XGBoost com explicabilidade auditavel SHAP.
    - Camada 2: Failover Manager Multi-Provider (Gemini com fallback deterministico e Circuit Breaker).
"""

import logging
from typing import Any

from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.infrastructure.llm.resilience.failover_manager import (
    FailoverExecutionMetadata,
    FailoverManager,
)
from app.infrastructure.ml.xgboost_risk_engine import RiskPredictionResult, XGBoostRiskEngine

logger = logging.getLogger(__name__)


class PulsoAgentLLM:
    """Motor analitico, preditivo e generativo para conformidade da NR-1.

    Principio de Confiabilidade:
        - A matematica e probabilidade sao 100% calculadas pelo modelo tabular XGBoost.
        - O SHAP decompõe legalmente a participacao de cada indicador na auditoria.
        - Se a IA generativa em nuvem falhar, o Failover Manager ativa o motor deterministico local.
    """

    def __init__(
        self,
        api_key: str | None = None,
        model_name: str = "gemini-1.5-pro",
        xgboost_engine: XGBoostRiskEngine | None = None,
        failover_manager: FailoverManager | None = None,
        devolutiva_writer: Any | None = None,
    ) -> None:
        """Inicializa os motores da Camada 1 (ML) e Camada 2 (LLM Failover).

        devolutiva_writer: provedor com generate_devolutiva(area, acao) e is_available();
        se ausente ou com falha, a devolutiva usa o texto deterministico.
        """
        self.api_key = api_key
        self.model_name = model_name
        self.ml_engine = xgboost_engine or XGBoostRiskEngine()
        self.failover_manager = failover_manager or FailoverManager()
        self.devolutiva_writer = devolutiva_writer

    def correlate_and_classify(
        self,
        area_name: str,
        history_delta: dict[str, Any],
        context_events: list[dict[str, Any]],
        survey_themes: list[str],
    ) -> tuple[
        RiskLevel, PsychosocialRiskFactor, str, str, RiskPredictionResult, FailoverExecutionMetadata
    ]:
        """Executa a predicao tabular do XGBoost com SHAP e gera a hipotese contextual via LLM.

        Retorna:
            Tuple contendo:
                - nivel_risco
                - fator_psicossocial
                - sintese_evidencias / hipotese
                - acao_proposta_pgr
                - predicao_xgboost_shap (Camada 1)
                - metadados_resiliencia_ia (Camada 2)
        """
        variacao_dias = float(history_delta.get("variacao_dias_atestado_pct", 0.0))
        variacao_he = float(history_delta.get("variacao_horas_extras_pct", 0.0))
        demissoes = int(history_delta.get("pedidos_demissao_periodo", 0))
        denuncias = int(history_delta.get("denuncias_contagem", 0))
        media_empresa = float(history_delta.get("media_empresa_pedidos_demissao", 1.0))
        queda_clima = float(
            history_delta.get("queda_nota_clima", 1.5 if variacao_dias > 30 else 0.0)
        )

        # 1. CAMADA 1: Inferencia do XGBoost + Explicabilidade SHAP
        ml_result = self.ml_engine.predict(
            variacao_dias_atestado_pct=variacao_dias,
            variacao_horas_extras_pct=variacao_he,
            pedidos_demissao=demissoes,
            media_empresa_pedidos_demissao=media_empresa,
            queda_nota_clima=queda_clima,
            denuncias_compliance=denuncias,
        )

        metrics_summary = (
            f"Variação de Atestados: {variacao_dias:+.1f}%, Horas Extras: {variacao_he:+.1f}%, "
            f"Demissões: {demissoes} (média: {media_empresa}), Denúncias: {denuncias}."
        )

        # 2. CAMADA 2: Geracao com Resiliencia e Failover Multi-Provider
        hypothesis, action, meta = self.failover_manager.generate_hypothesis_and_action(
            area_name=area_name,
            metrics_summary=metrics_summary,
            context_events=context_events,
            shap_narrative=ml_result.audit_narrative,
            factor=ml_result.probable_factor.value,
        )

        return (
            ml_result.risk_level,
            ml_result.probable_factor,
            hypothesis,
            action,
            ml_result,
            meta,
        )

    def draft_focus_card(
        self,
        area_name: str,
        headcount: int,
        metrics_summary: str,
        context_summary: str,
        factor: str,
    ) -> tuple[str, str]:
        """Redige o card de atencao do RH com evidencias e sugestao de acao."""
        evidence = f"Para a area {area_name} ({headcount} pessoas): {metrics_summary}"
        suggested = (
            f"Fator identificado: {factor}. Recomenda-se revisao com gestor e acolhimento do time."
        )
        return evidence, suggested

    def generate_devolutiva_text(self, area_name: str, action_description: str) -> str:
        """Gera o texto de devolutiva ('Voce falou, a empresa fez') em linguagem acolhedora."""
        writer = self.devolutiva_writer
        if writer is not None and writer.is_available():
            try:
                return str(writer.generate_devolutiva(area_name, action_description))
            except Exception as exc:  # noqa: BLE001 - qualquer falha cai no texto local
                logger.warning("Devolutiva via LLM falhou, usando texto local: %s", exc)
        return (
            f"Equipe {area_name}: Apos ouvirmos suas percepcoes nos check-ins recentes, "
            f"a lideranca e o RH formalizaram a seguinte medida de cuidado: {action_description}."
        )

    def process_chat_query(
        self,
        query_text: str,
        context_data: dict[str, Any],
    ) -> tuple[str, FailoverExecutionMetadata]:
        """Processa a consulta do chat corporativo com substituicao automatica de IA."""
        return self.failover_manager.generate_chat_reply(query_text, context_data)

    def generate_team_response(self, query_text: str) -> tuple[str, list[str]]:
        """Gera resposta sobre equipes no chat mantendo compatibilidade com use cases existentes."""
        reply, _ = self.failover_manager.generate_chat_reply(query_text, {})
        return reply, ["ponto", "folha", "desligamentos", "pesquisa_pulso", "xgboost_shap"]
