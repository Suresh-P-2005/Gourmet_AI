"""
Application configuration using Pydantic Settings.
Loads all secrets and config from .env file — no hardcoded values.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional


class Settings(BaseSettings):
    """Central configuration loaded from environment variables / .env file."""

    # ── Gemini AI ──────────────────────────────────────────────
    GEMINI_API_KEY: str = "your_gemini_api_key_here"
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # ── Application ────────────────────────────────────────────
    APP_TITLE: str = "Gourmet AI Recipe Generator"
    APP_VERSION: str = "2.0.0"
    DEBUG: bool = False

    # ── CORS ───────────────────────────────────────────────────
    CORS_ORIGINS: str = "*"

    # ── Database ───────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/recipes"

    # ── Rate limiting ──────────────────────────────────────────
    RATE_LIMIT_PER_MINUTE: int = 30

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton for app settings."""
    return Settings()
