"""Unit tests for system configuration."""

from backend.app.core.config import settings


def test_default_configuration():
    """Verify default business, timezone, currency, and locale settings."""
    assert settings.default_business_id == 1
    assert settings.default_timezone == "Asia/Tashkent"
    assert settings.default_currency == "UZS"
    assert "uz" in settings.supported_locales
    assert "ru" in settings.supported_locales
    assert "en" in settings.supported_locales


def test_guardrail_limits():
    """Verify deterministic safety guardrail defaults."""
    assert settings.max_tool_calls_per_turn == 5
    assert settings.max_context_window_turns == 10
    assert settings.max_output_tokens == 800
