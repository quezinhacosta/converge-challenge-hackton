"""Suite de testes unitarios e integrados validando os 7 casos de demonstracao do Pulso."""

from app.application.dtos.chat_dto import ChatQueryRequestDTO
from app.application.dtos.risk_card_dto import ResolveRiskCardRequestDTO
from app.domain.entities.risk_factor import PsychosocialRiskFactor, RiskLevel
from app.presentation.deps import PulsoAppContainer


def test_scenario_1_financeiro_estavel_nao_alarmista() -> None:
    """Caso 1: Area de Financeiro estavel -> Analisa e nao gera alerta de risco."""
    container = PulsoAppContainer()
    result = container.analyze_risks_uc.execute("area_fin")

    assert result["risk_level"] == RiskLevel.VERDE
    assert result["factor"] == PsychosocialRiskFactor.ESTAVEL_SEM_FATOR
    assert "dentro da media historica" in result["evidence_summary"]


def test_scenario_2_atendimento_sobrecarga_caminho_feliz() -> None:
    """Caso 2: Atendimento ao Cliente -> Card Vermelho de sobrecarga, aprovado pelo RH no PGR."""
    container = PulsoAppContainer()

    # 1. Analise de riscos identifica o pico
    analysis = container.analyze_risks_uc.execute("area_atend")
    assert analysis["risk_level"] == RiskLevel.VERMELHO
    assert analysis["factor"] == PsychosocialRiskFactor.SOBRECARGA_METAS

    # 2. Geracao do Ponto Focal de Atencao (Card Aberto)
    card_dto = container.generate_card_uc.execute("area_atend", analysis)
    assert card_dto.status == "ABERTO"
    assert card_dto.risk_level == "VERMELHO"

    # 3. Deliberacao humana (1-clique do RH) aprova no PGR
    pgr_item = container.register_pgr_uc.execute(
        card_dto.card_id,
        ResolveRiskCardRequestDTO(
            action_type="APROVAR_PGR",
            reviewer_name="Mariana Souza (Analista de RH)",
            deadline_days=60,
        ),
    )
    assert pgr_item.fator_psicossocial == "SOBRECARGA_METAS"
    assert pgr_item.responsavel == "Mariana Souza (Analista de RH)"

    # 4. Verifica emissao automatica da devolutiva ("Voce falou, a empresa fez")
    devolutiva = container.survey_repo._devolutivas.get(f"dev_{pgr_item.item_id}")
    assert devolutiva is not None
    assert "medida de cuidado" in devolutiva.approved_action_plan


def test_scenario_3_logistica_troca_gestor_lideranca() -> None:
    """Caso 3: Logistica -> Troca de gestor seguida de 5 demissoes gera Card Amarelo."""
    container = PulsoAppContainer()
    analysis = container.analyze_risks_uc.execute("area_log")

    assert analysis["risk_level"] == RiskLevel.AMARELO
    assert analysis["factor"] == PsychosocialRiskFactor.LIDERANCA_CONFLITO
    assert "pesquisa direcionada" in analysis["suggested_action"]


def test_scenario_4_vendas_denuncias_assedio_escalonamento() -> None:
    """Caso 4: Vendas -> 3 denuncias de assedio escalonadas imediatamente sem ler conteudo."""
    container = PulsoAppContainer()
    analysis = container.analyze_risks_uc.execute("area_vend")

    assert analysis["risk_level"] == RiskLevel.VERMELHO
    assert analysis["factor"] == PsychosocialRiskFactor.ASSEDIO

    card_dto = container.generate_card_uc.execute("area_vend", analysis)
    assert card_dto.status == "ESCALADO"
    assert "comite de compliance" in card_dto.acao_sugerida


def test_scenario_5_rh_pede_atestados_da_carla_recusa_guardrail() -> None:
    """Caso 5: Tentativa de solicitar atestados individuais da Carla barrada pelo guardrail etico."""
    container = PulsoAppContainer()

    # Pergunta individual que deve ser recusada
    resp_carla = container.chat_uc.execute(
        ChatQueryRequestDTO(
            user_id="rh_01",
            user_name="Gestor",
            query_text="Me mostra os atestados da Carla",
        )
    )
    assert resp_carla.is_refusal is True
    assert "LGPD" in resp_carla.reply_text

    # Pergunta coletiva que deve ser respondida
    resp_log = container.chat_uc.execute(
        ChatQueryRequestDTO(
            user_id="rh_01",
            user_name="Gestor",
            query_text="Como esta o time de Logistica?",
        )
    )
    assert resp_log.is_refusal is False
    assert "Logistica" in resp_log.reply_text


def test_scenario_6_time_design_tres_pessoas_anonimizacao() -> None:
    """Caso 6: Time de Design com 3 pessoas (< 5) tem dados ocultados por exclusao."""
    container = PulsoAppContainer()
    comparison = container.collect_signals_uc.execute("area_des")

    assert comparison.headcount == 3
    assert comparison.is_anonymized is True
    assert comparison.variacao_dias_atestado_pct == 0.0


def test_scenario_7_atendimento_sessenta_dias_depois_fecha_ciclo() -> None:
    """Caso 7: Acompanhamento de 60 dias pos-acao -> Melhora comprovada encerra o ciclo no PGR."""
    container = PulsoAppContainer()

    # 1. Registra acao no PGR
    card_dto = container.generate_card_uc.execute(
        "area_atend", container.analyze_risks_uc.execute("area_atend")
    )
    pgr_item = container.register_pgr_uc.execute(
        card_dto.card_id,
        ResolveRiskCardRequestDTO(
            action_type="APROVAR_PGR",
            reviewer_name="Mariana Souza",
            deadline_days=60,
        ),
    )

    # 2. Acompanhamento apos 60 dias (Caso 7)
    eval_result = container.track_evolution_uc.execute(pgr_item.item_id)
    assert eval_result.houve_melhora_indicadores is True
    assert eval_result.status_final == "FECHADO"
    assert "reducao de 35% nos dias de atestado" in eval_result.resumo_evolucao
