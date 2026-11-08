"""Relatorio PDF de riscos psicossociais (NR-1) da empresa, para o RH e o SESMT.

So dados agregados por area. Areas com menos de 5 pessoas aparecem como protegidas por quorum.
Sem nomes de gestores nem dados de saude individuais. Documento de apoio ao PGR: as decisoes
registradas sao do RH.
"""

from collections.abc import Iterable
from datetime import UTC, date, datetime
from typing import Any

from fpdf import FPDF
from sqlalchemy import text

from app.application.contracts.identity import ContextoAutorizado

QUORUM_MINIMO = 5
VIOLETA = (81, 34, 167)
TINTA = (23, 32, 51)
CINZA = (82, 96, 120)
LINHA = (225, 230, 239)
COR_NIVEL = {"VERMELHO": (190, 18, 60), "AMARELO": (146, 64, 14), "VERDE": (4, 120, 87)}
NOME_NIVEL = {"VERMELHO": "Atenção alta", "AMARELO": "Atenção moderada", "VERDE": "Estável"}
NOME_FATOR = {
    "SOBRECARGA_METAS": "Sobrecarga e metas",
    "JORNADAS_LONGAS": "Jornadas longas",
    "LIDERANCA_CONFLITO": "Conflito com a liderança",
    "ASSEDIO": "Assédio (compliance)",
    "FALTA_CLAREZA_PAPEL": "Falta de clareza de papel",
    "FALTA_AUTONOMIA": "Falta de autonomia",
    "INSEGURANCA_TRABALHO": "Insegurança no trabalho",
}
NOME_STATUS_CARD = {
    "ABERTO": "Aguardando decisão do RH",
    "APROVADO_PGR": "Aprovado e registrado no PGR",
    "AJUSTADO": "Ajustado pelo RH",
    "DESCARTADO": "Descartado com justificativa",
    "ESCALADO": "Encaminhado ao compliance",
}
NOME_STATUS_ACAO = {
    "PENDING": "aguardando aprovação",
    "QUEUED": "aprovada, na fila",
    "RUNNING": "em execução",
    "SUCCEEDED": "concluída",
    "FAILED": "falhou",
    "BLOCKED": "bloqueada",
    "UNKNOWN": "a conferir",
    "CANCELLED": "cancelada",
}


def _v(item: Any) -> str:
    return str(getattr(item, "value", item))


def _latin1(texto: Any) -> str:
    """As fontes padrao do PDF sao latin-1: troca o que nao cabe (aspas curvas, travessao...)."""
    s = str(texto if texto is not None else "")
    for a, b in {
        "–": "-",
        "—": "-",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "•": "-",
        "→": "->",
    }.items():
        s = s.replace(a, b)
    return s.encode("latin-1", "replace").decode("latin-1")


def _pct(valor: float | None) -> str:
    if valor is None:
        return "-"
    sinal = "+" if valor > 0 else ""
    return f"{sinal}{valor:.1f}%".replace(".", ",").replace(",0%", "%")


def _nota(valor: float | None) -> str:
    return "-" if valor is None else f"{valor:.1f}".replace(".", ",")


