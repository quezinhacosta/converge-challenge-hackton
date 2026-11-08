"""Upload .pdf/.txt/.md: tipo pelo conteudo, limites, PDF escaneado, triagem e rotas multipart."""

import io
from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient
from pypdf import PdfWriter

from app.knowledge import api
from app.knowledge.domain import CategoriaDocumento, ErroConhecimento, OrigemVersao, StatusVersao
from app.knowledge.dtos import (
    CadastroArquivoMetadados,
    ConsultaRecuperacao,
    NovaVersaoArquivoMetadados,
)
from app.knowledge.extraction import LIMITE_ARQUIVO_BYTES, validar_arquivo

from .fixtures import POLITICA_APOIO, Ambiente, ctx


def pdf_com_texto(*paginas: str) -> bytes:
    """PDF minimo valido, uma linha de texto (Helvetica) por pagina."""
    objetos: list[bytes] = []
    n = len(paginas)
    kids = " ".join(f"{3 + 2 * i} 0 R" for i in range(n))
    objetos.append(b"<< /Type /Catalog /Pages 2 0 R >>")
    objetos.append(f"<< /Type /Pages /Kids [{kids}] /Count {n} >>".encode())
    fonte = 3 + 2 * n
    for i, texto in enumerate(paginas):
        seguro = texto.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")
        stream = f"BT /F1 11 Tf 40 760 Td ({seguro}) Tj ET".encode("latin-1")
        objetos.append(
            f"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents {4 + 2 * i} 0 R "
            f"/Resources << /Font << /F1 {fonte} 0 R >> >> >>".encode()
        )
        objetos.append(b"<< /Length %d >>\nstream\n" % len(stream) + stream + b"\nendstream")
    objetos.append(b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>")
    saida = bytearray(b"%PDF-1.4\n")
    offsets = []
    for numero, corpo in enumerate(objetos, start=1):
        offsets.append(len(saida))
        saida += f"{numero} 0 obj\n".encode() + corpo + b"\nendobj\n"
    xref = len(saida)
    saida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    for off in offsets:
        saida += f"{off:010d} 00000 n \n".encode()
    saida += (
        f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n"
    ).encode()
    return bytes(saida)


def pdf_escaneado() -> bytes:
    escritor = PdfWriter()
    escritor.add_blank_page(width=612, height=792)
    buffer = io.BytesIO()
    escritor.write(buffer)
    return buffer.getvalue()


PAGINA_1 = "Programa Escuta: atendimento psicologico gratuito para colaboradores."
PAGINA_2 = "Agendamento pelo canal interno de apoio, de segunda a sexta."


def meta(**extra: object) -> CadastroArquivoMetadados:
    campos: dict[str, object] = {
        "titulo": "Programa Escuta (PDF)",
        "categoria": CategoriaDocumento.PROGRAMA_BENEFICIO,
        "responsavel": "RH Corporativo",
        "confirma_sem_dados_sensiveis": True,
    }
    campos.update(extra)
    return CadastroArquivoMetadados.model_validate(campos)


# -- extracao ------------------------------------------------------------------------------


def test_pdf_com_texto_vira_paginas_numeradas() -> None:
    arquivo = validar_arquivo("programa.pdf", pdf_com_texto(PAGINA_1, PAGINA_2))
    assert arquivo.formato == "PDF" and arquivo.mime == "application/pdf"
    assert [p for p, _ in arquivo.paginas] == [1, 2]
    assert "Programa Escuta" in arquivo.paginas[0][1]


def test_pdf_escaneado_e_recusado_sem_ocr() -> None:
    with pytest.raises(ErroConhecimento) as erro:
        validar_arquivo("escaneado.pdf", pdf_escaneado())
    assert erro.value.codigo == "SEM_TEXTO_EXTRAIVEL"


@pytest.mark.parametrize(
    ("nome", "conteudo", "codigo"),
    [
        ("planilha.xlsx", b"PK\x03\x04qualquer", "FORMATO_NAO_SUPORTADO"),
        ("falso.pdf", b"isto nao e um pdf de verdade, so texto comum", "ARQUIVO_CORROMPIDO"),
        ("disfarce.txt", b"PK\x03\x04conteudo zipado", "FORMATO_NAO_SUPORTADO"),
        ("binario.md", b"abc\x00\x01\x02" * 20, "FORMATO_NAO_SUPORTADO"),
        ("quebrado.pdf", b"%PDF-1.4\nlixo sem estrutura", "ARQUIVO_CORROMPIDO"),
        ("vazio.txt", b"", "TEXTO_VAZIO"),
        ("curto.txt", b"oi", "SEM_TEXTO_EXTRAIVEL"),
        ("grande.txt", b"a" * (LIMITE_ARQUIVO_BYTES + 1), "ARQUIVO_GRANDE"),
    ],
)
def test_arquivos_invalidos(nome: str, conteudo: bytes, codigo: str) -> None:
    with pytest.raises(ErroConhecimento) as erro:
        validar_arquivo(nome, conteudo)
    assert erro.value.codigo == codigo


def test_tipo_vem_do_conteudo_e_nome_e_limpo() -> None:
    arquivo = validar_arquivo("..\\..\\pasta/sem_extensao", pdf_com_texto(PAGINA_1))
    assert arquivo.formato == "PDF" and arquivo.nome == "sem_extensao"


def test_txt_em_cp1252_e_markdown() -> None:
    txt = validar_arquivo(
        "politica.txt", "Política de acolhimento e apoio psicológico.".encode("cp1252")
    )
    assert "Política" in txt.texto
    md = validar_arquivo("politica.md", POLITICA_APOIO.encode("utf-8"))
    assert md.formato == "TEXTO" and md.paginas[0][0] is None


# -- servico -------------------------------------------------------------------------------


def test_upload_pdf_processa_publica_e_cita_pagina() -> None:
    amb = Ambiente()
    doc = amb.servico.cadastrar_arquivo(
        ctx(), meta(), "programa.pdf", pdf_com_texto(PAGINA_1, PAGINA_2)
    )
    v1 = doc.versoes[0]
    assert v1.origem == OrigemVersao.UPLOAD and v1.status == StatusVersao.PRONTO
    assert v1.nome_arquivo == "programa.pdf" and v1.tamanho_bytes > 0
    amb.servico.publicar(ctx(), v1.id)
    r = amb.recuperador.buscar(ctx(), ConsultaRecuperacao(texto="agendamento canal de apoio"))
    assert r.evidencia_suficiente and r.trechos[0].pagina == 2

    # Falha simulada: reprocessar le de novo o original guardado e extrai o PDF outra vez.
    versao = amb.repo.obter_versao(ctx().empresa_id, v1.id)
    assert versao is not None
    versao.status, versao.publicada = StatusVersao.ERRO, False
    amb.repo.salvar_versao(versao)
    assert amb.servico.reprocessar(ctx(), v1.id).status == StatusVersao.PRONTO


def test_upload_exige_confirmacao_e_bloqueia_conteudo_sensivel() -> None:
    amb = Ambiente()
    with pytest.raises(ErroConhecimento) as erro:
        amb.servico.cadastrar_arquivo(
            ctx(), meta(confirma_sem_dados_sensiveis=False), "p.pdf", pdf_com_texto(PAGINA_1)
        )
    assert erro.value.codigo == "CONFIRMACAO_OBRIGATORIA"

    laudo = pdf_com_texto("Laudo do Joao Silva com afastamento de quinze dias por estresse.")
    doc = amb.servico.cadastrar_arquivo(ctx(), meta(titulo="Laudo"), "laudo.pdf", laudo)
    assert doc.versoes[0].status == StatusVersao.BLOQUEADO
    assert amb.armazenamento.ler(ctx().empresa_id, doc.versoes[0].id) is None
    assert list(amb.repo.todos_os_trechos()) == []


def test_upload_duplicado_do_texto_colado_e_nova_versao_por_arquivo() -> None:
    amb = Ambiente()
    from .fixtures import cadastro

    colado = amb.servico.cadastrar_texto(ctx(), cadastro(texto=POLITICA_APOIO))
    with pytest.raises(ErroConhecimento) as erro:
        amb.servico.cadastrar_arquivo(ctx(), meta(), "politica.md", POLITICA_APOIO.encode())
    assert erro.value.codigo == "DUPLICADO"

    doc = amb.servico.adicionar_versao_arquivo(
        ctx(),
        colado.id,
        NovaVersaoArquivoMetadados(confirma_sem_dados_sensiveis=True),
        "v2.pdf",
        pdf_com_texto(PAGINA_1, PAGINA_2),
    )
    assert [v.origem for v in doc.versoes] == [OrigemVersao.TEXTO, OrigemVersao.UPLOAD]


# -- rotas ---------------------------------------------------------------------------------


@pytest.fixture()
def cliente() -> Iterator[TestClient]:
    from app.knowledge.integration import fabrica_em_memoria
    from app.presentation.knowledge_integration import KnowledgeIntegration
    from app.presentation.main import create_application
    from app.presentation.security import request_session, require_authorized_context

    app = create_application(KnowledgeIntegration(router=api.router, factory=fabrica_em_memoria()))
    app.dependency_overrides[require_authorized_context] = lambda: ctx()
    app.dependency_overrides[request_session] = lambda: None
    with TestClient(app) as c:
        yield c


FORM = {
    "titulo": "Programa Escuta",
    "categoria": "PROGRAMA_BENEFICIO",
    "responsavel": "RH Corporativo",
    "vigenciaInicio": "2026-01-01",
    "confirmaSemDadosSensiveis": "true",
}
URL = "/api/v1/conhecimento"


def test_rota_upload_e_nova_versao(cliente: TestClient) -> None:
    r = cliente.post(
        f"{URL}/documentos/arquivo",
        data=FORM,
        files={"arquivo": ("programa.pdf", pdf_com_texto(PAGINA_1, PAGINA_2), "application/pdf")},
    )
    assert r.status_code == 201, r.text
    corpo = r.json()
    assert corpo["versoes"][0]["origem"] == "UPLOAD"
    assert corpo["versoes"][0]["nomeArquivo"] == "programa.pdf"

    r2 = cliente.post(
        f"{URL}/documentos/{corpo['id']}/versoes/arquivo",
        data={"confirmaSemDadosSensiveis": "true", "rotuloVersao": "2026.2"},
        files={"arquivo": ("v2.md", POLITICA_APOIO.encode(), "text/markdown")},
    )
    assert r2.status_code == 201, r2.text
    assert r2.json()["versoes"][1]["rotulo"] == "2026.2"


def test_rota_upload_erros_padronizados(cliente: TestClient) -> None:
    escaneado = cliente.post(
        f"{URL}/documentos/arquivo",
        data=FORM,
        files={"arquivo": ("scan.pdf", pdf_escaneado(), "application/pdf")},
    )
    assert escaneado.status_code == 422
    assert escaneado.json()["detail"]["codigo"] == "SEM_TEXTO_EXTRAIVEL"

    docx = cliente.post(
        f"{URL}/documentos/arquivo",
        data=FORM,
        files={"arquivo": ("p.docx", b"PK\x03\x04...", "application/pdf")},  # mime mentiroso
    )
    assert docx.status_code == 415

    grande = cliente.post(
        f"{URL}/documentos/arquivo",
        data=FORM,
        files={"arquivo": ("g.txt", b"a" * (LIMITE_ARQUIVO_BYTES + 10), "text/plain")},
    )
    assert grande.status_code == 413 and grande.json()["detail"]["codigo"] == "ARQUIVO_GRANDE"

    sem_categoria = cliente.post(
        f"{URL}/documentos/arquivo",
        data=FORM | {"categoria": "INEXISTENTE"},
        files={"arquivo": ("p.pdf", pdf_com_texto(PAGINA_1), "application/pdf")},
    )
    assert sem_categoria.status_code == 422
    assert sem_categoria.json()["detail"]["codigo"] == "METADADOS_INVALIDOS"
