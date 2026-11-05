"""PostgreSQL database connectivity and session lifecycle management.

Configured for SQLAlchemy 2.0 with asynchronous PostgreSQL (asyncpg).
Includes safe credential masking, non-blocking health probe checks,
and graceful fallback when drivers or database instances are unavailable.
"""

from __future__ import annotations

import logging
import re
from typing import Any, AsyncGenerator, Dict, Optional
from urllib.parse import urlparse

from app.core.config import settings

logger = logging.getLogger(__name__)


def mask_db_url(url: str) -> str:
    """Mask password credentials in database connection URLs for safe reporting."""
    if not url:
        return ""
    try:
        parsed = urlparse(url)
        if parsed.password:
            netloc = f"{parsed.username}:***@{parsed.hostname}"
            if parsed.port:
                netloc += f":{parsed.port}"
            return parsed._replace(netloc=netloc).geturl()
    except Exception:
        return re.sub(r"://([^:]+):([^@]+)@", r"://\1:***@", url)
    return url


# Module-level engine and sessionmaker state
_async_engine: Any = None
_async_session_maker: Any = None
_driver_error: Optional[str] = None


def get_engine() -> Any:
    """Initialize or return the cached SQLAlchemy async engine."""
    global _async_engine, _async_session_maker, _driver_error

    if _async_engine is not None:
        return _async_engine

    try:
        from sqlalchemy.ext.asyncio import (
            AsyncSession,
            async_sessionmaker,
            create_async_engine,
        )

        _async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
            future=True,
            pool_pre_ping=True,
            connect_args={"timeout": settings.DB_CONNECT_TIMEOUT_SECONDS},
        )
        _async_session_maker = async_sessionmaker(
            bind=_async_engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )
        _driver_error = None
        return _async_engine
    except (ImportError, ModuleNotFoundError) as err:
        logger.warning("PostgreSQL async driver unavailable: %s", err)
        _driver_error = str(err)
        return None
    except Exception as err:
        logger.warning("Error initializing database engine: %s", err)
        _driver_error = str(err)
        return None


def get_session_maker() -> Any:
    """Return configured async sessionmaker if available."""
    get_engine()
    return _async_session_maker


async def get_db() -> AsyncGenerator[Any, None]:
    """Dependency injection helper for FastAPI routes requesting a DB session."""
    session_factory = get_session_maker()
    if session_factory is None:
        raise RuntimeError(
            f"Database engine is not configured: {_driver_error or 'driver missing'}"
        )

    async with session_factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def check_db_connection() -> Dict[str, Any]:
    """Non-blocking probe to verify PostgreSQL availability.

    Returns diagnostic status without crashing the gateway if the database or driver is offline.
    """
    masked_url = mask_db_url(settings.DATABASE_URL)
    engine = get_engine()

    if engine is None:
        return {
            "status": "disconnected",
            "dialect": "postgresql",
            "driver": "asyncpg (not installed)",
            "target": masked_url,
            "message": (
                "PostgreSQL async driver 'asyncpg' is not installed in the active environment. "
                "Install requirements.txt (`pip install -r backend/requirements.txt`) to connect."
            ),
            "driver_error": _driver_error,
        }

    try:
        from sqlalchemy import text

        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            scalar = result.scalar()
            if scalar == 1:
                return {
                    "status": "connected",
                    "dialect": "postgresql",
                    "driver": getattr(engine.dialect, "driver", "asyncpg"),
                    "target": masked_url,
                    "message": "PostgreSQL relational store connection established.",
                }
    except Exception as exc:
        logger.warning("Database connection check failed: %s", exc)
        return {
            "status": "disconnected",
            "dialect": "postgresql",
            "driver": "asyncpg",
            "target": masked_url,
            "message": "PostgreSQL database offline or unreachable. Development standalone mode active.",
            "error_detail": str(exc).split("\n")[0],
        }

    return {
        "status": "unknown",
        "dialect": "postgresql",
        "target": masked_url,
    }
