"""Divisao de texto em trechos citaveis, preservando pagina e secao."""

import re
from dataclasses import dataclass

TAMANHO_ALVO = 1000
SOBREPOSICAO_MAX = 200
_TITULO_MD = re.compile(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$")


@dataclass(frozen=True)
class TrechoBruto:
    ordem: int
    texto: str
    pagina: int | None
    secao: str | None


def _eh_titulo(linha: str) -> str | None:
    """Titulo markdown ('# ...') ou linha curta sem pontuacao final, tipica de cabecalho."""
    marcado = _TITULO_MD.match(linha)
    if marcado:
        return marcado.group(1).strip()
    limpa = linha.strip()
    if 3 <= len(limpa) <= 80 and not limpa.endswith((".", ",", ";", ":")) and "  " not in limpa:
        palavras = limpa.split()
        if len(palavras) <= 10 and limpa[0].isupper() and not limpa.endswith("?"):
            return limpa
    return None


def _blocos(texto: str) -> list[tuple[str | None, str]]:
    """Paragrafos com a secao vigente em cada um."""
    secao: str | None = None
    blocos: list[tuple[str | None, str]] = []
    for paragrafo in re.split(r"\n\s*\n", texto.replace("\r\n", "\n")):
        linhas = [linha for linha in paragrafo.split("\n") if linha.strip()]
        if not linhas:
            continue
        if len(linhas) == 1 and _eh_titulo(linhas[0]):
            secao = _eh_titulo(linhas[0])
            continue
        if _TITULO_MD.match(linhas[0]):
            secao = _eh_titulo(linhas[0])
            linhas = linhas[1:]
            if not linhas:
                continue
        blocos.append((secao, " ".join(linha.strip() for linha in linhas)))
    return blocos


def _quebrar_longo(texto: str) -> list[str]:
    """Paragrafo maior que o alvo e quebrado por frases."""
    if len(texto) <= TAMANHO_ALVO:
        return [texto]
    partes, atual = [], ""
    for frase in re.split(r"(?<=[.!?;])\s+", texto):
        if atual and len(atual) + len(frase) + 1 > TAMANHO_ALVO:
            partes.append(atual)
            atual = frase
        else:
            atual = f"{atual} {frase}".strip()
    if atual:
        partes.append(atual)
    final: list[str] = []
    for parte in partes:  # frase gigante sem pontuacao
        final.extend(parte[i : i + TAMANHO_ALVO] for i in range(0, len(parte), TAMANHO_ALVO))
    return final


def dividir_em_trechos(paginas: list[tuple[int | None, str]]) -> list[TrechoBruto]:
    """paginas: [(numero_da_pagina ou None, texto)]. Trechos nunca atravessam pagina nem secao."""
    trechos: list[TrechoBruto] = []
    for pagina, texto in paginas:
        atual: list[str] = []
        secao_atual: str | None = None
        for secao, paragrafo in _blocos(texto):
            for pedaco in _quebrar_longo(paragrafo):
                tamanho = sum(len(p) + 1 for p in atual)
                if atual and (secao != secao_atual or tamanho + len(pedaco) > TAMANHO_ALVO):
                    trechos.append(TrechoBruto(len(trechos), " ".join(atual), pagina, secao_atual))
                    ultimo = atual[-1]
                    mesma_secao = secao == secao_atual
                    atual = [ultimo] if mesma_secao and len(ultimo) <= SOBREPOSICAO_MAX else []
                secao_atual = secao
                atual.append(pedaco)
        if atual:
            trechos.append(TrechoBruto(len(trechos), " ".join(atual), pagina, secao_atual))
    return trechos
