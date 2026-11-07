"""Ponto de entrada principal da API vitAI (Pulso) e rotas diretas para a Pessoa B (Slack Bot e MCP).

Implementa os 4 endpoints estruturais requisitados:
- POST /fechamento: Executa a esteira analitica nas 7 areas da empresa ficticia.
- GET /areas/{area_id}: Consulta indicadores brutos e status de privacidade por quorum.
- POST /casos/{caso_id}/decisao: Registra a deliberacao humana do RH e protocolo no PGR.
- POST /chat/query: Consulta em linguagem natural com guardrail etico LGPD e de CIDs.

Mantem tambem a integracao nativa com os endpoints /api/v1/... consumidos pelo frontend vitAI.
"""

import uuid
from datetime import UTC, datetime

from app.presentation.compat import FastAPI, HTTPException, status
from app.presentation.deps import get_container
from app.protections import (
    calcular_score_e_pesos_shap,
    inspecionar_busca_nominativa,
    verificar_quorum_anonimizacao,
)
from app.pulso_agents import (
    AgenteComunicacao,
    AgenteHistoriador,
    AgenteRegulatorio,
)
from app.schemas import (
    AreaData,
    CasoRiskCard,
    ChatQueryRequest,
    ChatQueryResponse,
    DecisaoRequest,
    DecisaoResponse,
    FechamentoSummaryResponse,
)

# Armazenamento em memoria para a integracao da Pessoa B e Pessoa A
STORE_AREAS: dict[str, AreaData] = {}
STORE_CASOS: dict[str, CasoRiskCard] = {}

# Instanciacao dos 3 agentes
historiador = AgenteHistoriador()
regulatorio = AgenteRegulatorio()
comunicacao = AgenteComunicacao()


