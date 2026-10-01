"""
Application configuration using Pydantic Settings.
Loads all secrets and config from .env file — no hardcoded values.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # ── Gemini AI ──────────────────────────────────────────────
    GEMINI_API_KEY: str
    GEMINI_MODEL: str = "gemini-3.8-flash"

    # ── Groq AI ────────────────────────────────────────────────
    GROQ_API_KEY: str

    # ── Application ────────────────────────────────────────────
    APP_TITLE: str = "Gourmet AI Recipe Generator"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # ── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str

    # ── Rate limiting ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30
    
    # ── Auth & JWT ─────────────────────────────────────────────
    SECRET_KEY: str = "your-super-secret-key-for-development"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7 # 1 week

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
    )


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for app settings."""
    return Settings()
