"""Servidor MCP do Pulso: expoe o digital worker como ferramentas para outros agentes.

Qualquer cliente MCP (Claude Desktop, MCP Inspector, o agente Otto da Tako, Copilot...) pode
consultar areas, rodar o fechamento, listar cards e registrar a decisao do RH.

O servidor nao guarda estado: ele chama a API REST do Pulso, entao tudo que um agente faz
por aqui aparece no painel web e no Slack (mesmo estado em memoria do backend).

Uso (a partir de backend/, com a API rodando em outra janela):
    python -m app.presentation.mcp_server                 # stdio (Claude Desktop, Inspector)
    python -m app.presentation.mcp_server --http          # streamable-http em 127.0.0.1:8765/mcp

Variaveis de ambiente:
    PULSO_API_URL  (padrao: http://localhost:8000/api/v1)
"""

import argparse
import logging
import os
from typing import Any

import httpx
from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError

logger = logging.getLogger("pulso.mcp")

API_URL = os.getenv("PULSO_API_URL", "http://localhost:8000/api/v1").rstrip("/")
TIMEOUT_SECONDS = float(os.getenv("PULSO_MCP_TIMEOUT", "120"))

INSTRUCTIONS = """Pulso e um analista digital de riscos psicossociais (NR-1) do RH.
Regras: trabalhe somente com AREAS, nunca com pessoas; areas com menos de 5 pessoas ficam
ocultas por LGPD; nenhuma decisao sobre o PGR e tomada sem confirmacao explicita de uma pessoa
do RH. Fluxo tipico: listar_areas -> rodar_fechamento ou analisar_area -> listar_cards_abertos
-> (o RH decide) -> decidir_card -> inventario_pgr."""

mcp = MCPServer(name="pulso", title="Pulso - Riscos Psicossociais NR-1", instructions=INSTRUCTIONS)


class PulsoApiError(ToolError):
    """Erro devolvido ao agente com a mensagem legivel (ToolError repassa o texto ao cliente)."""


def _request(method: str, path: str, payload: dict[str, Any] | None = None) -> Any:
    url = f"{API_URL}{path}"
    try:
        # Este processo stdio e de um unico principal. Nao compartilhar entre usuarios.
        headers = {}
        token = os.getenv("VYTAI_API_ACCESS_TOKEN")
        empresa = os.getenv("VYTAI_EMPRESA_ID")
        if token:
            headers["Authorization"] = f"Bearer {token}"
        if empresa:
            headers["X-Empresa-Id"] = empresa
        response = httpx.request(
            method, url, json=payload, headers=headers, timeout=TIMEOUT_SECONDS
        )
    except httpx.HTTPError as exc:
        raise PulsoApiError(
            f"API do Pulso indisponivel em {API_URL}. Inicie o backend (uvicorn). Detalhe: {exc}"
        ) from exc
    if response.status_code >= 400:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise PulsoApiError(f"API respondeu {response.status_code}: {detail}")
    return response.json()


def _resolve_area_id(area: str) -> str:
    """Aceita id ('area_log') ou nome ('Logistica')."""
    wanted = area.strip().lower()
    areas = _request("GET", "/areas")
    for item in areas:
        if wanted in {str(item["id"]).lower(), str(item["name"]).lower()}:
            return str(item["id"])
    for item in areas:
        if wanted and wanted in str(item["name"]).lower():
            return str(item["id"])
    raise PulsoApiError(f"Area '{area}' nao encontrada. Use listar_areas para ver as opcoes.")


@mcp.tool()
def listar_areas() -> list[dict[str, Any]]:
    """Lista as areas monitoradas com numero de pessoas e se os dados estao ocultos (LGPD)."""
    return [
        {
            "area_id": a["id"],
            "nome": a["name"],
            "pessoas": a["headcount"],
            "dados_ocultos_lgpd": a.get("isAnonymized", False),
        }
        for a in _request("GET", "/areas")
    ]


