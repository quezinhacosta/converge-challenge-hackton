from fastapi.testclient import TestClient

from app.presentation.main import create_application


def test_public_config_rejects_secret_keys(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://tvkvorzwjlivucubhwxu.supabase.co")
    client = TestClient(create_application())
    for key in ["sb_secret_do-not-expose", "service_role", ""]:
        monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", key)
        response = client.get("/api/v1/auth/config")
        assert response.status_code == 503
        assert key not in response.text if key else True
    monkeypatch.setenv("SUPABASE_PUBLISHABLE_KEY", "sb_publishable_test")
    assert client.get("/api/v1/auth/config").json()["publishableKey"] == "sb_publishable_test"


def test_legacy_anon_key_must_belong_to_project_and_never_service_role():
    import jwt

    from app.presentation.auth_api import is_public_key

    url = "https://tvkvorzwjlivucubhwxu.supabase.co"

    def token(role, ref="tvkvorzwjlivucubhwxu"):
        return jwt.encode(
            {"role": role, "ref": ref}, "unit-test-config-key-at-least-32-bytes", algorithm="HS256"
        )

    assert is_public_key(token("anon"), url)
    assert not is_public_key(token("service_role"), url)
    assert not is_public_key(token("anon", "anotherproject"), url)
    assert not is_public_key("malformed", url)
