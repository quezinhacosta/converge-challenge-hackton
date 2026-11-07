"""Testes unitarios da camada de dados, regras legais, agentes e rotas da Pessoa A (vitAI)."""

import pytest

from app.schemas import (
    AreaData,
    CasoRiskCard,
    ChatQueryRequest,
    ChatQueryResponse,
    DecisaoRequest,
    DecisaoResponse,
    FechamentoSummaryResponse,
)
from app.protections import (
    calcular_score_e_pesos_shap,
    inspecionar_busca_nominativa,
    verificar_quorum_anonimizacao,
)
from app.pulso_agents import (
    AgenteComunicacao,
    AgenteHistoriador,
    AgenteRegulatorio,
    FeatherlessClient,
)
from app.main import (
    carregar_areas_sinteticas,
    executar_fechamento_mensal,
    obter_dados_area,
    registrar_decisao_rh,
    consultar_chat_copiloto,
)
from app.presentation.compat import HTTPException


# -----------------------------------------------------------------------------
# 1. Testes de Schemas e Contratos Pydantic
# -----------------------------------------------------------------------------
def test_schemas_data_contracts() -> None:
    """Valida a instanciacao e consistencia dos modelos de dados Pydantic."""
    area = AreaData(
        area_id="area_teste",
        area_name="Time Teste",
        headcount=10,
        manager_name="Gestor Teste",
        variacao_dias_atestado_pct=15.0,
        variacao_horas_extras_pct=20.0,
        pedidos_demissao_periodo=1,
        media_empresa_pedidos_demissao=1.0,
        nota_clima_atual=3.5,
        nota_clima_anterior=4.0,
    )
    assert area.area_id == "area_teste"
    assert area.headcount == 10
    assert not area.is_blocked_privacy

    decisao = DecisaoRequest(acao="APROVADO", revisor_nome="RH Principal", prazo_dias=60)
    assert decisao.acao == "APROVADO"
    assert decisao.prazo_dias == 60


# -----------------------------------------------------------------------------
# 2. Testes de Protecoes Rigidas & LGPD
# -----------------------------------------------------------------------------
def test_quorum_anonimizacao_nr1() -> None:
    """Verifica que areas com N < 5 sao bloqueadas com flag BLOCKED_PRIVACY."""
    # Design com 3 colaboradores (Caso 5)
    elegivel, flag, justificativa = verificar_quorum_anonimizacao(3)
    assert not elegivel
    assert flag == "BLOCKED_PRIVACY"
    assert "bloqueada por quorum" in justificativa

    # Area com 5 colaboradores (limite inferior permitido)
    elegivel_5, flag_5, _ = verificar_quorum_anonimizacao(5)
    assert elegivel_5
    assert flag_5 == "ELIGIBLE"

    # Atendimento com 32 colaboradores
    elegivel_32, flag_32, _ = verificar_quorum_anonimizacao(32)
    assert elegivel_32
    assert flag_32 == "ELIGIBLE"


def test_recusa_etica_busca_nominativa() -> None:
    """Verifica bloqueio imediato para buscas nominativas e diagnosticos medicos (CIDs)."""
    # Tentativa de busca por colaborador nominativo
    violou, motivo = inspecionar_busca_nominativa("Como estao os atestados da Carla?")
    assert violou
    assert motivo is not None
    assert "Carla" in motivo
    assert "LGPD" in motivo

    # Tentativa de busca por CID medico
    violou_cid, motivo_cid = inspecionar_busca_nominativa("Quantos colaboradores estao com CID F32?")
    assert violou_cid
    assert motivo_cid is not None
    assert "Sigilo Medico" in motivo_cid

    # Pergunta agregada valida
    violou_ok, motivo_ok = inspecionar_busca_nominativa("Qual a situacao geral do setor de Atendimento?")
    assert not violou_ok
    assert motivo_ok is None


def test_calculo_score_e_pesos_shap() -> None:
    """Verifica o calculo matematico de risco e decomposicao de pesos proporcionais (SHAP)."""
    # Caso critico: atestados +45%, HE +60%, 4 demissoes, queda de clima de 1.5 pontos
    score, nivel, pesos, narrativa = calcular_score_e_pesos_shap(
        variacao_atestados_pct=45.0,
        variacao_horas_extras_pct=60.0,
        pedidos_demissao=4,
        media_empresa_pedidos_demissao=1.0,
        queda_clima_absoluta=1.5,
    )
    assert score >= 70.0
    assert nivel == "VERMELHO"
    assert "atestados" in pesos
    assert "clima" in pesos
    assert "horas_extras" in pesos
    assert "turnover" in pesos
    soma_pesos = sum(pesos.values())
    assert 99.0 <= soma_pesos <= 101.0  # Aproximadamente 100%
    assert "% do risco adveio" in narrativa


