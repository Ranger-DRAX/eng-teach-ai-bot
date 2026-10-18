"""Application configuration loaded from environment variables."""

from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    """Application settings populated from environment variables or .env file."""

    # Database
    database_url: str = "sqlite+aiosqlite:///./test.db"

    # LLM Configuration
    llm_provider: str = "auto"
    llm_model: str = "gemini-2.5-flash"
    llm_api_key: str = ""
    gemini_api_key: str = ""
    llm_timeout_ms: int = 4000

    # Application
    app_env: str = "development"
    log_level: str = "INFO"
    secret_key: str = "change-me-to-a-random-secret"

    # Test
    test_database_url: str = "sqlite+aiosqlite:///./test.db"

    model_config = SettingsConfigDict(
        env_file=[str(ROOT_DIR / ".env"), ".env"],
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def effective_api_key(self) -> str:
        key = self.gemini_api_key or self.llm_api_key
        if key:
            return key.strip()
        for env_var in ("Gemini_API_Key", "GEMINI_API_KEY", "gemini_api_key", "LLM_API_KEY"):
            val = os.environ.get(env_var)
            if val:
                return val.strip()
        env_path = ROOT_DIR / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    if k.strip().lower() in ("gemini_api_key", "llm_api_key"):
                        return v.strip().strip("'\"")
        return ""


# Singleton application settings instance
settings = Settings()
