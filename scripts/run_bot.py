"""Standalone script to run the Telegram bot service."""

import sys
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir))

from backend.app.bot.bot import run_polling
from backend.app.core.logging import logger

if __name__ == "__main__":
    logger.info("Initializing NEXUS AI Telegram Bot Runner...")
    run_polling()
