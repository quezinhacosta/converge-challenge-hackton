"""Guardrails centrais de privacidade, anonimizacao e limites eticos do Pulso (LGPD & NR-1).

Defesa em camadas para perguntas sobre pessoas:
    1. Este filtro deterministico recusa o pedido antes de chegar ao LLM.
    2. O prompt do agente de chat manda recusar pedidos individuais.
    3. As ferramentas do agente so devolvem dados agregados por area (minimo de 5 pessoas),
       entao nao existe dado individual para vazar mesmo que 1 e 2 falhem.
"""

import re
import unicodedata
from collections.abc import Iterable


def _fold(text: str) -> str:
    """Minusculas e sem acentos, para comparar palavras."""
    stripped = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode("ascii")
    return stripped.lower()


# Termos que, ligados a uma pessoa, viram dado individual sensivel.
_SENSITIVE_TERM = re.compile(
    r"\b(atestad\w*|falt\w*|afast\w*|doen\w*|cid|diagnost\w*|desempenh\w*|salari\w*|"
    r"demiss\w*|demit\w*|denunci\w*|licenc\w*|nota|notas|avaliac\w*)\b"
)
# "<termo> da/do/de <palavra>" (ex.: "atestados da carla").
_TERM_OF_WORD = re.compile(
    r"\b(atestad\w*|falt\w*|afast\w*|desempenh\w*|salari\w*|nota|notas|avaliac\w*|cid)"
    r"\s+d[aoe]s?\s+([a-z]+)"
)
_ALWAYS_BLOCK = [
    re.compile(r"\bquem\s+(faltou|falta|pediu|reclamou|denunciou|se afastou|esta afastad\w*)\b"),
    re.compile(r"\branking\s+d[aoe]s?\s+(pessoas|colaborador\w*|funcionari\w*)\b"),
    re.compile(
        r"\b(funcionari[oa]s?|colaborador[a]?|pessoa)\s+(chamad[oa]\s+)?[a-z]+\s+(tem|teve|esta)\b"
    ),
    re.compile(r"\b(cpf|matricula)\b"),
]

# Palavras comuns que aparecem depois de "falta de", "nota de", etc. em perguntas sobre areas.
_COMMON_WORDS = {
    "pessoal",
    "equipe",
    "equipes",
    "time",
    "times",
    "area",
    "areas",
    "setor",
    "setores",
    "gente",
    "apoio",
    "comunicacao",
    "recursos",
    "tempo",
    "clareza",
    "autonomia",
    "lideranca",
    "gestao",
    "carga",
    "trabalho",
    "clima",
    "atestado",
    "atestados",
    "pessoas",
    "colaboradores",
    "hoje",
    "ontem",
    "mes",
    "semana",
    "empresa",
    "estrutura",
    "treinamento",
    "material",
    "insumos",
}
# Palavras com inicial maiuscula que nao sao nomes de pessoas.
_NON_PERSON_CAPS = {
    "a",
    "o",
    "as",
    "os",
    "e",
    "me",
    "mostra",
    "mostre",
    "quero",
    "qual",
    "quais",
    "como",
    "quantos",
    "quantas",
    "ha",
    "existe",
    "pulso",
    "rh",
    "nr",
    "nr-1",
    "lgpd",
    "pgr",
    "sesmt",
    "cipa",
    "pcmso",
    "dp",
    "janeiro",
    "fevereiro",
    "marco",
    "abril",
    "maio",
    "junho",
    "julho",
    "agosto",
    "setembro",
    "outubro",
    "novembro",
    "dezembro",
    "atendimento",
    "cliente",
    "logistica",
    "vendas",
    "financeiro",
    "design",
    "produto",
    "engenharia",
    "software",
    "recursos",
    "humanos",
}

REFUSAL_MESSAGE = (
    "O Pulso opera exclusivamente no nivel de areas e times para gestao de riscos "
    "da NR-1. Em conformidade com a LGPD e as diretrizes eticas do Desafio Tako, "
    "informacoes individuais de saude ou desempenho nao sao consultadas nem exibidas."
)


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

    def __init__(self, known_area_terms: Iterable[str] = ()) -> None:
        """known_area_terms: nomes de areas da empresa, para nao confundir area com pessoa."""
        self._allowed = set(_COMMON_WORDS) | set(_NON_PERSON_CAPS)
        for term in known_area_terms:
            self._allowed.update(_fold(term).split())

    def is_group_protected(self, headcount: int) -> bool:
        """Verifica se a area possui headcount suficiente para exibicao sem quebra de anonimato.

        Retorna True se for seguro analisar (headcount >= 5), e False se for grupo pequeno (< 5).
        """
        return headcount >= self.MINIMUM_GROUP_SIZE

    def _mentions_unknown_capitalized_name(self, query_text: str) -> bool:
        words = re.findall(r"[A-Za-zÀ-ÿ][\wÀ-ÿ-]*", query_text)
        for index, word in enumerate(words):
            if index == 0 or not word[0].isupper():
                continue
            if _fold(word) not in self._allowed:
                return True
        return False

    def inspect_query_for_individual_data(self, query_text: str) -> tuple[bool, str | None]:
        """Avalia se uma consulta recebida no chat tenta acessar dados de individuo.

        Retorna:
            Tuple[bool, Optional[str]]: (is_blocked, justification_message)
        """
        folded = _fold(query_text)

        if any(pattern.search(folded) for pattern in _ALWAYS_BLOCK):
            return True, REFUSAL_MESSAGE

        if _SENSITIVE_TERM.search(folded):
            if self._mentions_unknown_capitalized_name(query_text):
                return True, REFUSAL_MESSAGE
            for match in _TERM_OF_WORD.finditer(folded):
                if match.group(2) not in self._allowed:
                    return True, REFUSAL_MESSAGE

        return False, None
