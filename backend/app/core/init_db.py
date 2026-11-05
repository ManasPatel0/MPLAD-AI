"""Database tables initialization utility for MPLAD-AI."""

from __future__ import annotations

import asyncio
import logging
from app.core.database import get_engine
from app.models import Base

logger = logging.getLogger("mplad_ai.init_db")


async def init_models() -> None:
    """Create all relational tables defined in SQLAlchemy models if they do not exist."""
    engine = get_engine()
    if engine is None:
        raise RuntimeError("Database engine is not configured or asyncpg is missing.")

    logger.info("Initializing database tables on connected PostgreSQL instance...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("All database tables verified and initialized successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(init_models())
