"""Triagem deterministica antes da publicacao.

- Conteudo sensivel (bloqueia): CPF valido, codigo CID, documento clinico nominativo, segredos.
- Instrucoes suspeitas (nao bloqueia, marca o trecho): tentativas de prompt injection.
Os achados guardam so o CODIGO e a localizacao, nunca o valor encontrado.
"""

import re
import unicodedata
from dataclasses import dataclass

_CPF = re.compile(r"(?<!\d)(\d{3})\.?(\d{3})\.?(\d{3})-?(\d{2})(?!\d)")
_CID = re.compile(r"\b(?:cid(?:-?10)?\s*[:\-]?\s*)?([A-TV-Z]\d{2}(?:\.\d{1,2})?)\b")
_CID_CONTEXTO = re.compile(r"\bcid\b|\bf\d{2}(?:\.\d)?\b", re.IGNORECASE)
# Palavra-chave sem diferenciar maiusculas; o nome precisa comecar com maiuscula.
_CLINICO_NOMINATIVO = re.compile(
    r"\b(?i:atestado|laudo|prontuario|receituario|diagnostico)s?\s+(?i:medico\s+)?(?i:d[aoe]s?)\s+"
    r"(?:(?i:sr\.?|sra\.?|colaborador[a]?)\s+)?[A-Z][a-z]+",
)
_SEGREDOS = [
    ("SEGREDO_CHAVE_PRIVADA", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    (
        "SEGREDO_CHAVE_API",
        re.compile(r"\b(sk-[A-Za-z0-9_\-]{20,}|rc_[a-f0-9]{32,}|AKIA[0-9A-Z]{16})\b"),
    ),
    (
        "SEGREDO_CREDENCIAL",
        re.compile(r"\b(senha|password|token|api[_\-]?key|secret)\s*[:=]\s*\S{6,}", re.IGNORECASE),
    ),
]
_INJECAO = re.compile(
    r"(ignore|desconsidere|esqueca)\s+(as|todas\s+as|suas|quaisquer)?\s*(instruc|regras|orientac)"
    r"|voce\s+agora\s+(e|eh)\b|a\s+partir\s+de\s+agora\s+voce"
    r"|system\s*prompt|<\s*/?\s*system\s*>|\bassistant\s*:|\baja\s+como\b"
    r"|revele\s+(o|seu)\s+prompt",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Achado:
    codigo: str
    pagina: int | None


def _sem_acento(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")


def _cpf_valido(digitos: str) -> bool:
    if len(set(digitos)) == 1:
        return False
    for tamanho in (9, 10):
        soma = sum(int(d) * (tamanho + 1 - i) for i, d in enumerate(digitos[:tamanho]))
        if (soma * 10 % 11) % 10 != int(digitos[tamanho]):
            return False
    return True


def triar_conteudo_sensivel(paginas: list[tuple[int | None, str]]) -> list[Achado]:
    """Lista de achados (codigo + pagina). Lista vazia = pode seguir."""
    achados: set[Achado] = set()
    for pagina, texto in paginas:
        plano = _sem_acento(texto)
        for match in _CPF.finditer(plano):
            if _cpf_valido("".join(match.groups())):
                achados.add(Achado("CPF", pagina))
        if _CID_CONTEXTO.search(plano):
            for match in _CID.finditer(plano):
                codigo = match.group(1)
                if codigo.upper().startswith("F") or "cid" in match.group(0).lower():
                    achados.add(Achado("CODIGO_CID", pagina))
        if _CLINICO_NOMINATIVO.search(plano):
            achados.add(Achado("DOCUMENTO_CLINICO_NOMINATIVO", pagina))
        for codigo, padrao in _SEGREDOS:
            if padrao.search(texto):
                achados.add(Achado(codigo, pagina))
    return sorted(achados, key=lambda a: (a.codigo, a.pagina or 0))


def parece_injecao(texto: str) -> bool:
    return bool(_INJECAO.search(_sem_acento(texto)))
