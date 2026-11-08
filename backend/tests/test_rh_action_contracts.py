from datetime import UTC, datetime, timedelta
from uuid import uuid4

import httpx
import pytest
from pydantic import ValidationError

from app.rh_actions.connectors import Connectors, ConnectorSettings, DeliveryError
from app.rh_actions.contracts import (
    CalendarPayload,
    ReminderPolicy,
    SlackPayload,
    TaskPayload,
    slack_text,
)


def settings(company):
    return ConnectorSettings(
        company,
        True,
        "test-token",
        frozenset({"C123456"}),
        "id",
        "secret",
        "refresh",
        frozenset({"rh@example.com"}),
        frozenset(),
    )


def test_dates_recurrence_and_destinations_are_bounded():
    with pytest.raises(ValidationError):
        TaskPayload(title="Revisar ação", dueAt="2026-11-20T10:00:00")
    with pytest.raises(ValidationError):
        ReminderPolicy(channel="C123456", maxReminders=4)
    now = datetime.now(UTC) + timedelta(days=1)
    with pytest.raises(ValidationError):
        CalendarPayload(
            calendarId="primary",
            startsAt=now,
            endsAt=now + timedelta(hours=1),
            timezone="invalid/zone",
        )
    with pytest.raises(ValidationError):
        SlackPayload(channel="https://example.com")


def test_slack_uses_exact_reviewed_text_and_receipt():
    company = uuid4()
    calls = []

    def handle(request):
        calls.append(request)
        return httpx.Response(200, json={"ok": True, "channel": "C123456", "ts": "123.456"})

    connector = Connectors(settings(company), httpx.Client(transport=httpx.MockTransport(handle)))
    action = uuid4()
    payload = SlackPayload(channel="C123456")
    result = connector.send(
        company, action, payload, "a" * 64, {"text": slack_text(payload, action)}
    )
    assert result["messageTs"] == "123.456"
    assert len(calls) == 1 and calls[0].url.host == "slack.com"
    assert b"objective" not in calls[0].content
    with pytest.raises(DeliveryError, match="CONNECTOR_DISABLED"):
        connector.send(uuid4(), action, payload, "a" * 64, {"text": "x"})
    assert len(calls) == 1


@pytest.mark.parametrize(
    "status,body,code,uncertain",
    [
        (503, {}, "SLACK_OUTCOME_UNKNOWN", True),
        (200, {"ok": False, "error": "invalid_auth"}, "SLACK_REJECTED", False),
        (429, {}, "SLACK_RATE_LIMITED", False),
    ],
)
def test_slack_never_assumes_delivery(status, body, code, uncertain):
    company = uuid4()
    client = httpx.Client(
        transport=httpx.MockTransport(lambda _: httpx.Response(status, json=body))
    )
    with pytest.raises(DeliveryError) as error:
        Connectors(settings(company), client).send(
            company, uuid4(), SlackPayload(channel="C123456"), "a" * 64, {"text": "Acompanhamento"}
        )
    assert error.value.code == code and error.value.uncertain == uncertain


def test_calendar_retry_finds_same_event_without_second_insert():
    company = uuid4()
    action = uuid4()
    calls = []
    stored = {}

    def handle(request):
        import json

        calls.append(request)
        if request.url.host == "oauth2.googleapis.com":
            return httpx.Response(200, json={"access_token": "test"})
        if request.method == "GET":
            return httpx.Response(200, json=stored) if stored else httpx.Response(404, json={})
        stored.update(json.loads(request.content))
        return httpx.Response(200, json=stored)

    connector = Connectors(settings(company), httpx.Client(transport=httpx.MockTransport(handle)))
    now = datetime.now(UTC) + timedelta(days=1)
    payload = CalendarPayload(
        calendarId="rh@example.com", startsAt=now, endsAt=now + timedelta(hours=1)
    )
    preview = {
        "summary": "Acompanhamento RH",
        "description": "Referência privada",
        "startsAt": now.isoformat(),
        "endsAt": payload.ends_at.isoformat(),
    }
    one = connector.send(company, action, payload, "a" * 64, preview)
    two = connector.send(company, action, payload, "a" * 64, preview)
    assert one == two
    assert len([r for r in calls if r.method == "POST" and r.url.host == "www.googleapis.com"]) == 1
