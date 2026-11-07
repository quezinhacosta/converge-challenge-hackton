"""Base de conhecimento curta usada nos prompts (RAG leve, sem banco vetorial).

O conteudo e pequeno o bastante para ir inteiro no contexto. Os trechos da NR-1 sao
parafrases com o numero do item; confira a redacao oficial antes de citar no pitch.
"""

from app.domain.entities.risk_factor import PsychosocialRiskFactor

FACTOR_CATALOG: dict[PsychosocialRiskFactor, str] = {
    PsychosocialRiskFactor.SOBRECARGA_METAS: (
        "Excesso de demandas e metas: volume ou ritmo acima da capacidade da equipe."
    ),
    PsychosocialRiskFactor.JORNADAS_LONGAS: (
        "Jornadas longas: horas extras recorrentes, intervalos e descansos nao cumpridos."
    ),
    PsychosocialRiskFactor.LIDERANCA_CONFLITO: (
        "Falta de suporte e conflitos com a lideranca; ma gestao de mudancas na equipe."
    ),
    PsychosocialRiskFactor.ASSEDIO: (
        "Assedio moral ou sexual. Tratado pelo compliance; o agente nao le conteudo de denuncias."
    ),
    PsychosocialRiskFactor.FALTA_CLAREZA_PAPEL: (
        "Baixa clareza de papel: atribuicoes e expectativas ambiguas ou conflitantes."
    ),
    PsychosocialRiskFactor.FALTA_AUTONOMIA: (
        "Baixo controle e autonomia sobre como e quando o trabalho e feito."
    ),
    PsychosocialRiskFactor.INSEGURANCA_TRABALHO: (
        "Inseguranca: reestruturacoes, ameacas de desligamento, falta de previsibilidade."
    ),
    PsychosocialRiskFactor.ESTAVEL_SEM_FATOR: "Sem fator de risco relevante identificado.",
}

NR1_REFERENCES: list[str] = [
    "NR-1 cap. 1.5 (Portaria MTE 1.419/2024): o gerenciamento de riscos ocupacionais "
    "inclui os fatores de risco psicossociais relacionados ao trabalho.",
    "Item 1.5.3.3: a organizacao deve consultar os trabalhadores sobre a percepcao de riscos "
    "e comunicar os riscos do inventario e as medidas do plano de acao.",
    "Item 1.5.5.2.1 e 1.5.5.2.2: o plano de acao indica medidas de prevencao com cronograma, "
    "formas de acompanhamento e afericao de resultados.",
    "Item 1.5.7.3.2: o inventario descreve perigos, grupos expostos, avaliacao com classificacao "
    "e os criterios adotados.",
]

PRIVACY_RULES = (
    "Regras inegociaveis: fale apenas de areas e equipes, nunca de pessoas; nao cite nomes de "
    "colaboradores; nao infira diagnosticos nem estado de saude individual; nao avalie desempenho "
    "de pessoas ou gestores; decisoes ficam com o RH."
)


def factor_catalog_text() -> str:
    """Catalogo de fatores no formato usado pelos prompts."""
    return "\n".join(f"- {f.value}: {desc}" for f, desc in FACTOR_CATALOG.items())


def nr1_references_text() -> str:
    """Trechos da NR-1 no formato usado pelos prompts."""
    return "\n".join(f"- {ref}" for ref in NR1_REFERENCES)