@mcp.tool()
def status_area(area: str) -> dict[str, Any]:
    """Indicadores agregados de uma area: variacao de atestados e horas extras, demissoes,
    nota de carga de trabalho e eventos de contexto. Aceita id ou nome da area.
    """
    return dict(_request("GET", f"/areas/{_resolve_area_id(area)}/signals"))


@mcp.tool()
def analisar_area(area: str) -> dict[str, Any]:
    """Roda o ciclo do Pulso numa area: compara com o historico, aponta o fator de risco da
    NR-1 e o nivel (VERDE/AMARELO/VERMELHO). Se for amarelo ou vermelho, abre um card para o RH
    (sem duplicar se ja houver um pendente). Pode levar alguns segundos (usa IA).
    """
    return dict(_request("POST", f"/areas/{_resolve_area_id(area)}/analyze"))


@mcp.tool()
def rodar_fechamento() -> list[dict[str, Any]]:
    """Fechamento da folha: analisa todas as areas e abre cards onde houver sinal de risco."""
    return list(_request("POST", "/fechamento"))


@mcp.tool()
def listar_cards_abertos() -> list[dict[str, Any]]:
    """Cards de atencao aguardando decisao do RH, com evidencias, contexto e acao sugerida."""
    return list(_request("GET", "/risk-cards/active"))


@mcp.tool()
def decidir_card(
    card_id: str,
    decisao: str,
    responsavel_rh: str,
    confirmado_pelo_rh: bool,
    texto_ajustado: str | None = None,
    justificativa: str | None = None,
    prazo_dias: int = 60,
) -> dict[str, Any]:
    """Registra a decisao HUMANA do RH sobre um card. So chame depois que uma pessoa do RH
    confirmar explicitamente a decisao nesta conversa.

    Args:
        card_id: Id do card (veja listar_cards_abertos).
        decisao: APROVAR_PGR, AJUSTAR_ACAO ou DESCARTAR.
        responsavel_rh: Nome de quem do RH tomou a decisao.
        confirmado_pelo_rh: Precisa ser true; confirma que a pessoa do RH aprovou.
        texto_ajustado: Obrigatorio em AJUSTAR_ACAO (a nova acao).
        justificativa: Obrigatoria em DESCARTAR.
        prazo_dias: Prazo de reavaliacao (15 a 180) para aprovar ou ajustar.
    """
    if not confirmado_pelo_rh:
        raise PulsoApiError(
            "Decisao nao registrada: confirme com a pessoa do RH e envie confirmado_pelo_rh=true."
        )
    payload = {
        "actionType": decisao.strip().upper(),
        "reviewerName": responsavel_rh,
        "adjustedActionText": texto_ajustado,
        "justificationNotes": justificativa,
        "deadlineDays": 0 if decisao.strip().upper() == "DESCARTAR" else prazo_dias,
    }
    return dict(_request("POST", f"/risk-cards/{card_id}/resolve", payload))


@mcp.tool()
def inventario_pgr() -> list[dict[str, Any]]:
    """Inventario de riscos psicossociais e plano de acao do PGR (NR-1), com rastro de auditoria."""
    return list(_request("GET", "/pgr/inventory"))


@mcp.tool()
def perguntar_ao_pulso(pergunta: str) -> dict[str, Any]:
    """Pergunta em linguagem natural ao agente do Pulso sobre areas (ex.: 'Como esta a
    Logistica?'). Pedidos sobre pessoas sao recusados pelo guardrail de LGPD.
    """
    return dict(
        _request(
            "POST",
            "/chat",
            {"userId": "mcp_client", "userName": "Agente via MCP", "queryText": pergunta},
        )
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Servidor MCP do Pulso")
    parser.add_argument("--http", action="store_true", help="usa streamable-http em vez de stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    if args.http and os.getenv("VYTAI_MODE", "production") != "demo":
        parser.error("MCP HTTP multiusuario requer transporte autenticado; use stdio por usuario.")

    # Em stdio, stdout e o canal do protocolo: logs vao para stderr.
    logging.basicConfig(level=logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    if args.http:
        mcp.run(transport="streamable-http", host=args.host, port=args.port)
    else:
        mcp.run()


if __name__ == "__main__":
    main()
