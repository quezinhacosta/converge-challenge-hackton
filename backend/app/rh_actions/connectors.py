"""Adaptadores reais com destinos fixos e credenciais do servidor; sem execucao no request de aprovacao."""

import os
from dataclasses import dataclass
from typing import Any
from urllib.parse import quote
from uuid import UUID

import httpx

from app.rh_actions.contracts import CalendarPayload, SlackPayload


class DeliveryError(Exception):
    def __init__(
        self, code: str, *, retryable: bool = False, uncertain: bool = False, delay: int = 30
    ):
        self.code, self.retryable, self.uncertain, self.delay = code, retryable, uncertain, delay
        super().__init__(code)  # Nunca incluir resposta bruta ou credencial no erro/log.


@dataclass(frozen=True)
class ConnectorSettings:
    empresa_id: UUID | None
    enabled: bool
    slack_token: str
    slack_channels: frozenset[str]
    google_client_id: str
    google_client_secret: str
    google_refresh_token: str
    google_calendars: frozenset[str]
    google_attendees: frozenset[str]

    @classmethod
    def from_env(cls) -> "ConnectorSettings":
        value = os.getenv("VYTAI_CONNECTOR_EMPRESA_ID", "")

        def items(name: str) -> frozenset[str]:
            return frozenset(x.strip() for x in os.getenv(name, "").split(",") if x.strip())

        return cls(
            UUID(value) if value else None,
            os.getenv("VYTAI_ACTIONS_EXTERNAL_ENABLED", "").lower() == "true",
            os.getenv("VYTAI_SLACK_BOT_TOKEN", ""),
            items("VYTAI_SLACK_ALLOWED_CHANNELS"),
            os.getenv("VYTAI_GOOGLE_CLIENT_ID", ""),
            os.getenv("VYTAI_GOOGLE_CLIENT_SECRET", ""),
            os.getenv("VYTAI_GOOGLE_REFRESH_TOKEN", ""),
            items("VYTAI_GOOGLE_ALLOWED_CALENDARS"),
            items("VYTAI_GOOGLE_ALLOWED_ATTENDEES"),
        )


