from app import ai_provider
from app.arn_generator import generate_arn
from app.main import DEFAULT_CORS_ORIGINS, get_allowed_origins


def test_arn_generator_uses_environment_context(monkeypatch):
    monkeypatch.setenv("AWS_REGION", "eu-west-1")
    monkeypatch.setenv("AWS_ACCOUNT_ID", "999999999999")

    assert generate_arn("dynamodb", "clients") == (
        "arn:aws:dynamodb:eu-west-1:999999999999:table/clients"
    )


def test_cors_origins_can_be_configured(monkeypatch):
    monkeypatch.setenv(
        "CORS_ALLOWED_ORIGINS",
        "https://consciencenumerique.com, https://www.consciencenumerique.com",
    )

    assert get_allowed_origins() == [
        "https://consciencenumerique.com",
        "https://www.consciencenumerique.com",
    ]


def test_cors_origins_keep_local_defaults_without_configuration(monkeypatch):
    monkeypatch.delenv("CORS_ALLOWED_ORIGINS", raising=False)

    assert get_allowed_origins() == DEFAULT_CORS_ORIGINS


def test_ai_limits_have_safe_bounds(monkeypatch):
    monkeypatch.setenv("AI_MAX_TOKENS", "5000")
    monkeypatch.setenv("AI_TIMEOUT_SECONDS", "500")

    assert ai_provider.get_ai_max_tokens() == 500
    assert ai_provider.get_ai_timeout_seconds() == 60.0
