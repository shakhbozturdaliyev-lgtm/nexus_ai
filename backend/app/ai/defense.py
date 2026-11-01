"""Prompt injection defense and outbound secret leak prevention."""

import re
import unicodedata
from typing import Optional, Tuple
from backend.app.core.config import settings
from backend.app.core.logging import logger

# Prompt injection signatures
INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(all\s+)?(previous|prior)\s+instructions", re.IGNORECASE),
    re.compile(r"disregard\s+(all\s+)?(previous|prior)\s+rules", re.IGNORECASE),
    re.compile(r"system\s+(prompt|instructions?)\s+(override|reveal|leak)", re.IGNORECASE),
    re.compile(r"you\s+are\s+now\s+in\s+(developer|dan|jailbreak)\s+mode", re.IGNORECASE),
    re.compile(r"reveal\s+(your\s+)?([a-z_]*)(api_?key|bot_?token|secret|password|token)", re.IGNORECASE),
    re.compile(r"print\s+(your\s+)?(system\s+prompt|instructions)", re.IGNORECASE),
    re.compile(r"bypass\s+(safety|content)\s+filters?", re.IGNORECASE),
    re.compile(r"what\s+is\s+your\s+(initial|system)\s+prompt", re.IGNORECASE),
]

# Sensitive token leakage signatures
LEAKAGE_PATTERNS = [
    re.compile(r"bot[0-9]{8,10}:[a-zA-Z0-9_-]{35}"),
    re.compile(r"AIza[0-9A-Za-z-_]{35}"),
    re.compile(r"eyJ[a-zA-Z0-9_-]+\.eyJ[a-zA-Z0-9_-]+\.[a-zA-Z0-9_-]+"),  # JWT
    re.compile(r"(sqlite|postgres|mysql|redis):\/\/[^\s]+", re.IGNORECASE),
]


def sanitize_input(text: str) -> str:
    """Normalize unicode, strip hidden control tags and zero-width characters."""
    if not text:
        return ""
    # NFKC normalizes wide characters, accents, ligatures
    text = unicodedata.normalize("NFKC", text)
    # Strip zero-width spaces and control characters (excluding standard whitespace)
    cleaned = "".join(
        ch for ch in text
        if ch in "\n\r\t " or unicodedata.category(ch) not in ["Cc", "Cf", "Co", "Cn"]
    )
    return cleaned.strip()


def check_prompt_injection(text: str) -> Tuple[bool, Optional[str]]:
    """Inspect input for prompt injection signatures. Returns (is_injection, reason)."""
    cleaned = sanitize_input(text)
    for pattern in INJECTION_PATTERNS:
        match = pattern.search(cleaned)
        if match:
            matched_phrase = match.group(0)
            logger.warning(f"Prompt injection attempt detected: '{matched_phrase}'")
            return True, f"Injection signature matched: '{matched_phrase}'"
    return False, None


def redact_secrets(text: str) -> str:
    """Scan outbound text and redact secrets, keys, and tokens before delivery."""
    if not text:
        return ""

    # Redact configured environment secrets
    if settings.gemini_api_key and len(settings.gemini_api_key) > 6:
        text = text.replace(settings.gemini_api_key, "[REDACTED_API_KEY]")
    if settings.telegram_bot_token and len(settings.telegram_bot_token) > 6:
        text = text.replace(settings.telegram_bot_token, "[REDACTED_BOT_TOKEN]")
    if settings.session_secret and len(settings.session_secret) > 6:
        text = text.replace(settings.session_secret, "[REDACTED_SECRET]")

    # Redact regex patterns
    for pattern in LEAKAGE_PATTERNS:
        text = pattern.sub("[REDACTED_CREDENTIAL]", text)

    return text
