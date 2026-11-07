"""Classificacao e fatores de risco psicossocial conforme a Portaria MTE nº 1.419/2024 (NR-1)."""

from enum import Enum


class RiskLevel(str, Enum):
    """Nivel de intensidade e duracao do sinal de risco identificado pelo Pulso."""

    VERDE = "VERDE"  # Estavel ou sem desvios relevantes
    AMARELO = "AMARELO"  # Sinal de alerta moderado ou correlacao inicial
    VERMELHO = "VERMELHO"  # Sinal critico de alto risco / sobrecarga severa


class PsychosocialRiskFactor(str, Enum):
    """Fatores de risco psicossocial expressos na NR-1 (GRO/PGR).

    Exemplos normativos: sobrecarga e metas excessivas, jornadas longas, assedio moral e sexual,
    ma gestao e conflitos com lideranca, falta de clareza de papel, falta de autonomia e inseguranca.
    """

    SOBRECARGA_METAS = "SOBRECARGA_METAS"
    JORNADAS_LONGAS = "JORNADAS_LONGAS"
    LIDERANCA_CONFLITO = "LIDERANCA_CONFLITO"
    ASSEDIO = "ASSEDIO"
    FALTA_CLAREZA_PAPEL = "FALTA_CLAREZA_PAPEL"
    FALTA_AUTONOMIA = "FALTA_AUTONOMIA"
    INSEGURANCA_TRABALHO = "INSEGURANCA_TRABALHO"
    ESTAVEL_SEM_FATOR = "ESTAVEL_SEM_FATOR"
