"""Structured logging configuration with automatic secret redaction."""

import logging
import re
import sys
from typing import Any
from backend.app.core.config import settings

# Sensitive token detection patterns
TOKEN_PATTERNS = [
    re.compile(r"bot[0-9]{8,10}:[a-zA-Z0-9_-]{35}"),  # Telegram Bot Token
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),             # Gemini / Google API Key
    re.compile(r"(password|secret|token)=['\"]?[^'\"\s]+['\"]?", re.IGNORECASE),
]


class SecretMaskingFilter(logging.Filter):
    """Logging filter that scrubs credentials and sensitive tokens from log records."""

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_secrets(record.msg)
        if record.args:
            if isinstance(record.args, dict):
                record.args = {k: self._mask_val(v) for k, v in record.args.items()}
            elif isinstance(record.args, tuple):
                record.args = tuple(self._mask_val(v) for v in record.args)
        return True

    @classmethod
    def _mask_val(cls, val: Any) -> Any:
        if isinstance(val, str):
            return cls.mask_secrets(val)
        return val

    @classmethod
    def mask_secrets(cls, text: str) -> str:
        # Also redact configured secrets if present
        if settings.gemini_api_key and len(settings.gemini_api_key) > 6:
            text = text.replace(settings.gemini_api_key, "***GEMINI_KEY_REDACTED***")
        if settings.telegram_bot_token and len(settings.telegram_bot_token) > 6:
            text = text.replace(settings.telegram_bot_token, "***TG_TOKEN_REDACTED***")
        if settings.session_secret and len(settings.session_secret) > 6:
            text = text.replace(settings.session_secret, "***SESSION_SECRET_REDACTED***")

        for pattern in TOKEN_PATTERNS:
            text = pattern.sub("***REDACTED***", text)
        return text


def setup_logging() -> logging.Logger:
    """Initialize and configure root logger with masking filter."""
    logger = logging.getLogger("nexus_ai")
    level = getattr(logging, settings.log_level.upper(), logging.INFO)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        handler.addFilter(SecretMaskingFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
