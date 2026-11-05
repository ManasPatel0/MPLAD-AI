"""Application configuration module for MPLAD-AI.

Supports reading settings from environment variables and local .env files.
Compatible with standard Pydantic v2 and pydantic-settings.
Includes normalization for Neon Cloud PostgreSQL URLs (asyncpg driver prefix and SSL modes).
"""

from __future__ import annotations

import os
import re
from typing import List, Union
from pathlib import Path


def normalize_database_url(url: str, is_async: bool = True) -> str:
    """Normalize database connection URLs for Neon PostgreSQL and asyncpg/sync drivers.

    Converts `postgres://` or `postgresql://` to `postgresql+asyncpg://` for async connections.
    Translates `sslmode=...` to `ssl=...` for compatibility with asyncpg, and ensures
    SSL is enabled when connecting to Neon cloud hosts.
    """
    if not url:
        return ""

    clean_url = url.strip()

    # Normalize scheme for asyncpg
    if is_async:
        if clean_url.startswith("postgres://"):
            clean_url = "postgresql+asyncpg://" + clean_url[len("postgres://") :]
        elif clean_url.startswith("postgresql://"):
            clean_url = "postgresql+asyncpg://" + clean_url[len("postgresql://") :]
        elif clean_url.startswith("postgresql+psycopg2://"):
            clean_url = "postgresql+asyncpg://" + clean_url[len("postgresql+psycopg2://") :]

        # Asyncpg uses 'ssl' keyword rather than 'sslmode'
        if "sslmode=" in clean_url:
            clean_url = re.sub(r"([?&])sslmode=", r"\1ssl=", clean_url)

        # Ensure Neon cloud connections have ssl=require if not explicitly specified
        if "neon.tech" in clean_url.lower():
            if "ssl=" not in clean_url and "sslmode=" not in clean_url:
                separator = "&" if "?" in clean_url else "?"
                clean_url = f"{clean_url}{separator}ssl=require"
    else:
        # Normalize scheme for sync drivers (psycopg2 / Alembic migrations)
        if clean_url.startswith("postgres://"):
            clean_url = "postgresql://" + clean_url[len("postgres://") :]
        elif clean_url.startswith("postgresql+asyncpg://"):
            clean_url = "postgresql://" + clean_url[len("postgresql+asyncpg://") :]

    return clean_url


# Load environment variables from .env file if available
try:
    from dotenv import load_dotenv

    # Search for .env in current directory, backend directory, or project root
    for path in [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent.parent / ".env",
        Path(__file__).resolve().parent.parent.parent.parent / ".env",
    ]:
        if path.exists():
            load_dotenv(dotenv_path=path, override=False)
            break
except ImportError:
    pass

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator

    class Settings(BaseSettings):
        PROJECT_NAME: str = Field(default="MPLAD-AI API Gateway")
        VERSION: str = Field(default="1.0.0")
        API_V1_STR: str = Field(default="/api/v1")
        ENVIRONMENT: str = Field(default="development")
        DEBUG: bool = Field(default=True)

        # Database (Default: local dev, auto-normalizes for Neon Cloud)
        DATABASE_URL: str = Field(
            default="postgresql+asyncpg://postgres:postgres@localhost:5432/mplads_db"
        )
        DATABASE_SYNC_URL: str = Field(
            default="postgresql://postgres:postgres@localhost:5432/mplads_db"
        )
        DB_CONNECT_TIMEOUT_SECONDS: float = Field(default=10.0)

        # Security
        SECRET_KEY: str = Field(
            default="insecure-dev-secret-key-change-for-production-deployment"
        )
        ALGORITHM: str = Field(default="HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=1440)

        # CORS
        CORS_ORIGINS: Union[List[str], str] = Field(
            default=[
                "http://localhost:5173",
                "http://127.0.0.1:5173",
                "http://localhost:3000",
                "http://127.0.0.1:3000",
            ]
        )

        model_config = {
            "case_sensitive": True,
            "extra": "ignore",
            "env_file": ".env",
        }

        @field_validator("DATABASE_URL", mode="after")
        @classmethod
        def validate_database_url(cls, v: str) -> str:
            return normalize_database_url(v, is_async=True)

        @field_validator("DATABASE_SYNC_URL", mode="after")
        @classmethod
        def validate_database_sync_url(cls, v: str) -> str:
            return normalize_database_url(v, is_async=False)

        @property
        def cors_origins_list(self) -> List[str]:
            if isinstance(self.CORS_ORIGINS, list):
                return self.CORS_ORIGINS
            if isinstance(self.CORS_ORIGINS, str):
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            return ["*"]

except ImportError:
    from pydantic import BaseModel

    class Settings(BaseModel):  # type: ignore[no-redef]
        PROJECT_NAME: str = os.getenv("PROJECT_NAME", "MPLAD-AI API Gateway")
        VERSION: str = os.getenv("VERSION", "1.0.0")
        API_V1_STR: str = os.getenv("API_V1_STR", "/api/v1")
        ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
        DEBUG: bool = os.getenv("DEBUG", "true").lower() in ("1", "true", "yes")

        # Database
        DATABASE_URL: str = normalize_database_url(
            os.getenv(
                "DATABASE_URL",
                "postgresql+asyncpg://postgres:postgres@localhost:5432/mplads_db",
            ),
            is_async=True,
        )
        DATABASE_SYNC_URL: str = normalize_database_url(
            os.getenv(
                "DATABASE_SYNC_URL",
                "postgresql://postgres:postgres@localhost:5432/mplads_db",
            ),
            is_async=False,
        )
        DB_CONNECT_TIMEOUT_SECONDS: float = float(
            os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "10.0")
        )

        # Security
        SECRET_KEY: str = os.getenv(
            "SECRET_KEY", "insecure-dev-secret-key-change-for-production-deployment"
        )
        ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
        ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
        )

        # CORS
        CORS_ORIGINS: Union[List[str], str] = os.getenv(
            "CORS_ORIGINS",
            "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000,http://127.0.0.1:3000",
        )

        @property
        def cors_origins_list(self) -> List[str]:
            if isinstance(self.CORS_ORIGINS, list):
                return self.CORS_ORIGINS
            if isinstance(self.CORS_ORIGINS, str):
                return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
            return ["*"]


settings = Settings()
