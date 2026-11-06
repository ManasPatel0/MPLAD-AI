"""Command-line script to populate MPLADS sample developmental works.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Usage:
    python -m app.scripts.seed_sample_data
"""

from __future__ import annotations

import asyncio
import logging
import sys

from app.core.database import get_engine, get_session_maker
from app.models.base import Base
from app.services.ingestion_service import MPLADSIngestionService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("mplad_ai.seeder")


async def seed_data() -> None:
    """Execute sample data seeding in the active PostgreSQL database."""
    engine = get_engine()
    if engine is None:
        logger.error("Database engine could not be initialized. Please verify DATABASE_URL.")
        sys.exit(1)

    logger.info("Connecting to database and verifying table schema...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database schema synchronized.")

    session_maker = get_session_maker()
    service = MPLADSIngestionService()
    seed_records = service.get_seed_dataset()

    logger.info("Ingesting %d sample MPLADS project records...", len(seed_records))
    async with session_maker() as session:
        summary = await service.process_batch(session, seed_records)
        await session.commit()

    logger.info("Ingestion completed: %s", summary.model_dump_json(indent=2))


if __name__ == "__main__":
    asyncio.run(seed_data())
