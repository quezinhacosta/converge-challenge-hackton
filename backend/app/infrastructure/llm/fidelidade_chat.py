"""Fidelidade da resposta do chat ao que as ferramentas devolveram nesta requisicao.

O modelo pode errar ou inventar numeros e conclusoes de ausencia. Antes de o RH ver a resposta:
- uma frase so fica se cada numero dela aparecer nos resultados das ferramentas desta conversa
  (ou na propria pergunta). Numero sem fonte remove a frase inteira;
- "a empresa nao possui/oferece ..." (canal, programa, politica...) vira "nao encontrei na base
  publicada": ausencia de resultado na busca nao prova que a empresa nao oferece.
Determinístico: nao depende do modelo seguir o prompt.
"""

import json
import re
from collections.abc import Iterable
from typing import Any

_NUMERO = re.compile(r"(?<![A-Za-z]-)(?<![A-Za-z])(?<!NR )\d+(?:[.,]\d+)?")
_FRASE = re.compile(r"(?<=[.!?])\s+")
_AUSENCIA = re.compile(
    r"\b(n[aã]o\s+(possui|tem|h[aá]|existe[m]?|oferece|disp[oõ]e|conta\s+com)|nenhum[a]?\s)",
    re.IGNORECASE,
)
_OFERTA = re.compile(
    r"\b(canal|canais|programa|apoio|pol[ií]tica|benef[ií]cio|procedimento|atendimento\s+psicol)",
    re.IGNORECASE,
)
FRASE_SEM_REGISTRO = (
    "Nao encontrei esse tema na base de conhecimento publicada; vale conferir em /conhecimento."
)
RESPOSTA_SEM_FONTE = (
    "Nao consegui confirmar os numeros desta resposta nas fontes consultadas. "
    "Confira os sinais da area no painel ou pergunte de novo."
)


def _normalizar(numero: str) -> str:
    try:
        return f"{float(numero.replace(',', '.')):g}"
    except ValueError:
        return numero


def numeros(texto: str) -> set[str]:
    return {_normalizar(n) for n in _NUMERO.findall(texto)}


def resultados_de_ferramentas(mensagens: Iterable[dict[str, Any]]) -> str:
    """Texto de todos os toolResult bem-sucedidos da conversa do agente (formato Strands)."""
    partes: list[str] = []
    for mensagem in mensagens:
        for bloco in mensagem.get("content", []) or []:
            resultado = bloco.get("toolResult") if isinstance(bloco, dict) else None
            if not resultado or resultado.get("status") == "error":
                continue
            for item in resultado.get("content", []) or []:
                if "text" in item:
                    partes.append(str(item["text"]))
                elif "json" in item:
                    partes.append(json.dumps(item["json"], ensure_ascii=False))
    return "\n".join(partes)


def aplicar_fidelidade(resposta: str, evidencias: str, pergunta: str = "") -> str:
    permitidos = numeros(evidencias) | numeros(pergunta)
    linhas_saida: list[str] = []
    removeu_por_numero = False
    ausencia_trocada = False
    for linha in resposta.splitlines():
        frases_ok: list[str] = []
        for frase in _FRASE.split(linha):
            if not frase.strip():
                continue
            if numeros(frase) - permitidos:
                removeu_por_numero = True
                continue
            if _AUSENCIA.search(frase) and _OFERTA.search(frase):
                if not ausencia_trocada:
                    frases_ok.append(FRASE_SEM_REGISTRO)
                    ausencia_trocada = True
                continue
            frases_ok.append(frase.strip())
        if frases_ok or not linha.strip():
            linhas_saida.append(" ".join(frases_ok))
    texto = "\n".join(linhas_saida).strip()
    texto = re.sub(r"\n{3,}", "\n\n", texto)
    if not texto or (removeu_por_numero and not numeros(texto) and len(texto) < 40):
        return RESPOSTA_SEM_FONTE
    return texto
