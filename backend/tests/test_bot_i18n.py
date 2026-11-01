"""Unit tests for bot internationalization (i18n)."""

from backend.app.bot.i18n import MESSAGES, get_text


def test_i18n_all_languages_defined():
    """Verify supported language dictionaries exist."""
    assert "uz" in MESSAGES
    assert "ru" in MESSAGES
    assert "en" in MESSAGES
    assert "uz_cyrl" in MESSAGES


def test_i18n_welcome_interpolation():
    """Verify welcome message string formatting."""
    text_uz = get_text("welcome", "uz", business_name="Demo Electronics")
    assert "Demo Electronics" in text_uz
    assert "xush kelibsiz" in text_uz

    text_ru = get_text("welcome", "ru", business_name="Demo Electronics")
    assert "Demo Electronics" in text_ru
    assert "Добро пожаловать" in text_ru

    text_en = get_text("welcome", "en", business_name="Demo Electronics")
    assert "Demo Electronics" in text_en
    assert "Welcome" in text_en


def test_i18n_fallback():
    """Verify fallback when an unknown language is passed."""
    text = get_text("back_to_menu", "fr")
    assert text == "⬅️ Bosh menyu"
