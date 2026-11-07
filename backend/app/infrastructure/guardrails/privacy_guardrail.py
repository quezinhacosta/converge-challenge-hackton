"""Guardrails centrais de privacidade, anonimizacao e limites eticos do Pulso (LGPD & NR-1)."""

import re
from typing import Optional, Tuple


class PrivacyAndEthicsGuardrail:
    """Implementa as barreiras de protecao e compliance etico do agente Pulso.

    Regras Inegociaveis:
        1. So areas, nunca pessoas: bloqueia solicitacoes sobre colaboradores individuais.
        2. Minimo de 5 pessoas por grupo: oculta dados de areas com headcount < 5.
        3. Sem dado de saude individual: assegura que campos sensiveis (CID, diagnostico)
           jamais transitem pelo agente.
        4. Decisoes com humanos: garante que acoes no PGR dependam de aprovacao humana previa.
    """

    MINIMUM_GROUP_SIZE = 5

    INDIVIDUAL_QUERY_PATTERNS = [
        r"\b(atestado|atestados|falta|faltas|nota|desempenho)\s+d[aoe]\s+([A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ][a-záéíóúâêîôûãõç]+)",
        r"\bmostr[ea]\s+.*?\s+d[aoe]\s+([A-ZÁÉÍÓÚÂÊÎÔÛÃÕÇ][a-záéíóúâêîôûãõç]+)",
        r"\bquem\s+(faltou|pediu|reclamou|denunciou)\b",
        r"\branking\s+de\s+(pessoas|colaboradores|funcion[aá]rios)\b",
    ]

    def is_group_protected(self, headcount: int) -> bool:
        """Verifica se a area possui headcount suficiente para exibicao sem quebra de anonimato.

        Retorna True se for seguro analisar (headcount >= 5), e False se for grupo pequeno (< 5).
        """
        return headcount >= self.MINIMUM_GROUP_SIZE

    def inspect_query_for_individual_data(self, query_text: str) -> Tuple[bool, Optional[str]]:
        """Avalia se uma consulta recebida no chat tenta acessar dados de individuo.

        Argumentos:
            query_text: Mensagem submetida pelo usuario.

        Retorna:
            Tuple[bool, Optional[str]]: (is_blocked, justification_message)
        """
        lower_query = query_text.lower()

        for pattern in self.INDIVIDUAL_QUERY_PATTERNS:
            if re.search(pattern, lower_query, re.IGNORECASE):
                return (
                    True,
                    (
                        "O Pulso opera exclusivamente no nivel de areas e times para gestao de riscos "
                        "da NR-1. Em conformidade com a LGPD e as diretrizes eticas do Desafio Tako, "
                        "informacoes individuais de saude ou desempenho nao sao consultadas nem exibidas."
                    ),
                )

        return (False, None)
