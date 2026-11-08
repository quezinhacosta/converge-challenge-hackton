"""Servidor MCP do Pulso: as ferramentas chamam a API (aqui, via TestClient, sem rede)."""

from collections.abc import Iterator
from typing import Any

import pytest

pytest.importorskip("anyio")
pytest.importorskip("fastapi.testclient")
import anyio
from fastapi.testclient import TestClient

from app.presentation import mcp_server
from app.presentation.deps import PulsoAppContainer, get_container
from app.presentation.main import create_application


@pytest.fixture()
def api(monkeypatch: pytest.MonkeyPatch) -> Iterator[TestClient]:
    app = create_application()
    container = PulsoAppContainer()
    app.dependency_overrides[get_container] = lambda: container
    with TestClient(app) as client:

        def fake_request(
            method: str, url: str, json: Any = None, timeout: float = 0, headers: Any = None
        ) -> Any:
            path = url.replace("http://localhost:8000", "")
            return client.request(method, path, json=json, headers=headers)

        monkeypatch.setattr(mcp_server.httpx, "request", fake_request)
        yield client


def test_tools_are_registered() -> None:
    tools = anyio.run(mcp_server.mcp.list_tools)
    names = {t.name for t in tools}
    assert {
        "listar_areas",
        "status_area",
        "analisar_area",
        "rodar_fechamento",
        "listar_cards_abertos",
        "decidir_card",
        "inventario_pgr",
        "perguntar_ao_pulso",
    } <= names


def test_status_area_accepts_name_and_hides_small_groups(api: TestClient) -> None:
    assert mcp_server.status_area("Logistica")["areaId"] == "area_log"
    assert mcp_server.status_area("Design")["isAnonymized"] is True


def test_full_cycle_through_mcp(api: TestClient) -> None:
    analysis = mcp_server.analisar_area("Atendimento")
    assert analysis["riskLevel"] == "VERMELHO"

    with pytest.raises(mcp_server.PulsoApiError):
        mcp_server.decidir_card(analysis["cardId"], "APROVAR_PGR", "Juliana", False)

    item = mcp_server.decidir_card(analysis["cardId"], "APROVAR_PGR", "Juliana", True)
    assert item["factor"] == "SOBRECARGA_METAS"
    assert any(i["itemId"] == item["itemId"] for i in mcp_server.inventario_pgr())


def test_chat_refuses_individual_requests(api: TestClient) -> None:
    reply = mcp_server.perguntar_ao_pulso("A Carla tem faltado muito?")
    assert reply["isRefusal"] is True