# -----------------------------------------------------------------------------
# 3. Testes dos Agentes e Resiliencia Featherless
# -----------------------------------------------------------------------------
def test_agentes_resiliencia_e_fallback() -> None:
    """Garante que os 3 agentes operam estavelmente sem credenciais externas ou em falha de rede."""
    client = FeatherlessClient(api_key="", timeout=1.0)
    assert not client.has_active_credentials

    historiador = AgenteHistoriador(client)
    hipotese = historiador.formular_hipotese(
        area_name="Atendimento ao Cliente",
        evidencias_texto="Atestados +45%, Horas Extras +60%",
        eventos_contexto=["Nova meta de atendimentos"],
    )
    assert "meta" in hipotese.lower()

    regulatorio = AgenteRegulatorio(client)
    medida = regulatorio.estruturar_medida_nr1(
        area_name="Atendimento ao Cliente",
        fator_risco="Sobrecarga",
        hipotese_contexto=hipotese,
    )
    assert "fator_nr1" in medida
    assert "NR-1" in medida["artigo_nr1"]
    assert medida["prazo_dias"] == 60

    comunicacao = AgenteComunicacao(client)
    texto, perguntas = comunicacao.gerar_comunicacao_fechamento_e_roteiro(
        area_name="Atendimento ao Cliente",
        medida_nr1=medida["medida_sugerida"],
    )
    assert "Voce falou, a empresa fez" in texto
    assert len(perguntas) == 3


# -----------------------------------------------------------------------------
# 4. Testes dos Endpoints Principais da API (Pessoa B)
# -----------------------------------------------------------------------------
def test_endpoint_fechamento_mensal() -> None:
    """Testa a esteira completa do endpoint POST /fechamento."""
    resultado = executar_fechamento_mensal()
    assert resultado.total_areas == 7
    assert resultado.areas_elegiveis == 6
    assert resultado.areas_bloqueadas == 1
    assert len(resultado.casos_gerados) == 7

    # Verifica se Design foi bloqueado por privacidade
    card_design = next(c for c in resultado.casos_gerados if c.area_id == "area_des")
    assert card_design.status == "BLOCKED_PRIVACY"
    assert card_design.score_risco == 0.0

    # Verifica se Atendimento gerou card critico
    card_atend = next(c for c in resultado.casos_gerados if c.area_id == "area_atend")
    assert card_atend.nivel_risco == "VERMELHO"
    assert card_atend.score_risco >= 70.0


def test_endpoint_obter_dados_area() -> None:
    """Testa consulta individual no endpoint GET /areas/{area_id}."""
    area_log = obter_dados_area("area_log")
    assert area_log.area_name == "Logistica"
    assert area_log.headcount == 28
    assert not area_log.is_blocked_privacy

    area_des = obter_dados_area("area_des")
    assert area_des.is_blocked_privacy

    with pytest.raises(HTTPException):
        obter_dados_area("area_inexistente")


def test_endpoint_deliberacao_rh_e_pgr() -> None:
    """Testa registro de aprovacao, ajuste e descarte no endpoint POST /casos/{id}/decisao."""
    executar_fechamento_mensal()

    # 1. Aprovacao
    req_aprov = DecisaoRequest(acao="APROVADO", revisor_nome="Mariana RH")
    resp_aprov = registrar_decisao_rh("area_atend", req_aprov)
    assert resp_aprov.novo_status == "APROVADO"
    assert resp_aprov.registrado_no_pgr
    assert "GRO-NR1" in resp_aprov.protocolo_gro

    # 2. Ajuste
    req_ajust = DecisaoRequest(
        acao="AJUSTADO",
        revisor_nome="Carlos SESMT",
        acao_ajustada_texto="Reuniao emergencial com diretoria para repactuar metas.",
        prazo_dias=30,
    )
    resp_ajust = registrar_decisao_rh("area_log", req_ajust)
    assert resp_ajust.novo_status == "AJUSTADO"
    assert resp_ajust.registrado_no_pgr

    # 3. Descarte
    req_desc = DecisaoRequest(
        acao="DESCARTADO",
        revisor_nome="Diretor Gente",
        justificativa="Sinal isolado ja equacionado na semana anterior.",
    )
    resp_desc = registrar_decisao_rh("area_fin", req_desc)
    assert resp_desc.novo_status == "DESCARTADO"
    assert not resp_desc.registrado_no_pgr


def test_endpoint_chat_query_guardrails() -> None:
    """Testa o endpoint POST /chat/query sob diferentes consultas."""
    # Consulta violando LGPD com busca nominativa
    req_viola = ChatQueryRequest(pergunta="Quais sao os atestados do Joao?")
    resp_viola = consultar_chat_copiloto(req_viola)
    assert resp_viola.recusado_lgpd
    assert resp_viola.motivo_recusa is not None

    # Consulta valida sobre area de logistica
    req_log = ChatQueryRequest(pergunta="Como esta a situacao da area de Logistica?")
    resp_log = consultar_chat_copiloto(req_log)
    assert not resp_log.recusado_lgpd
    assert "Logistica" in resp_log.areas_citadas
    assert "5 pedidos de demissao" in resp_log.resposta

    # Consulta sobre area bloqueada (Design)
    req_des = ChatQueryRequest(pergunta="Quais sao as metricas de Design?")
    resp_des = consultar_chat_copiloto(req_des)
    assert not resp_des.recusado_lgpd
    assert "bloqueados" in resp_des.resposta or "menos de 5 pessoas" in resp_des.resposta