class _Pdf(FPDF):
    def __init__(self, empresa: str, gerado_em: datetime) -> None:
        super().__init__(format="A4")
        self.empresa, self.gerado_em = empresa, gerado_em
        self.set_auto_page_break(auto=True, margin=18)
        self.set_margins(16, 16, 16)
        self.alias_nb_pages()

    def header(self) -> None:
        if self.page_no() == 1:
            return
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(*VIOLETA)
        self.cell(
            0, 6, _latin1(f"VytAI · Relatório NR-1 · {self.empresa}"), new_x="LMARGIN", new_y="NEXT"
        )
        self.ln(2)

    def footer(self) -> None:
        self.set_y(-12)
        self.set_font("Helvetica", "", 7)
        self.set_text_color(*CINZA)
        self.cell(
            0,
            5,
            _latin1(
                f"Gerado em {self.gerado_em:%d/%m/%Y %H:%M} UTC · Dados agregados por área, sem "
                f"dados individuais · Página {self.page_no()}/{{nb}}"
            ),
            align="C",
        )

    def titulo(self, texto: str) -> None:
        self.ln(3)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(*TINTA)
        self.cell(0, 8, _latin1(texto), new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(*VIOLETA)
        self.set_line_width(0.6)
        self.line(self.l_margin, self.get_y(), self.l_margin + 24, self.get_y())
        self.ln(3)

    def paragrafo(
        self, texto: str, tamanho: float = 9.5, cor: tuple[int, int, int] = TINTA
    ) -> None:
        self.set_font("Helvetica", "", tamanho)
        self.set_text_color(*cor)
        self.multi_cell(0, 5, _latin1(texto), new_x="LMARGIN", new_y="NEXT")

    def rotulo_valor(self, rotulo: str, valor: str) -> None:
        self.set_font("Helvetica", "B", 9)
        self.set_text_color(*CINZA)
        self.multi_cell(0, 5, _latin1(rotulo), new_x="LMARGIN", new_y="NEXT")
        self.paragrafo(valor)
        self.ln(1)

    def tabela(
        self, cabecalho: list[str], linhas: Iterable[list[str]], larguras: list[float]
    ) -> None:
        self.set_font("Helvetica", "B", 8)
        self.set_fill_color(245, 246, 250)
        self.set_text_color(*CINZA)
        for titulo, largura in zip(cabecalho, larguras, strict=True):
            self.cell(largura, 7, _latin1(titulo), border="B", fill=True)
        self.ln()
        self.set_font("Helvetica", "", 8)
        self.set_text_color(*TINTA)
        self.set_draw_color(*LINHA)
        for linha in linhas:
            for valor, largura in zip(linha, larguras, strict=True):
                self.cell(largura, 7, _latin1(valor)[:60], border="B")
            self.ln()
        self.ln(2)

    def kpis(self, itens: list[tuple[str, str]]) -> None:
        largura = (self.w - self.l_margin - self.r_margin - 3 * 4) / 4
        y = self.get_y()
        for i, (numero, rotulo) in enumerate(itens):
            x = self.l_margin + i * (largura + 4)
            self.set_draw_color(*LINHA)
            self.rect(x, y, largura, 20)
            self.set_xy(x + 3, y + 3)
            self.set_font("Helvetica", "B", 15)
            self.set_text_color(*TINTA)
            self.cell(largura - 6, 7, _latin1(numero))
            self.set_xy(x + 3, y + 11)
            self.set_font("Helvetica", "", 7.5)
            self.set_text_color(*CINZA)
            self.multi_cell(largura - 6, 3.5, _latin1(rotulo))
        self.set_xy(self.l_margin, y + 24)


def _nome_empresa(container: Any, ctx: ContextoAutorizado) -> str:
    session = getattr(container, "session", None)
    if session is None:
        return "Empresa de demonstração"
    nome = session.execute(
        text("SELECT nome FROM empresa WHERE id=:id"), {"id": ctx.empresa_id}
    ).scalar_one_or_none()
    return str(nome or "Empresa")


def gerar_relatorio_pdf(
    ctx: ContextoAutorizado,
    container: Any,
    conhecimento: Any | None = None,
    acoes: Any | None = None,
    agora: datetime | None = None,
) -> bytes:
    agora = agora or datetime.now(UTC)
    empresa = _nome_empresa(container, ctx)
    areas = [a for a in container.area_repo.list_all() if getattr(a, "is_active", True)]
    cards = list(container.risk_card_repo.list_all())
    pgr = list(container.pgr_repo.list_all())
    card_por_area: dict[str, Any] = {}
    for card in sorted(cards, key=lambda c: c.created_at):
        card_por_area[card.area_id] = card
    abertos = [c for c in cards if _v(c.status) in ("ABERTO", "ESCALADO")]

    intervencoes: list[dict[str, Any]] = []
    if acoes is not None:
        for item in acoes.list_interventions():
            detalhe = acoes.intervention(item["id"])
            intervencoes.append(detalhe)
    documentos: list[Any] = []
    pendencias: list[Any] = []
    if conhecimento is not None:
        documentos = [d for d in conhecimento.servico.listar(ctx) if d.versao_publicada]
        pendencias = conhecimento.assistente.revisar_base(ctx, agora.date()).pendencias

    pdf = _Pdf(empresa, agora)
    pdf.add_page()

    # Capa
    pdf.set_fill_color(33, 20, 57)
    pdf.rect(0, 0, pdf.w, 62, style="F")
    pdf.set_xy(16, 16)
    pdf.set_font("Helvetica", "B", 9)
    pdf.set_text_color(198, 255, 51)
    pdf.cell(0, 5, "VYTAI · DIGITAL WORKER DE RH", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(255, 255, 255)
    pdf.set_x(16)
    pdf.cell(0, 11, _latin1("Relatório de riscos psicossociais"), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(229, 219, 247)
    pdf.set_x(16)
    pdf.cell(
        0,
        6,
        _latin1(f"{empresa} · NR-1 / GRO · {agora:%d/%m/%Y}"),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.set_y(70)

    vermelhos = sum(1 for c in abertos if _v(c.risk_level) == "VERMELHO")
    amarelos = sum(1 for c in abertos if _v(c.risk_level) == "AMARELO")
    pdf.kpis(
        [
            (str(len(areas)), "áreas acompanhadas"),
            (f"{vermelhos} / {amarelos}", "focos de atenção alta / moderada"),
            (str(len(pgr)), "medidas registradas no PGR"),
            (str(len(intervencoes)), "intervenções na fila do RH"),
        ]
    )
    pdf.paragrafo(
        "Este relatório reúne os sinais agregados por área (atestados, horas extras, pedidos de "
        "demissão e pesquisa de carga de trabalho), os focos de atenção abertos pelo VytAI, as "
        "medidas registradas no inventário do PGR e o que a empresa já oferece na base de "
        "conhecimento. Nenhuma informação individual é exibida, e áreas com menos de 5 pessoas "
        "têm os indicadores ocultos.",
        9,
        CINZA,
    )

    # Mapa por area
    pdf.titulo("1. Mapa de sinais por área")
    linhas = []
    for area in sorted(areas, key=lambda a: a.name):
        card = card_por_area.get(area.id)
        nivel = NOME_NIVEL.get(_v(card.risk_level), "-") if card else "Estável"
        if area.headcount < QUORUM_MINIMO:
            linhas.append(
                [area.name, "< 5", "oculto", "oculto", "oculto", "oculto", "Protegido por quórum"]
            )
            continue
        try:
            s = container.collect_signals_uc.execute(area.id)
        except Exception:  # noqa: BLE001 - area sem historico nao derruba o relatorio
            linhas.append([area.name, str(area.headcount), "-", "-", "-", "-", nivel])
            continue
        linhas.append(
            [
                area.name,
                str(area.headcount),
                _pct(s.variacao_dias_atestado_pct),
                _pct(s.variacao_horas_extras_pct),
                f"{s.pedidos_demissao_periodo} (média {_nota(s.media_empresa_pedidos_demissao)})",
                f"{_nota(s.nota_carga_trabalho_anterior)} -> {_nota(s.nota_carga_trabalho_atual)}",
                nivel,
            ]
        )
    pdf.tabela(
        ["Área", "Pessoas", "Atestados", "Horas extras", "Demissões", "Nota de carga", "Situação"],
        linhas,
        [40, 15, 20, 22, 28, 25, 28],
    )

    # Focos de atencao
    pdf.titulo("2. Focos de atenção")
    if not abertos:
        pdf.paragrafo("Nenhum foco de atenção aberto nesta data.")
    for card in sorted(abertos, key=lambda c: (_v(c.risk_level) != "VERMELHO", c.area_name)):
        nivel = _v(card.risk_level)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*COR_NIVEL.get(nivel, TINTA))
        pdf.cell(
            0,
            7,
            _latin1(f"{card.area_name} · {NOME_NIVEL.get(nivel, nivel)}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        fator = _v(card.probable_risk_factor)
        pdf.rotulo_valor("Fator de risco provável", NOME_FATOR.get(fator, fator))
        pdf.rotulo_valor("O que mudou", card.evidence_summary)
        if card.context_description:
            pdf.rotulo_valor("Contexto", card.context_description)
        pdf.rotulo_valor("Ação sugerida", card.suggested_action)
        pdf.rotulo_valor("Situação", NOME_STATUS_CARD.get(_v(card.status), _v(card.status)))
        pdf.ln(2)

    # PGR
    pdf.titulo("3. Inventário de riscos do PGR")
    if not pgr:
        pdf.paragrafo("Nenhuma medida registrada no PGR até esta data.")
    for item in pgr:
        fator = _v(item.factor)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*TINTA)
        pdf.cell(
            0,
            6,
            _latin1(f"{item.area_name} · {NOME_FATOR.get(fator, fator)}"),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        prazo = (
            item.deadline_date.strftime("%d/%m/%Y") if isinstance(item.deadline_date, date) else "-"
        )
        pdf.paragrafo(
            f"Medida: {item.action_plan_description}\nResponsável: {item.responsible_person} · "
            f"Prazo: {prazo} · Reavaliação: a cada {item.reassessment_interval_days} dias"
            + (" · Reaberto" if item.is_reopened else "")
        )
        pdf.ln(2)

    # Intervencoes
    pdf.titulo("4. Intervenções preparadas na fila do RH")
    if not intervencoes:
        pdf.paragrafo("Nenhuma intervenção na fila.")
    for item in intervencoes:
        estados = [
            NOME_STATUS_ACAO.get(a.get("status", ""), a.get("status", ""))
            for a in item.get("actions", [])
        ]
        criada = item.get("created_at")
        quando = criada.strftime("%d/%m/%Y") if isinstance(criada, datetime) else "-"
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(*TINTA)
        pdf.cell(0, 6, _latin1(str(item.get("title", ""))), new_x="LMARGIN", new_y="NEXT")
        pdf.paragrafo(
            f"Preparada em {quando}. Ações: {', '.join(estados) or 'nenhuma'}.", 8.5, CINZA
        )
        pdf.ln(1)

    # Base de conhecimento
    pdf.titulo("5. Base de conhecimento da empresa")
    if conhecimento is None:
        pdf.paragrafo("Base de conhecimento indisponível neste ambiente.")
    else:
        pdf.tabela(
            ["Documento publicado", "Categoria", "Versão"],
            [
                [d.titulo, _v(d.categoria).replace("_", " ").title(), d.versao_publicada.rotulo]
                for d in sorted(documentos, key=lambda d: d.titulo)
            ]
            or [["Nenhum documento publicado", "-", "-"]],
            [104, 54, 20],
        )
        if pendencias:
            pdf.rotulo_valor(
                "O que revisar na base", "\n".join(f"- {p.mensagem}" for p in pendencias)
            )
        else:
            pdf.paragrafo("Nenhuma pendência na base de conhecimento.", 9, CINZA)

    pdf.ln(4)
    pdf.paragrafo(
        "O VytAI prepara análises e propostas; as decisões e o registro no PGR são do RH. Este "
        "documento apoia o Gerenciamento de Riscos Ocupacionais (NR-1) e não substitui a "
        "avaliação do SESMT nem constitui diagnóstico de saúde.",
        8,
        CINZA,
    )
    return bytes(pdf.output())