class Connectors:
    def __init__(self, settings: ConnectorSettings, client: httpx.Client | None = None):
        self.settings = settings
        self.client = client or httpx.Client(timeout=15, follow_redirects=False)

    def close(self) -> None:
        self.client.close()

    def readiness(self, empresa_id: UUID) -> dict:
        match = self.settings.empresa_id == empresa_id
        return {
            "externalEnabled": self.settings.enabled and match,
            "slackConfigured": match
            and bool(self.settings.slack_token and self.settings.slack_channels),
            "calendarConfigured": match
            and bool(
                self.settings.google_client_id
                and self.settings.google_client_secret
                and self.settings.google_refresh_token
                and self.settings.google_calendars
            ),
            "slackChannels": sorted(self.settings.slack_channels) if match else [],
            "calendars": sorted(self.settings.google_calendars) if match else [],
            "allowedAttendees": sorted(self.settings.google_attendees) if match else [],
        }

    def send(
        self, empresa_id: UUID, action_id: UUID, payload: Any, fingerprint: str, preview: dict
    ) -> dict:
        if not self.settings.enabled or self.settings.empresa_id != empresa_id:
            raise DeliveryError("CONNECTOR_DISABLED")
        if isinstance(payload, SlackPayload):
            return self.slack(action_id, payload, preview)
        if isinstance(payload, CalendarPayload):
            return self.calendar(action_id, payload, fingerprint, preview)
        raise DeliveryError("UNSUPPORTED_ACTION")

    def slack(self, id: UUID, payload: SlackPayload, preview: dict) -> dict:
        if not self.settings.slack_token:
            raise DeliveryError("CONNECTOR_NOT_CONFIGURED")
        if payload.channel not in self.settings.slack_channels:
            raise DeliveryError("TARGET_NOT_ALLOWED")
        try:
            response = self.client.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": "Bearer " + self.settings.slack_token},
                json={
                    "channel": payload.channel,
                    "text": preview["text"],
                    "mrkdwn": False,
                    "parse": "none",
                    "unfurl_links": False,
                    "unfurl_media": False,
                },
            )
        except httpx.HTTPError:
            raise DeliveryError("SLACK_OUTCOME_UNKNOWN", uncertain=True) from None
        if response.status_code == 429:
            delay = (
                min(3600, max(1, int(response.headers.get("retry-after", "30"))))
                if response.headers.get("retry-after", "30").isdigit()
                else 30
            )
            raise DeliveryError("SLACK_RATE_LIMITED", retryable=True, delay=delay)
        if response.status_code >= 500:
            raise DeliveryError("SLACK_OUTCOME_UNKNOWN", uncertain=True)
        try:
            body = response.json()
        except ValueError:
            raise DeliveryError("SLACK_OUTCOME_UNKNOWN", uncertain=True) from None
        if (
            response.status_code == 200
            and body.get("ok") is True
            and body.get("ts")
            and body.get("channel") == payload.channel
        ):
            return {"provider": "SLACK", "channel": payload.channel, "messageTs": str(body["ts"])}
        if body.get("error") in {"ratelimited", "rate_limited"}:
            raise DeliveryError("SLACK_RATE_LIMITED", retryable=True)
        if response.status_code in {401, 403} or body.get("error") in {
            "invalid_auth",
            "token_revoked",
            "not_authed",
            "missing_scope",
            "channel_not_found",
            "not_in_channel",
            "is_archived",
            "restricted_action",
            "posting_to_channel_denied",
            "no_permission",
            "invalid_arguments",
            "msg_too_long",
        }:
            raise DeliveryError("SLACK_REJECTED")
        raise DeliveryError("SLACK_OUTCOME_UNKNOWN", uncertain=True)

    def calendar(self, id: UUID, payload: CalendarPayload, fingerprint: str, preview: dict) -> dict:
        s = self.settings
        if not all((s.google_client_id, s.google_client_secret, s.google_refresh_token)):
            raise DeliveryError("CONNECTOR_NOT_CONFIGURED")
        if (
            payload.calendar_id not in s.google_calendars
            or not set(payload.attendees) <= s.google_attendees
        ):
            raise DeliveryError("TARGET_NOT_ALLOWED")
        try:
            token = self.client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": s.google_client_id,
                    "client_secret": s.google_client_secret,
                    "refresh_token": s.google_refresh_token,
                    "grant_type": "refresh_token",
                },
            )
            if token.status_code != 200:
                raise DeliveryError(
                    "GOOGLE_AUTH_UNAVAILABLE",
                    retryable=token.status_code >= 500 or token.status_code == 429,
                )
            access = token.json().get("access_token")
            if not access:
                raise DeliveryError("GOOGLE_AUTH_UNAVAILABLE")
            headers = {"Authorization": "Bearer " + access}
            base = (
                "https://www.googleapis.com/calendar/v3/calendars/"
                + quote(payload.calendar_id, safe="")
                + "/events"
            )
            existing = self.client.get(base + "/" + id.hex, headers=headers)
            if existing.status_code == 200:
                return self._calendar_receipt(existing, id, fingerprint)
            if existing.status_code != 404:
                raise DeliveryError(
                    "CALENDAR_LOOKUP_FAILED",
                    retryable=existing.status_code in {429, 500, 502, 503, 504},
                )
            from datetime import UTC, datetime

            if payload.starts_at <= datetime.now(UTC):
                raise DeliveryError("EVENT_EXPIRED")
            result = self.client.post(
                base,
                headers=headers,
                params={"sendUpdates": "all" if payload.attendees else "none"},
                json={
                    "id": id.hex,
                    "summary": preview["summary"],
                    "description": preview["description"],
                    "visibility": "private",
                    "guestsCanModify": False,
                    "guestsCanInviteOthers": False,
                    "guestsCanSeeOtherGuests": False,
                    "start": {"dateTime": preview["startsAt"], "timeZone": payload.timezone},
                    "end": {"dateTime": preview["endsAt"], "timeZone": payload.timezone},
                    "attendees": [{"email": email} for email in payload.attendees],
                    "extendedProperties": {
                        "private": {"vytaiActionId": str(id), "vytaiDigest": fingerprint}
                    },
                },
            )
            if result.status_code in {200, 201}:
                return self._calendar_receipt(result, id, fingerprint)
            if result.status_code == 409:
                result = self.client.get(base + "/" + id.hex, headers=headers)
                if result.status_code == 200:
                    return self._calendar_receipt(result, id, fingerprint)
                raise DeliveryError("CALENDAR_CONFIRMATION_PENDING", retryable=True, uncertain=True)
            if result.status_code == 429:
                raise DeliveryError("CALENDAR_RATE_LIMITED", retryable=True)
            if result.status_code >= 500:
                raise DeliveryError("CALENDAR_CONFIRMATION_PENDING", retryable=True, uncertain=True)
            raise DeliveryError("CALENDAR_REJECTED")
        except (httpx.HTTPError, ValueError):
            # Repetir e seguro apenas com o mesmo event ID e verificacao dos metadados.
            raise DeliveryError(
                "CALENDAR_CONFIRMATION_PENDING", retryable=True, uncertain=True
            ) from None

    @staticmethod
    def _calendar_receipt(response: httpx.Response, id: UUID, fingerprint: str) -> dict:
        body = response.json()
        private = body.get("extendedProperties", {}).get("private", {})
        if (
            body.get("id") != id.hex
            or private.get("vytaiActionId") != str(id)
            or private.get("vytaiDigest") != fingerprint
            or body.get("status") == "cancelled"
        ):
            raise DeliveryError("CALENDAR_ID_CONFLICT", uncertain=True)
        return {"provider": "CALENDAR", "eventId": id.hex}
