"""Testes unitarios para a integracao com a API da Tako (customer-api.8arm.io)."""

from datetime import date
from unittest.mock import MagicMock, patch

from app.domain.entities.signals import AreaMonthlyMetrics
from app.infrastructure.integrations.tako import TakoApiClient, TakoSyncService
from app.infrastructure.repositories.in_memory_pulso_repositories import (
    InMemoryAreaRepository,
    InMemorySignalRepository,
)
from app.presentation.main import app


def test_tako_api_client_initialization() -> None:
    client = TakoApiClient(
        base_url="https://customer-api.8arm.io",
        organization_id="org_test_123",
        access_key="key_abc",
        access_secret="secret_xyz",
    )
    assert client.base_url == "https://customer-api.8arm.io"
    assert client.has_credentials is True


def test_tako_sync_service_aggregates_contracts_by_department() -> None:
    area_repo = InMemoryAreaRepository()
    signal_repo = InMemorySignalRepository()
    sync_service = TakoSyncService(
        area_repository=area_repo,
        signal_repository=signal_repo,
    )

    sample_contracts = [
        {"contractId": "c1", "department": "Atendimento ao Cliente", "status": "active"},
        {"contractId": "c2", "department": "Atendimento ao Cliente", "status": "active"},
        {"contractId": "c3", "department": "Atendimento ao Cliente", "status": "active"},
        {"contractId": "c4", "department": "Logística", "status": "active"},
        {"contractId": "c5", "department": "Logística", "status": "active"},
    ]

    areas = sync_service.sync_areas_and_headcount(sample_contracts=sample_contracts)
    assert len(areas) == 2

    atend = next(a for a in areas if a.name == "Atendimento ao Cliente")
    assert atend.headcount == 3

    log = next(a for a in areas if a.name == "Logística")
    assert log.headcount == 2


def test_tako_sync_service_calculates_monthly_metrics() -> None:
    area_repo = InMemoryAreaRepository()
    signal_repo = InMemorySignalRepository()
    sync_service = TakoSyncService(
        area_repository=area_repo,
        signal_repository=signal_repo,
    )

    # Cria as áreas
    sync_service.sync_areas_and_headcount(sample_contracts=[
        {"contractId": f"atend_{i}", "department": "Atendimento ao Cliente", "status": "active"} for i in range(10)
    ])

    sample_terminated = [
        {"contractId": "term_1", "department": "Atendimento ao Cliente", "status": "terminated"},
        {"contractId": "term_2", "department": "Atendimento ao Cliente", "status": "terminated"},
    ]

    metrics = sync_service.sync_monthly_metrics(
        competence_period=date(2026, 10, 1),
        sample_terminated=sample_terminated,
    )
    assert len(metrics) > 0
    atend_metric = next(m for m in metrics if "Atendimento" in m.id or "atend" in m.area_id)
    assert atend_metric.resignation_requests_count == 2
    assert atend_metric.turnover_rate == 20.0


def test_tako_webhook_processing() -> None:
    sync_service = TakoSyncService()

    msg_term = sync_service.process_webhook_payload({
        "payloadEvent": "eventTermination",
        "payloadContractId": "contract_123",
        "payloadEffectiveDate": "2026-10-15",
    })
    assert "Rescisão do contrato contract_123" in msg_term

    msg_adm = sync_service.process_webhook_payload({
        "payloadEvent": "eventAdmission",
        "payloadContractId": "contract_456",
        "payloadEffectiveDate": "2026-10-01",
    })
    assert "Admissão do contrato contract_456" in msg_adm

    msg_payslip = sync_service.process_webhook_payload({
        "payloadEvent": "eventPayslipAvailable",
        "payloadContractId": "contract_789",
    })
    assert "Holerite do contrato contract_789" in msg_payslip


def test_tako_endpoints_in_fastapi() -> None:
    # Testa via chamada de funcao ou TestClient se disponivel
    from app.presentation.api.v1.endpoints.tako import get_tako_status, sync_tako_data, receive_tako_webhook

    # 1. Status
    status_res = get_tako_status()
    assert status_res["service"] == "Tako Customer API Integration"
    assert "POST /api/v1/auth/token" in status_res["supported_endpoints"]

    # 2. Sync
    sync_res = sync_tako_data()
    assert sync_res["status"] == "success"
    assert sync_res["areas_synchronized"] > 0

    # 3. Webhook
    webhook_res = receive_tako_webhook({"event": "eventTermination", "contractId": "c_999"})
    assert webhook_res["status"] == "received"
