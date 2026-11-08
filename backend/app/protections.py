"""Protecoes rigidas, salvaguardas da LGPD e calculo explicavel de risco (vitAI / NR-1).

Contem regras puramente deterministicas (sem dependencia de LLM) para:
1. Anonimizacao e bloqueio por quorum estatistico minimo (N >= 5).
2. Recusa etica instantanea a consultas nominativas e diagnosticos medicos (CIDs).
3. Calculo do Score de Risco (0 a 100) com decomposicao explicavel de pesos (SHAP).
"""

import re
from typing import Dict, List, Optional, Tuple

MIN_ANONYMIZATION_QUORUM: int = 5

NOMINATIVE_NAME_KEYWORDS: List[str] = [
    "carla",
    "joao",
    "maria",
    "pedro",
    "lucas",
    "mariana",
    "ana",
    "paulo",
    "fernanda",
    "roberto prado",
    "juliana costa",
    "fernando dias",
    "marcos valente",
    "luciana mello",
    "beatriz neves",
    "camila guimaraes",
]

INDIVIDUAL_TARGET_PATTERNS: List[str] = [
    r"\batestado[s]? d[eao]\b",
    r"\blaudo[s]? d[eao]\b",
    r"\bcid d[eao]\b",
    r"\bburnout d[eao]\b",
    r"\bdepress[aã]o d[eao]\b",
    r"\bsal[aá]rio d[eao]\b",
    r"\bcpf\b",
    r"\bcolaborador[a]?\s+[a-z]+",
    r"\bfavorita[s]?\b",
    r"\bdemiti[r]?\s+[a-z]+",
]

CID_CLINICAL_PATTERNS: List[str] = [
    r"\b[fF][0-9]{2}(\.[0-9])?\b",  # CID-10 Transtornos Mentais (F00-F99)
    r"\bcid\s*[-:]?\s*[0-9a-zA-Z]+",
    r"\bdiagn[oó]stico\s+cl[ií]nico\b",
    r"\bprontu[aá]rio\b",
    r"\breceitu[aá]rio\b",
]


def verificar_quorum_anonimizacao(headcount: int) -> Tuple[bool, str, str]:
    """Valida se a area possui quorum minimo estatistico (N >= 5) exigido pela NR-1 e LGPD.

    Retorna:
        Tuple[bool, str, str]:
            - is_eligible: True se elegivel para agregacao, False se bloqueada.
            - status_flag: 'ELIGIBLE' ou 'BLOCKED_PRIVACY'.
            - justification: Explicacao juridico-estatistica da salvaguarda.
    """
    if headcount < MIN_ANONYMIZATION_QUORUM:
        return (
            False,
            "BLOCKED_PRIVACY",
            (
                f"Area com {headcount} pessoas bloqueada por quorum estatistico insuficiente "
                f"(minimo N >= {MIN_ANONYMIZATION_QUORUM}). Em conformidade com a NR-1 e a LGPD, "
                "equipes com menos de 5 colaboradores nao tem dados agregados exibidos para "
                "impedir a deducao de respostas ou a reidentificacao involuntaria de individuos."
            ),
        )
    return (
        True,
        "ELIGIBLE",
        f"Quorum compativel (N = {headcount} >= {MIN_ANONYMIZATION_QUORUM}) para analise agregada.",
    )


def inspecionar_busca_nominativa(texto: str) -> Tuple[bool, Optional[str]]:
    """Varre texto de entrada em busca de nomes proprios, CIDs ou investigacoes de individuos.

    Retorna:
        Tuple[bool, Optional[str]]:
            - violou_privacidade: True se detectou tentativa de busca individual ou medica.
            - motivo_recusa: Texto de recusa etica fundamentada ou None se aprovado.
    """
    if not texto:
        return False, None

    texto_lower = texto.lower()

    # 1. Verificacao de nomes conhecidos de colaboradores
    for name in NOMINATIVE_NAME_KEYWORDS:
        pattern = rf"\b{re.escape(name)}\b"
        if re.search(pattern, texto_lower):
            return (
                True,
                (
                    f"Recusa Etica de Privacidade (LGPD / NR-1): A consulta identificou busca direcionada "
                    f"ao individuo '{name.title()}'. O vitAI monitora exclusivamente padroes coletivos "
                    "e organizacionais por setor (N >= 5), sendo terminantemente vedado inspecionar, "
                    "rastrear ou expor informacoes de colaboradores especificos."
                ),
            )

    # 2. Verificacao de alvos individuais (atestado de, CPF, etc.)
    for target_pat in INDIVIDUAL_TARGET_PATTERNS:
        if re.search(target_pat, texto_lower):
            return (
                True,
                (
                    "Recusa Etica de Privacidade (LGPD / NR-1): Identificada intencao de consulta sobre "
                    "dados individuais ou pessoais de colaboradores. O sistema disponibiliza somente "
                    "indicadores agregados por area funcional para prevencao coletiva no PGR."
                ),
            )

    # 3. Verificacao de CIDs ou diagnosticos clinicos de saude
    for cid_pat in CID_CLINICAL_PATTERNS:
        if re.search(cid_pat, texto, re.IGNORECASE):
            return (
                True,
                (
                    "Recusa Etica Medica (Sigilo Medico / LGPD): O vitAI nao armazena nem processa "
                    "codigos de diagnostico (CID), laudos ou prontuarios medicos individuais. Tais dados "
                    "sao de posse e sigilo estrito da Medicina do Trabalho, operando o sistema apenas "
                    "com dias de ausencia agregados por time."
                ),
            )

    return False, None


