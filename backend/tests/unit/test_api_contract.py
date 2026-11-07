"""Contrato da API com o frontend (camelCase) e regras da decisao do RH."""

from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from app.presentation.deps import PulsoAppContainer, get_container
from app.presentation.main import create_application


@pytest.fixture()
def client() -> Iterator[TestClient]:
    app = create_application()
    container = PulsoAppContainer()
    app.dependency_overrides[get_container] = lambda: container
    with TestClient(app) as test_client:
        yield test_client


def _open_card_for(client: TestClient, area_id: str) -> str:
    result = client.post(f"/api/v1/areas/{area_id}/analyze").json()
    assert result["cardId"], result
    return str(result["cardId"])


def test_areas_use_camel_case(client: TestClient) -> None:
    area = client.get("/api/v1/areas").json()[0]
    assert {"managerName", "isAnonymized"} <= set(area)


def test_active_cards_use_frontend_field_names(client: TestClient) -> None:
    _open_card_for(client, "area_atend")
    card = client.get("/api/v1/risk-cards/active").json()[0]
    assert {"cardId", "riskLevel", "oQueMudouUltimosMeses", "acaoSugerida"} <= set(card)


def test_resolve_accepts_frontend_payload_and_returns_pgr_names(client: TestClient) -> None:
    card_id = _open_card_for(client, "area_atend")
    inventory_before = len(client.get("/api/v1/pgr/inventory").json())
    response = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={"actionType": "APROVAR_PGR", "reviewerName": "Juliana Costa", "deadlineDays": 60},
    )
    assert response.status_code == 200, response.text
    item = response.json()
    assert item["factor"] == "SOBRECARGA_METAS"
    assert {"itemId", "severityLevel", "actionPlanDescription", "auditLog"} <= set(item)

    # Segundo clique (ou retry do Slack) nao cria outro item no PGR.
    again = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={"actionType": "APROVAR_PGR", "reviewerName": "Juliana Costa", "deadlineDays": 60},
    )
    assert again.status_code == 409
    assert len(client.get("/api/v1/pgr/inventory").json()) == inventory_before + 1


def test_escalated_harassment_card_cannot_enter_pgr(client: TestClient) -> None:
    result = client.post("/api/v1/areas/area_vend/analyze").json()
    response = client.post(
        f"/api/v1/risk-cards/{result['cardId']}/resolve",
        json={"actionType": "APROVAR_PGR", "reviewerName": "RH", "deadlineDays": 60},
    )
    assert response.status_code == 409


def test_decision_requirements_are_validated(client: TestClient) -> None:
    card_id = _open_card_for(client, "area_log")
    adjust_without_text = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={"actionType": "AJUSTAR_ACAO", "reviewerName": "RH", "deadlineDays": 60},
    )
    discard_without_reason = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={"actionType": "DESCARTAR", "reviewerName": "RH", "deadlineDays": 0},
    )
    typo = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={"actionType": "APROVAR", "reviewerName": "RH", "deadlineDays": 60},
    )
    assert adjust_without_text.status_code == 422
    assert discard_without_reason.status_code == 422
    assert typo.status_code == 422

    discard = client.post(
        f"/api/v1/risk-cards/{card_id}/resolve",
        json={
            "actionType": "DESCARTAR",
            "reviewerName": "RH",
            "deadlineDays": 0,
            "justificationNotes": "Validado com a gestao.",
        },
    )
    assert discard.status_code == 200, discard.text


def test_analyze_does_not_duplicate_cards(client: TestClient) -> None:
    first = client.post("/api/v1/areas/area_atend/analyze").json()
    second = client.post("/api/v1/areas/area_atend/analyze").json()
    assert first["cardStatus"] in {"CARD_ABERTO", "CARD_JA_EXISTENTE"}
    assert second["cardStatus"] == "CARD_JA_EXISTENTE"
    assert second["cardId"] == first["cardId"]
    active = [
        c for c in client.get("/api/v1/risk-cards/active").json() if c["areaId"] == "area_atend"
    ]
    assert len(active) == 1


def test_closing_cycle_respects_small_groups(client: TestClient) -> None:
    results = {r["areaId"]: r for r in client.post("/api/v1/fechamento").json()}
    assert results["area_des"]["isAnonymized"] is True
    assert results["area_des"]["cardStatus"] == "SEM_CARD"
    assert results["area_fin"]["riskLevel"] == "VERDE"


def test_chat_response_uses_camel_case(client: TestClient) -> None:
    reply = client.post(
        "/api/v1/chat",
        json={"user_id": "rh", "user_name": "RH", "query_text": "Me mostra os atestados da Carla"},
    ).json()
    assert reply["isRefusal"] is True
    assert "replyText" in reply
