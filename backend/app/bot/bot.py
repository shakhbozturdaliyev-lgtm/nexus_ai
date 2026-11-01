"""Telegram Application setup and handler registration."""

from typing import Optional
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    MessageHandler,
    filters,
)
from backend.app.bot.handlers import (
    callback_query_handler,
    help_handler,
    language_handler,
    menu_handler,
    start_handler,
    text_message_handler,
)
from backend.app.core.config import settings
from backend.app.core.logging import logger


def build_bot_app(token: Optional[str] = None) -> Optional[Application]:
    """Build and configure the Telegram bot Application instance."""
    bot_token = token or settings.telegram_bot_token
    if not bot_token:
        logger.warning("TELEGRAM_BOT_TOKEN is not configured. Telegram bot service is dormant.")
        return None

    app = ApplicationBuilder().token(bot_token).build()

    # Register Command Handlers
    app.add_handler(CommandHandler("start", start_handler))
    app.add_handler(CommandHandler("help", help_handler))
    app.add_handler(CommandHandler("menu", menu_handler))
    app.add_handler(CommandHandler("lang", language_handler))

    # Register Callback Query Handler for Inline Buttons
    app.add_handler(CallbackQueryHandler(callback_query_handler))

    # Register Text Message Handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_message_handler))

    # Global Error Handler
    async def error_handler(update, context):
        logger.error(f"Telegram bot exception for update {update}: {context.error}")

    app.add_error_handler(error_handler)

    logger.info("Telegram Bot application successfully assembled.")
    return app


def run_polling() -> None:
    """Run bot using long polling."""
    app = build_bot_app()
    if not app:
        logger.error("Cannot start polling: TELEGRAM_BOT_TOKEN is missing in .env.")
        return
    logger.info("Starting Telegram bot in Long Polling mode...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    run_polling()