def calcular_score_e_pesos_shap(
    variacao_atestados_pct: float,
    variacao_horas_extras_pct: float,
    pedidos_demissao: int,
    media_empresa_pedidos_demissao: float,
    queda_clima_absoluta: float,
) -> Tuple[float, str, Dict[str, float], str]:
    """Calcula deterministica e fidedignamente o Score de Risco (0-100) e os pesos de explicabilidade (SHAP).

    Garante auditabilidade legal para a fiscalizacao do Trabalho (NR-1 / Portaria MTE nº 1.419/2024).

    Retorna:
        Tuple contendo:
            - score_total (0.0 a 100.0)
            - nivel_risco ('VERDE', 'AMARELO', 'VERMELHO')
            - pesos_proporcionais (dicionario com as porcentagens exatas somando ~100%)
            - narrativa_auditoria (explicacao em texto corrido dos pesos)
    """
    # 1. Normalizacao dos 4 componentes para a escala 0 a 100
    # Atestados: variacao positiva eleva o risco linearmente (saturando em +100%)
    comp_atestados = max(0.0, min(100.0, variacao_atestados_pct * 1.5))

    # Clima: queda na nota de 1.0 a 2.5 pontos representa risco severo
    comp_clima = max(0.0, min(100.0, queda_clima_absoluta * 55.0))

    # Horas Extras: elevacao acima do normal
    comp_he = max(0.0, min(100.0, variacao_horas_extras_pct * 1.25))

    # Turnover: razao entre demissoes da area e a media da empresa
    ratio_turnover = (
        (pedidos_demissao / max(1.0, media_empresa_pedidos_demissao))
        if pedidos_demissao > 0
        else 0.0
    )
    comp_turnover = max(0.0, min(100.0, ratio_turnover * 22.0))

    # 2. Pesos estruturais dos fatores de risco psicossocial
    p_atestados = 0.35
    p_clima = 0.30
    p_he = 0.20
    p_turnover = 0.15

    # 3. Contribuicoes individuais
    c_atestados = comp_atestados * p_atestados
    c_clima = comp_clima * p_clima
    c_he = comp_he * p_he
    c_turnover = comp_turnover * p_turnover

    score_bruto = c_atestados + c_clima + c_he + c_turnover
    score_final = round(max(0.0, min(100.0, score_bruto)), 1)

    # 4. Calculo dos pesos relativos proporcionais (SHAP Feature Importance)
    soma_contribuicoes = c_atestados + c_clima + c_he + c_turnover
    if soma_contribuicoes > 0:
        peso_atestados = round((c_atestados / soma_contribuicoes) * 100.0, 1)
        peso_clima = round((c_clima / soma_contribuicoes) * 100.0, 1)
        peso_he = round((c_he / soma_contribuicoes) * 100.0, 1)
        peso_turnover = round(max(0.0, 100.0 - (peso_atestados + peso_clima + peso_he)), 1)
    else:
        peso_atestados = 35.0
        peso_clima = 30.0
        peso_he = 20.0
        peso_turnover = 15.0

    pesos = {
        "atestados": peso_atestados,
        "clima": peso_clima,
        "horas_extras": peso_he,
        "turnover": peso_turnover,
    }

    # 5. Classificacao do nivel de risco
    if score_final >= 70.0:
        nivel_risco = "VERMELHO"
    elif score_final >= 40.0:
        nivel_risco = "AMARELO"
    else:
        nivel_risco = "VERDE"

    # 6. Narrativa de auditoria legal
    narrativa = (
        f"{pesos['atestados']}% do risco adveio do aumento de atestados medicos, "
        f"{pesos['clima']}% da queda no clima organizacional, "
        f"{pesos['horas_extras']}% da sobrecarga em horas extras e "
        f"{pesos['turnover']}% dos pedidos de desligamento no periodo."
    )

    return score_final, nivel_risco, pesos, narrativa
