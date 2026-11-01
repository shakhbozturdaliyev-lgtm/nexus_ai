"""Telegram bot keyboard generators."""

from typing import List
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from backend.app.bot.i18n import get_text


def get_language_keyboard() -> InlineKeyboardMarkup:
    """Return inline keyboard for selecting bot language."""
    buttons = [
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha (Lotin)", callback_data="lang:uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="lang:ru"),
        ],
        [
            InlineKeyboardButton("🇬🇧 English", callback_data="lang:en"),
            InlineKeyboardButton("🇺🇿 Ўзбекча (Кирилл)", callback_data="lang:uz_cyrl"),
        ],
    ]
    return InlineKeyboardMarkup(buttons)


def get_main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Return standard persistent reply keyboard for customer navigation."""
    keyboard = [
        [get_text("menu_products", lang), get_text("menu_search", lang)],
        [get_text("menu_orders", lang), get_text("menu_delivery", lang)],
        [get_text("menu_warranty", lang), get_text("menu_faq", lang)],
        [get_text("menu_support", lang), get_text("menu_language", lang)],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True, is_persistent=True)


def get_support_confirmation_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Return confirmation keyboard before escalating to operator."""
    buttons = [
        [
            InlineKeyboardButton("✅ Ha, bog'lanish" if lang == "uz" else ("✅ Да, связаться" if lang == "ru" else "✅ Yes, connect"), callback_data="confirm_support"),
            InlineKeyboardButton("❌ Bekor qilish" if lang == "uz" else ("❌ Отмена" if lang == "ru" else "❌ Cancel"), callback_data="cancel_support"),
        ]
    ]
    return InlineKeyboardMarkup(buttons)
