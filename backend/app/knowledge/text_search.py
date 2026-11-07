"""Ranking textual em portugues (BM25 com normalizacao leve).

Implementacao em Python usada nos testes e no repositorio em memoria. Em producao o
repositorio Postgres usa FTS ('portuguese' + unaccent); o contrato de retorno e o mesmo.
"""

import math
import re
import unicodedata
from collections import Counter
from collections.abc import Sequence

_STOPWORDS = frozenset(
    """a ao aos as ate com como da das de dela dele do dos e ela ele em entre era essa esse esta
    este eu foi ha isso isto ja la lhe mais mas me mesmo meu minha muito na nao nas nem no nos
    num numa o os ou para pela pelas pelo pelos por qual quando que quem se sem ser seu seus sua
    suas tambem te tem ter um uma umas uns voce voces sobre existe existem qual quais como esta
    estao sao foram tem temos tenho""".split()
)

# Expansao deterministica por fator de risco (o vocabulario dos documentos varia).
EXPANSAO_POR_FATOR: dict[str, tuple[str, ...]] = {
    "SOBRECARGA_METAS": ("carga", "metas", "jornada", "pausa", "ritmo", "acolhimento"),
    "JORNADAS_LONGAS": ("jornada", "horas extras", "pausa", "descanso", "banco de horas"),
    "LIDERANCA_CONFLITO": ("lideranca", "gestor", "conflito", "feedback", "mediacao"),
    "ASSEDIO": ("assedio", "denuncia", "canal", "compliance", "etica"),
    "FALTA_CLAREZA_PAPEL": ("papel", "responsabilidade", "atribuicao"),
    "FALTA_AUTONOMIA": ("autonomia", "decisao", "flexibilidade"),
    "INSEGURANCA_TRABALHO": ("mudanca", "reestruturacao", "comunicacao", "transicao"),
}


def normalizar(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    return sem_acento.lower()


def _radical(token: str) -> str:
    """Radical leve: tira plural simples e corta em 6 letras (aproxima o stemmer do Postgres)."""
    if len(token) > 4 and token.endswith("oes"):
        token = token[:-3] + "ao"
    elif len(token) > 3 and token.endswith("s"):
        token = token[:-1]
    return token[:6]


def termos(texto: str) -> list[str]:
    return [
        _radical(t)
        for t in re.findall(r"[a-z0-9]+", normalizar(texto))
        if t not in _STOPWORDS and len(t) > 1
    ]


def ranquear_bm25(
    consulta: Sequence[str], documentos: Sequence[Sequence[str]], k1: float = 1.2, b: float = 0.75
) -> list[float]:
    """Pontuacao BM25 de cada documento (lista de termos) para a consulta (lista de termos)."""
    if not documentos:
        return []
    n = len(documentos)
    media = sum(len(d) for d in documentos) / n or 1.0
    df: Counter[str] = Counter()
    for doc in documentos:
        df.update(set(doc))
    pontuacoes = []
    termos_consulta = set(consulta)
    for doc in documentos:
        freq = Counter(doc)
        total = 0.0
        for termo in termos_consulta:
            if termo not in freq:
                continue
            idf = math.log(1 + (n - df[termo] + 0.5) / (df[termo] + 0.5))
            tf = freq[termo]
            total += idf * tf * (k1 + 1) / (tf + k1 * (1 - b + b * len(doc) / media))
        pontuacoes.append(total)
    return pontuacoes
