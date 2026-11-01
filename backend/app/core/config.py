"""Application configuration module using Pydantic Settings."""

from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Central configuration schema for NEXUS AI."""

    # Environment
    app_env: str = Field(default="development", validation_alias="APP_ENV")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # Business & Localization
    default_business_id: int = Field(default=1, validation_alias="DEFAULT_BUSINESS_ID")
    default_timezone: str = Field(default="Asia/Tashkent", validation_alias="DEFAULT_TIMEZONE")
    default_currency: str = Field(default="UZS", validation_alias="DEFAULT_CURRENCY")
    supported_locales: List[str] = ["uz", "ru", "en", "uz_cyrl"]

    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./nexus_ai.db",
        validation_alias="DATABASE_URL",
    )

    # Security & JWT
    session_secret: str = Field(
        default="super_secret_nexus_ai_key_at_least_32_bytes_long_123456",
        validation_alias="SESSION_SECRET",
    )
    jwt_algorithm: str = Field(default="HS256", validation_alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(
        default=1440, validation_alias="ACCESS_TOKEN_EXPIRE_MINUTES"
    )
    cors_origins: List[str] = ["*"]

    # Telegram Bot
    telegram_bot_token: Optional[str] = Field(
        default=None, validation_alias="TELEGRAM_BOT_TOKEN"
    )
    telegram_webhook_url: Optional[str] = Field(
        default=None, validation_alias="TELEGRAM_WEBHOOK_URL"
    )

    # Google Gen AI
    gemini_api_key: Optional[str] = Field(
        default=None, validation_alias="GEMINI_API_KEY"
    )
    gemini_model: str = Field(
        default="gemini-2.5-flash", validation_alias="GEMINI_MODEL"
    )
    ai_mock_mode: bool = Field(default=False, validation_alias="AI_MOCK_MODE")

    # AI Execution Guardrails
    max_tool_calls_per_turn: int = 5
    max_context_window_turns: int = 10
    max_output_tokens: int = 800

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Global settings singleton
settings = Settings()
