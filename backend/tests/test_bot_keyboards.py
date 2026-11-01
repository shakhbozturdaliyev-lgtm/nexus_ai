"""Unit tests for bot keyboard structures."""

from backend.app.bot.keyboards import (
    get_language_keyboard,
    get_main_menu_keyboard,
    get_support_confirmation_keyboard,
)


def test_language_keyboard_buttons():
    """Verify inline language selection buttons and callback codes."""
    kb = get_language_keyboard()
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "lang:uz" in callbacks
    assert "lang:ru" in callbacks
    assert "lang:en" in callbacks
    assert "lang:uz_cyrl" in callbacks


def test_main_menu_keyboard_layout():
    """Verify main reply keyboard contains 4 rows with 2 buttons each."""
    kb_uz = get_main_menu_keyboard("uz")
    assert len(kb_uz.keyboard) == 4
    for row in kb_uz.keyboard:
        assert len(row) == 2

    # Check button texts
    all_buttons = [
        btn.text if hasattr(btn, "text") else str(btn)
        for row in kb_uz.keyboard
        for btn in row
    ]
    assert "📱 Mahsulotlar" in all_buttons
    assert "📦 Buyurtmalarim" in all_buttons
    assert "🚚 Yetkazib berish" in all_buttons
    assert "👨‍💼 Operator bilan bog'lanish" in all_buttons


def test_support_confirmation_keyboard():
    """Verify support confirmation callback buttons."""
    kb = get_support_confirmation_keyboard("uz")
    callbacks = [btn.callback_data for row in kb.inline_keyboard for btn in row]
    assert "confirm_support" in callbacks
    assert "cancel_support" in callbacks
