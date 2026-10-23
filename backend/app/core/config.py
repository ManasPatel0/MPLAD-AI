"""Application configuration module for MPLAD-AI.

Supports reading settings from environment variables and local .env files.
Compatible with standard Pydantic v2 and pydantic-settings.
"""

from __future__ import annotations

import os
from typing import List, Union
from pathlib import Path

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
    from pydantic import Field

    class Settings(BaseSettings):
        PROJECT_NAME: str = Field(default="MPLAD-AI API Gateway")
        VERSION: str = Field(default="1.0.0")
        API_V1_STR: str = Field(default="/api/v1")
        ENVIRONMENT: str = Field(default="development")
        DEBUG: bool = Field(default=True)

        # Database
        DATABASE_URL: str = Field(
            default="postgresql+asyncpg://postgres:postgres@localhost:5432/mplads_db"
        )
        DATABASE_SYNC_URL: str = Field(
            default="postgresql://postgres:postgres@localhost:5432/mplads_db"
        )
        DB_CONNECT_TIMEOUT_SECONDS: float = Field(default=2.0)

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
        DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/mplads_db",
        )
        DATABASE_SYNC_URL: str = os.getenv(
            "DATABASE_SYNC_URL",
            "postgresql://postgres:postgres@localhost:5432/mplads_db",
        )
        DB_CONNECT_TIMEOUT_SECONDS: float = float(
            os.getenv("DB_CONNECT_TIMEOUT_SECONDS", "2.0")
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
