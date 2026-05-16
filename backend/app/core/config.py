from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application-wide configuration loaded from environment variables.

    Every value here can be overridden via a `.env` file in the backend
    directory or through real environment variables in production.
    """

    # ── Application ──────────────────────────────────────────────
    PROJECT_NAME: str = "DevSentinel AI"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"
    FRONTEND_URL: str = "http://localhost:3000"
    BACKEND_URL: str = "http://localhost:8000"

    # ── Database ─────────────────────────────────────────────────
    DATABASE_URL: str = "postgresql+psycopg://devsentinel:devsentinel_local@localhost:5433/devsentinel"

    # ── Redis ────────────────────────────────────────────────────
    REDIS_URL: str = "redis://localhost:6379/0"

    # ── Security ─────────────────────────────────────────────────
    SECRET_KEY: str = "replace-this-with-a-64-char-random-hex-string-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # ── OpenAI / AI models ───────────────────────────────────────
    OPENAI_API_KEY: str = ""
    REASONING_MODEL: str = "gpt-5.4"
    FAST_MODEL: str = "gpt-5-mini"
    EMBEDDING_MODEL: str = "text-embedding-3-large"
    EMBEDDING_DIMENSIONS: int = 3072

    @property
    def is_development(self) -> bool:
        return self.ENVIRONMENT == "development"

    @property
    def is_production(self) -> bool:
        return self.ENVIRONMENT == "production"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
