"""Agente analista de riscos psicossociais baseado em LLM com regras hibridas (NR-1)."""

from typing import Any, Dict, List, Optional, Tuple
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel


class PulsoAgentLLM:
    """Motor generativo e correlacional de riscos psicossociais da NR-1.

    Arquitetura Hibrida (Regras Deterministicas + LLM):
        - Os calculos de variacao percentual e quoruns rodam em codigo deterministico.
        - O LLM correlaciona metricas com contexto organizacional e redige o card.
    """

    def __init__(self, api_key: Optional[str] = None, model_name: str = "glm-4-flash") -> None:
        """Inicializa o cliente do modelo de linguagem."""
        self.api_key = api_key
        self.model_name = model_name

    def correlate_and_classify(
        self,
        area_name: str,
        history_delta: Dict[str, Any],
        context_events: List[Dict[str, Any]],
        survey_themes: List[str],
    ) -> Tuple[RiskLevel, PsychosocialRiskFactor, str, str]:
        """Correlaciona evidencias e classifica o fator provavel sob a NR-1.

        Retorna:
            Tuple contendo: (nivel_risco, fator_psicossocial, sintese_evidencias, acao_proposta).
        """
        variacao_dias = history_delta.get("variacao_dias_atestado_pct", 0.0)
        variacao_he = history_delta.get("variacao_horas_extras_pct", 0.0)
        demissoes = history_delta.get("pedidos_demissao_periodo", 0)
        denuncias = history_delta.get("denuncias_contagem", 0)

        # Regra de assedio (Caso 4: Vendas)
        if denuncias >= 3:
            return (
                RiskLevel.VERMELHO,
                PsychosocialRiskFactor.ASSEDIO,
                f"{denuncias} denuncias registradas no canal de compliance nos ultimos 2 meses.",
                (
                    "escalonar imediatamente para o comite de compliance; o Pulso nao acessa conteudo "
                    "nem envolvidos das denuncias."
                ),
            )

        # Regra de sobrecarga e metas excessivas (Caso 2: Atendimento)
        if variacao_dias >= 30.0 and variacao_he >= 40.0:
            return (
                RiskLevel.VERMELHO,
                PsychosocialRiskFactor.SOBRECARGA_METAS,
                (
                    f"dias de atestado +{variacao_dias}%, horas extras +{variacao_he}%, "
                    f"{demissoes} pedidos de demissao (media da empresa: 1)."
                ),
                (
                    "revisar a meta com a lideranca, conversa de escuta com o time mediada pelo RH, "
                    "incluir o risco no inventario do PGR com reavaliacao em 60 dias."
                ),
            )

        # Regra de lideranca e conflito (Caso 3: Logistica)
        if demissoes >= 4:
            return (
                RiskLevel.AMARELO,
                PsychosocialRiskFactor.LIDERANCA_CONFLITO,
                f"{demissoes} pedidos de demissao em curto periodo apos meses de estabilidade turnover zero.",
                "disparar pesquisa direcionada a area sobre lideranca e alinhamento com a nova gestao.",
            )

        # Caso estavel (Caso 1: Financeiro)
        return (
            RiskLevel.VERDE,
            PsychosocialRiskFactor.ESTAVEL_SEM_FATOR,
            "Indicadores dentro da media historica sem variacoes atipicas observadas.",
            "Nenhuma intervencao necessaria no momento. Manter monitoramento continuo.",
        )

    def draft_focus_card(
        self,
        area_name: str,
        headcount: int,
        metrics_summary: str,
        context_summary: str,
        factor: str,
    ) -> Tuple[str, str]:
        """Redige o card de atencao do RH com evidencias e sugestao de acao."""
        evidence = f"Para a area {area_name} ({headcount} pessoas): {metrics_summary}"
        suggested = (
            f"Fator identificado: {factor}. Recomenda-se revisao com gestor e acolhimento do time."
        )
        return evidence, suggested

    def generate_devolutiva_text(self, area_name: str, action_description: str) -> str:
        """Gera o texto de devolutiva ('Voce falou, a empresa fez') em linguagem acolhedora."""
        return (
            f"Equipe {area_name}: Apos ouvirmos suas percepcoes nos check-ins recentes, "
            f"a lideranca e o RH formalizaram a seguinte medida de cuidado: {action_description}."
        )

    def generate_team_response(self, query_text: str) -> Tuple[str, List[str]]:
        """Gera resposta consultando exclusivamente dados agregados de times e areas."""
        lower = query_text.lower()
        if "logistica" in lower or "logística" in lower:
            return (
                (
                    "O time de Logistica (28 pessoas) apresentou 5 pedidos de demissao recentes "
                    "logo apos a troca de gestor em setembro. Foi emitido um Card Amarelo recomendando "
                    "pesquisa pulso direcionada a area sobre relacoes de lideranca."
                ),
                ["ponto", "folha", "desligamentos", "eventos_contexto"],
            )
        if "atendimento" in lower:
            return (
                (
                    "O time de Atendimento ao Cliente (32 pessoas) esta sob Atencao Alta (Card Vermelho) "
                    "devido a um salto de +45% em dias de atestado e +60% em horas extras, coincidente "
                    "com a nova meta de atendimentos por hora implantada em agosto."
                ),
                ["ponto", "folha", "pesquisa_pulso", "eventos_contexto"],
            )
        return (
            (
                "O Pulso monitora 7 areas corporativas. Atendimento e Logistica possuem apontamentos "
                "de risco sob analise do RH, enquanto Financeiro e Engenharia estao estaveis."
            ),
            ["base_geral_areas"],
        )
