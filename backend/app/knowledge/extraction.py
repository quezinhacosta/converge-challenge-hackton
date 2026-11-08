"""Validacao e extracao de texto de arquivos enviados (.txt, .md, .pdf).

O tipo vem do conteudo (assinatura), nao do nome ou do Content-Type informado pelo cliente.
Limites protegem o servidor de arquivos grandes, PDFs com milhares de paginas e PDFs que
travam o parser. PDF escaneado (sem camada de texto) nao passa: nao ha OCR no MVP.
"""

import io
import time
from dataclasses import dataclass
from typing import Literal

from app.knowledge.domain import ErroConhecimento

LIMITE_ARQUIVO_BYTES = 10 * 1024 * 1024  # igual ao CHECK de documento_arquivo
LIMITE_PAGINAS_PDF = 300
LIMITE_CARACTERES_EXTRAIDOS = 500_000  # igual ao limite do texto colado
LIMITE_SEGUNDOS_PDF = 20.0
MINIMO_CARACTERES_UTEIS = 40

Formato = Literal["PDF", "TEXTO"]
EXTENSOES = {".pdf": "PDF", ".txt": "TEXTO", ".md": "TEXTO", ".markdown": "TEXTO"}
MIME_POR_FORMATO = {"PDF": "application/pdf", "TEXTO": "text/plain"}


@dataclass(frozen=True)
class ArquivoValidado:
    formato: Formato
    mime: str
    nome: str
    paginas: list[tuple[int | None, str]]

    @property
    def texto(self) -> str:
        return "\n\n".join(t for _, t in self.paginas)


def _nome_seguro(nome: str | None) -> str:
    base = (nome or "documento").replace("\\", "/").rsplit("/", 1)[-1].strip()
    base = "".join(c for c in base if c.isprintable() and c not in '<>:"|?*')
    return base[:120] or "documento"


def _extensao(nome: str) -> str:
    return "." + nome.rsplit(".", 1)[-1].lower() if "." in nome else ""


def detectar_formato(nome: str, conteudo: bytes) -> Formato:
    if conteudo[:5] == b"%PDF-":
        return "PDF"
    esperado = EXTENSOES.get(_extensao(nome))
    if esperado == "PDF":
        raise ErroConhecimento("ARQUIVO_CORROMPIDO", "O arquivo nao e um PDF valido.")
    if esperado is None:
        raise ErroConhecimento(
            "FORMATO_NAO_SUPORTADO", "Envie .pdf, .txt ou .md (Word e imagens nao sao aceitos)."
        )
    # Texto: rejeita binarios disfarcados (zip/docx, imagens, executaveis).
    if (
        b"\x00" in conteudo[:8192]
        or conteudo[:2] in (b"PK", b"MZ")
        or conteudo[:3] == b"\xff\xd8\xff"
    ):
        raise ErroConhecimento(
            "FORMATO_NAO_SUPORTADO", "O conteudo nao e texto. Envie .pdf, .txt ou .md."
        )
    return "TEXTO"


def _decodificar_texto(conteudo: bytes) -> str:
    for codificacao in ("utf-8-sig", "cp1252"):
        try:
            return conteudo.decode(codificacao)
        except UnicodeDecodeError:
            continue
    raise ErroConhecimento("ARQUIVO_CORROMPIDO", "Nao foi possivel ler o texto (codificacao).")


def _extrair_pdf(conteudo: bytes) -> list[tuple[int | None, str]]:
    from pypdf import PdfReader
    from pypdf.errors import PdfReadError

    try:
        leitor = PdfReader(io.BytesIO(conteudo))
        if leitor.is_encrypted:
            raise ErroConhecimento(
                "ARQUIVO_CORROMPIDO", "PDF protegido por senha. Envie uma copia sem protecao."
            )
        total = len(leitor.pages)
    except ErroConhecimento:
        raise
    except (PdfReadError, ValueError, KeyError, TypeError, OSError) as erro:
        raise ErroConhecimento("ARQUIVO_CORROMPIDO", "O PDF esta corrompido ou ilegivel.") from erro
    if total > LIMITE_PAGINAS_PDF:
        raise ErroConhecimento(
            "TEXTO_MUITO_LONGO",
            f"O PDF tem {total} paginas; o limite e {LIMITE_PAGINAS_PDF}. Divida o documento.",
        )
    inicio = time.monotonic()
    paginas: list[tuple[int | None, str]] = []
    caracteres = 0
    for numero, pagina in enumerate(leitor.pages, start=1):
        if time.monotonic() - inicio > LIMITE_SEGUNDOS_PDF:
            raise ErroConhecimento(
                "ARQUIVO_CORROMPIDO",
                "O PDF demorou demais para ser lido. Tente exporta-lo de novo.",
            )
        try:
            texto = pagina.extract_text() or ""
        except Exception as erro:  # noqa: BLE001 - pagina malformada
            raise ErroConhecimento(
                "ARQUIVO_CORROMPIDO", f"Nao foi possivel ler a pagina {numero} do PDF."
            ) from erro
        caracteres += len(texto)
        if caracteres > LIMITE_CARACTERES_EXTRAIDOS:
            raise ErroConhecimento(
                "TEXTO_MUITO_LONGO",
                f"O PDF passa de {LIMITE_CARACTERES_EXTRAIDOS} caracteres. Divida o documento.",
            )
        if texto.strip():
            paginas.append((numero, texto))
    return paginas


def extrair(formato: Formato, conteudo: bytes) -> list[tuple[int | None, str]]:
    """Paginas (numero, texto). Usado no upload e de novo no processamento/reprocessamento."""
    if formato == "PDF":
        paginas = _extrair_pdf(conteudo)
    else:
        texto = _decodificar_texto(conteudo).replace("\r\n", "\n")
        if len(texto) > LIMITE_CARACTERES_EXTRAIDOS:
            raise ErroConhecimento(
                "TEXTO_MUITO_LONGO",
                f"O texto passa de {LIMITE_CARACTERES_EXTRAIDOS} caracteres. Divida o documento.",
            )
        paginas = [(None, texto)] if texto.strip() else []
    if sum(len(t.strip()) for _, t in paginas) < MINIMO_CARACTERES_UTEIS:
        raise ErroConhecimento(
            "SEM_TEXTO_EXTRAIVEL",
            "Nao ha texto legivel no arquivo (PDF escaneado ou vazio). Envie um PDF com texto "
            "selecionavel ou cole o conteudo.",
        )
    return paginas


def validar_arquivo(nome: str | None, conteudo: bytes) -> ArquivoValidado:
    if len(conteudo) > LIMITE_ARQUIVO_BYTES:
        raise ErroConhecimento("ARQUIVO_GRANDE", "O arquivo passa de 10 MB.")
    if not conteudo:
        raise ErroConhecimento("TEXTO_VAZIO", "O arquivo esta vazio.")
    nome_limpo = _nome_seguro(nome)
    formato = detectar_formato(nome_limpo, conteudo)
    return ArquivoValidado(
        formato, MIME_POR_FORMATO[formato], nome_limpo, extrair(formato, conteudo)
    )


def formato_do_mime(mime: str | None) -> Formato:
    return "PDF" if mime == "application/pdf" else "TEXTO"