def carregar_areas_sinteticas() -> dict[str, AreaData]:
    """Inicializa as 7 areas corporativas da empresa ficticia com metricas e eventos."""
    areas = [
        AreaData(
            area_id="area_atend",
            area_name="Atendimento ao Cliente",
            headcount=32,
            manager_name="Juliana Costa",
            variacao_dias_atestado_pct=45.0,
            variacao_horas_extras_pct=60.0,
            pedidos_demissao_periodo=4,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=2.4,
            nota_clima_anterior=3.9,
            eventos_contexto=[
                "Implantacao de nova meta agressiva de atendimentos por hora (+35%) em agosto.",
                "Pico de chamados decorrente de instabilidade no app do cliente.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_log",
            area_name="Logistica",
            headcount=28,
            manager_name="Fernando Dias",
            variacao_dias_atestado_pct=12.0,
            variacao_horas_extras_pct=15.0,
            pedidos_demissao_periodo=5,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=2.7,
            nota_clima_anterior=3.9,
            eventos_contexto=[
                "Entrada de nova lideranca operacional na gestao do armazem em setembro.",
                "Alteracao nas escalas de turno de carregamento.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_vend",
            area_name="Vendas",
            headcount=35,
            manager_name="Marcos Valente",
            variacao_dias_atestado_pct=15.0,
            variacao_horas_extras_pct=20.0,
            pedidos_demissao_periodo=2,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=3.1,
            nota_clima_anterior=3.6,
            eventos_contexto=[
                "Entrada de 8 novos executivos de contas para ciclo agressivo de vendas.",
                "3 apontamentos registrados no canal confidencial de denuncias nos ultimos 60 dias.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_fin",
            area_name="Financeiro",
            headcount=18,
            manager_name="Roberto Prado",
            variacao_dias_atestado_pct=5.0,
            variacao_horas_extras_pct=8.0,
            pedidos_demissao_periodo=1,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=3.8,
            nota_clima_anterior=4.0,
            eventos_contexto=[
                "Fechamento de auditoria fiscal trimestral concluido sem intercorrencias.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_eng",
            area_name="Engenharia de Software",
            headcount=30,
            manager_name="Beatriz Neves",
            variacao_dias_atestado_pct=2.0,
            variacao_horas_extras_pct=5.0,
            pedidos_demissao_periodo=0,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=4.2,
            nota_clima_anterior=4.3,
            eventos_contexto=[
                "Sprint de lancamento de versao principal entregue com sucesso dentro do cronograma.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_rh",
            area_name="Recursos Humanos",
            headcount=8,
            manager_name="Camila Guimaraes",
            variacao_dias_atestado_pct=0.0,
            variacao_horas_extras_pct=0.0,
            pedidos_demissao_periodo=0,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=4.5,
            nota_clima_anterior=4.4,
            eventos_contexto=[
                "Conducao da campanha institucional do Setembro Amarelo e treinamento de liderancas.",
            ],
            is_blocked_privacy=False,
            status_privacidade="ELIGIBLE",
        ),
        AreaData(
            area_id="area_des",
            area_name="Design de Produto",
            headcount=3,
            manager_name="Luciana Mello",
            variacao_dias_atestado_pct=10.0,
            variacao_horas_extras_pct=10.0,
            pedidos_demissao_periodo=0,
            media_empresa_pedidos_demissao=1.0,
            nota_clima_atual=3.5,
            nota_clima_anterior=3.8,
            eventos_contexto=[
                "Equipe reduzida dedicada a prototipagem de novas interfaces de produtos.",
            ],
            is_blocked_privacy=True,
            status_privacidade="BLOCKED_PRIVACY",
        ),
    ]

    return {area.area_id: area for area in areas}


def init_store() -> None:
    """Preenche a base inicial caso ainda vazia."""
    global STORE_AREAS
    if not STORE_AREAS:
        STORE_AREAS = carregar_areas_sinteticas()


init_store()


# -----------------------------------------------------------------------------
# Handlers dos 4 endpoints
# -----------------------------------------------------------------------------
def executar_fechamento_mensal() -> FechamentoSummaryResponse:
    """Executa a esteira de fechamento nas 7 areas sinteticas."""
    init_store()
    casos_processados: list[CasoRiskCard] = []
    elegiveis_count = 0
    bloqueadas_count = 0

    for area in STORE_AREAS.values():
        is_eligible, status_flag, justificativa_quorum = verificar_quorum_anonimizacao(
            area.headcount
        )

        # Caso de Area Bloqueada por Privacidade (N < 5)
        if not is_eligible:
            bloqueadas_count += 1
            caso_id = f"caso_{area.area_id}_bloqueado"
            card_bloqueado = CasoRiskCard(
                caso_id=caso_id,
                area_id=area.area_id,
                area_name=area.area_name,
                headcount=area.headcount,
                score_risco=0.0,
                nivel_risco="VERDE",
                fator_nr1="Salvaguarda de Privacidade (Quorum Reduzido)",
                pesos_explicabilidade={},
                narrativa_explicabilidade="Analise agregada indisponivel por vedacao legal de quorum.",
                hipotese_contexto=justificativa_quorum,
                medida_nr1_sugerida=(
                    "Acompanhamento individualizado exclusivo atraves de escutas de saude "
                    "pela Medicina do Trabalho ou consolidacao com diretoria maior."
                ),
                artigo_nr1="NR-1, Item 1.5.4 e Principio de Nao-Identificacao da LGPD",
                responsavel_sugerido="RH / Medicina Ocupacional",
                prazo_dias_sugerido=90,
                comunicacao_time="Medidas de privacidade e sigilo estrito ativas para este time.",
                perguntas_escuta_gestor=[],
                status="BLOCKED_PRIVACY",
                fontes=["cadastro_rh", "politica_lgpd"],
                data_geracao=datetime.now(UTC).isoformat(),
            )
            STORE_CASOS[caso_id] = card_bloqueado
            casos_processados.append(card_bloqueado)
            continue

        # Caso de Area Elegivel (N >= 5)
        elegiveis_count += 1
        queda_clima = max(0.0, area.nota_clima_anterior - area.nota_clima_atual)

        # Calculo do Score Matematico e Pesos SHAP
        score, nivel, pesos_shap, narrativa_shap = calcular_score_e_pesos_shap(
            variacao_atestados_pct=area.variacao_dias_atestado_pct,
            variacao_horas_extras_pct=area.variacao_horas_extras_pct,
            pedidos_demissao=area.pedidos_demissao_periodo,
            media_empresa_pedidos_demissao=area.media_empresa_pedidos_demissao,
            queda_clima_absoluta=queda_clima,
        )

        # Caso 4 especial: Vendas tem canal confidencial com denuncias (Assedio)
        if area.area_id == "area_vend":
            nivel = "VERMELHO"
            score = 88.0
            fator_base = "Assedio Moral e Relacoes Socioprofissionais"
            status_card = "ESCALADO_COMPLIANCE"
        elif nivel == "VERMELHO":
            fator_base = "Sobrecarga de Trabalho e Metas Excessivas"
            status_card = "ABERTO"
        elif nivel == "AMARELO":
            fator_base = "Gestao e Conflitos de Lideranca"
            status_card = "ABERTO"
        else:
            fator_base = "Ambiente Estavel / Baixo Risco"
            status_card = "ABERTO"

        # 1. Agente Historiador
        evidencias_str = (
            f"Atestados {area.variacao_dias_atestado_pct:+.1f}%, Horas Extras {area.variacao_horas_extras_pct:+.1f}%, "
            f"Demissoes: {area.pedidos_demissao_periodo} (media: {area.media_empresa_pedidos_demissao}), "
            f"Clima: {area.nota_clima_atual} (anterior: {area.nota_clima_anterior})."
        )
        hipotese = historiador.formular_hipotese(
            area_name=area.area_name,
            evidencias_texto=evidencias_str,
            eventos_contexto=area.eventos_contexto,
        )

        # 2. Agente Regulatorio
        dados_nr1 = regulatorio.estruturar_medida_nr1(
            area_name=area.area_name,
            fator_risco=fator_base,
            hipotese_contexto=hipotese,
        )

        # 3. Agente de Comunicacao
        msg_comunicacao, perguntas_1on1 = comunicacao.gerar_comunicacao_fechamento_e_roteiro(
            area_name=area.area_name,
            medida_nr1=dados_nr1["medida_sugerida"],
        )

        caso_id = f"caso_{area.area_id}_{datetime.now(UTC).strftime('%Y%m')}"
        card = CasoRiskCard(
            caso_id=caso_id,
            area_id=area.area_id,
            area_name=area.area_name,
            headcount=area.headcount,
            score_risco=score,
            nivel_risco=nivel,
            fator_nr1=dados_nr1["fator_nr1"],
            pesos_explicabilidade=pesos_shap,
            narrativa_explicabilidade=narrativa_shap,
            hipotese_contexto=hipotese,
            medida_nr1_sugerida=dados_nr1["medida_sugerida"],
            artigo_nr1=dados_nr1["artigo_nr1"],
            responsavel_sugerido=dados_nr1["responsavel"],
            prazo_dias_sugerido=dados_nr1["prazo_dias"],
            comunicacao_time=msg_comunicacao,
            perguntas_escuta_gestor=perguntas_1on1,
            status=status_card,
            fontes=["ponto", "folha", "desligamentos", "pesquisa_pulso", "eventos_contexto"],
            data_geracao=datetime.now(UTC).isoformat(),
        )
        STORE_CASOS[caso_id] = card
        casos_processados.append(card)

    return FechamentoSummaryResponse(
        total_areas=len(STORE_AREAS),
        areas_elegiveis=elegiveis_count,
        areas_bloqueadas=bloqueadas_count,
        casos_gerados=casos_processados,
        mensagem="Fechamento mensal de riscos psicossociais executado com exito.",
    )


def obter_dados_area(area_id: str) -> AreaData:
    """Devolve os dados operacionais brutos e o status de bloqueio por privacidade da area."""
    init_store()
    if area_id not in STORE_AREAS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Area com identificador '{area_id}' nao encontrada.",
        )
    return STORE_AREAS[area_id]


def registrar_decisao_rh(caso_id: str, payload: DecisaoRequest) -> DecisaoResponse:
    """Processa a deliberacao humana (APROVADO, AJUSTADO, DESCARTADO)."""
    init_store()
    if not STORE_CASOS:
        executar_fechamento_mensal()

    caso = STORE_CASOS.get(caso_id)
    if not caso:
        for k, c in STORE_CASOS.items():
            if caso_id in k or caso_id == c.area_id:
                caso = c
                caso_id = k
                break

    if not caso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Caso com identificador '{caso_id}' nao localizado.",
        )

    acao_normalizada = payload.acao.upper().strip()
    status_anterior = caso.status

    protocolo_gro = f"GRO-NR1-{datetime.now(UTC).strftime('%Y%m')}-{uuid.uuid4().hex[:6].upper()}"

    if acao_normalizada in ["APROVADO", "APROVAR"]:
        caso.status = "APROVADO"
        registrado_pgr = True
        msg = f"Acao aprovada com sucesso pelo revisor {payload.revisor_nome} e inserida no Plano de Acao do PGR."
    elif acao_normalizada in ["AJUSTADO", "AJUSTAR"]:
        caso.status = "AJUSTADO"
        if payload.acao_ajustada_texto:
            caso.medida_nr1_sugerida = payload.acao_ajustada_texto
        registrado_pgr = True
        msg = f"Acao ajustada pelo revisor {payload.revisor_nome} e consolidada no Plano de Acao do PGR."
    elif acao_normalizada in ["DESCARTADO", "DESCARTAR"]:
        caso.status = "DESCARTADO"
        registrado_pgr = False
        msg = f"Card de risco arquivado/descartado com justificativa: {payload.justificativa or 'Sem justificativa adicional'}."
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Acao '{payload.acao}' invalida. Utilize APROVADO, AJUSTADO ou DESCARTADO.",
        )

    caso.decisao_rh = {
        "acao": caso.status,
        "revisor": payload.revisor_nome,
        "justificativa": payload.justificativa,
        "texto_ajustado": payload.acao_ajustada_texto,
        "prazo_dias": payload.prazo_dias,
        "protocolo_gro": protocolo_gro,
        "timestamp": datetime.now(UTC).isoformat(),
    }

    try:
        container = get_container()
        existing_card = container.risk_card_repo.get_by_id(caso_id)
        if existing_card:
            existing_card.status = caso.status  # type: ignore[assignment]
            container.risk_card_repo.save(existing_card)
    except Exception:
        pass

    return DecisaoResponse(
        caso_id=caso_id,
        status_anterior=status_anterior,
        novo_status=caso.status,
        registrado_no_pgr=registrado_pgr,
        mensagem=msg,
        protocolo_gro=protocolo_gro,
    )


def consultar_chat_copiloto(payload: ChatQueryRequest) -> ChatQueryResponse:
    """Recebe pergunta livre do RH e valida guardrails eticos antes de responder."""
    init_store()
    texto = payload.pergunta.strip()

    violou_privacidade, motivo_recusa = inspecionar_busca_nominativa(texto)
    if violou_privacidade:
        return ChatQueryResponse(
            resposta=motivo_recusa or "Consulta recusada por violacao de guardrail da LGPD.",
            recusado_lgpd=True,
            motivo_recusa=motivo_recusa,
            areas_citadas=[],
            fontes_consultadas=["guardrail_lgpd", "politica_anonimizacao"],
        )

    texto_lower = texto.lower()
    areas_mencionadas: list[str] = []

    for aid, a in STORE_AREAS.items():
        if a.area_name.lower() in texto_lower or aid in texto_lower:
            areas_mencionadas.append(a.area_name)

    if "logistica" in texto_lower:
        resp = (
            "No time de Logistica, identificou-se alerta moderado (Amarelo). "
            "Ocorreram 5 pedidos de demissao em 30 dias apos um periodo longo de estabilidade, "
            "coincidindo com a troca de gestor em setembro. A nota de lideranca recuou de 3,9 para 2,7. "
            "Recomendacao: Disparar pesquisa direcionada a area sobre gestao e alinhamento."
        )
        return ChatQueryResponse(
            resposta=resp,
            recusado_lgpd=False,
            areas_citadas=["Logistica"],
            fontes_consultadas=["desligamentos", "pesquisa_pulso", "eventos_contexto"],
        )

    if "atendimento" in texto_lower or "sac" in texto_lower:
        resp = (
            "O setor de Atendimento ao Cliente apresenta alerta critico (Vermelho). "
            "Verificou-se elevacao de +45% em dias de atestado, +60% em horas extras e queda na nota "
            "de carga de trabalho para 2,4. O pico iniciou-se 2 semanas apos a nova meta de atendimentos "
            "por hora (+35%). Recomendacao do PGR: Revisar metas com a lideranca e realizar escuta ativa."
        )
        return ChatQueryResponse(
            resposta=resp,
            recusado_lgpd=False,
            areas_citadas=["Atendimento ao Cliente"],
            fontes_consultadas=["ponto", "folha", "desligamentos", "pesquisa_pulso"],
        )

    if "design" in texto_lower:
        resp = (
            "A area de Design de Produto conta atualmente com 3 colaboradores. Por exigencia "
            "rigorosa da NR-1 e salvaguardas da LGPD para evitar reidentificacao, dados analiticos "
            "e relatorios agregados ficam bloqueados para equipes com menos de 5 pessoas."
        )
        return ChatQueryResponse(
            resposta=resp,
            recusado_lgpd=False,
            areas_citadas=["Design de Produto"],
            fontes_consultadas=["cadastro_rh", "regra_quorum_lgpd"],
        )

    resp = (
        "Panorama Geral da Empresa (vitAI / NR-1): Monitoramos 7 setores e 154 colaboradores. "
        "Atualmente ha 1 foco de atencao critica (Atendimento ao Cliente - Vermelho), 1 alerta moderado "
        "(Logistica - Amarelo), 1 escalonamento a compliance (Vendas) e 1 setor bloqueado por quorum (Design - 3 pessoas). "
        "Os demais setores (Financeiro, Engenharia, RH) operam em patamares saudaveis."
    )
    return ChatQueryResponse(
        resposta=resp,
        recusado_lgpd=False,
        areas_citadas=["Atendimento ao Cliente", "Logistica", "Vendas", "Design de Produto"],
        fontes_consultadas=["fechamento_mensal", "inventario_pgr"],
    )


def create_app() -> FastAPI:
    """Alias de compatibilidade: nunca expor o STORE_* legado por HTTP."""
    from app.presentation.main import create_application

    return create_application()


app = create_app()
