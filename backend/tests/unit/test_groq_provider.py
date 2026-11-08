import json

import httpx
import pytest

from app.infrastructure.llm.resilience.failover_manager import FailoverManager
from app.infrastructure.llm.resilience.groq_provider import GroqProvider


class Unavailable:
    name = "primary"

    def is_available(self):
        return False


@pytest.fixture(autouse=True)
def allow_mock_groq(monkeypatch):
    monkeypatch.setenv("PULSO_LLM_ENABLED", "true")


def provider(response):
    return GroqProvider(
        api_key="unit-test-secret",
        client=httpx.Client(transport=httpx.MockTransport(lambda request: response(request))),
    )


def test_groq_returns_structured_assessment_without_changing_factor():
    requests = []

    def handle(request):
        requests.append(request)
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": json.dumps(
                                {
                                    "hypothesis": "Hipótese para conferir com o RH",
                                    "action": "Revisar organização do trabalho",
                                }
                            )
                        }
                    }
                ]
            },
        )

    p = provider(handle)
    result = p.generate_hypothesis_and_action(
        "Equipe", "Horas extras +20%", [], "score transparente", "JORNADAS_LONGAS"
    )
    assert result[1] == "Revisar organização do trabalho"
    body = json.loads(requests[0].content)
    assert body["response_format"] == {"type": "json_object"}
    assert requests[0].url.host == "api.groq.com"
    assert "JORNADAS_LONGAS" in body["messages"][1]["content"]


@pytest.mark.parametrize(
    "response",
    [
        httpx.Response(429, json={"error": "private response"}),
        httpx.Response(200, json={"choices": []}),
        httpx.Response(200, json={"choices": [{"message": {"content": "not json"}}]}),
    ],
)
def test_groq_failure_is_safe_and_does_not_log_credentials(response):
    p = provider(lambda _: response)
    with pytest.raises(RuntimeError) as error:
        p.generate_hypothesis_and_action("Equipe", "", [], "", "SOBRECARGA_METAS")
    assert "unit-test-secret" not in str(error.value) and "private response" not in str(error.value)


def test_failover_chat_uses_groq_secondary_before_rules():
    p = provider(
        lambda _: httpx.Response(
            200, json={"choices": [{"message": {"content": "Informação agregada para revisão."}}]}
        )
    )
    text, metadata = FailoverManager(
        primary_provider=Unavailable(), secondary_provider=p
    ).generate_chat_reply("Resumo", {})
    assert (
        text == "Informação agregada para revisão."
        and metadata.provider_used.startswith("groq-")
        and metadata.fallback_triggered
    )


def test_groq_respects_disabled_llm(monkeypatch):
    monkeypatch.setenv("PULSO_LLM_ENABLED", "false")
    assert not GroqProvider(api_key="unit-test").is_available()
