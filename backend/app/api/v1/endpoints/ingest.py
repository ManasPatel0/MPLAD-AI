"""FastAPI router endpoints for MPLADS Data Ingestion and ETL.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)
"""

from __future__ import annotations

from typing import Any, Dict, List
from fastapi import APIRouter, Body, Depends, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.agency import ImplementingAgency
from app.models.constituency import Constituency
from app.models.district import District
from app.models.project import Project
from app.schemas.ingestion import IngestionSummary, ProjectIngestRecord
from app.services.ingestion_service import MPLADSIngestionService

router = APIRouter(prefix="/ingest", tags=["Data Ingestion & ETL"])
service = MPLADSIngestionService()


@router.post(
    "/batch",
    response_model=IngestionSummary,
    status_code=status.HTTP_200_OK,
    summary="Ingest batch of project records (JSON)",
    description="Validate and ingest or update a list of MPLADS project records into PostgreSQL.",
)
async def ingest_batch(
    records: List[Dict[str, Any]] = Body(
        ...,
        description="List of raw project objects",
        examples=[
            [
                {
                    "project_code": "MPLADS-TEST-001",
                    "title": "Community RO Plant",
                    "category": "DRINKING_WATER",
                    "state": "Uttar Pradesh",
                    "constituency_code": "PC-UP-77",
                    "constituency_name": "Varanasi",
                    "district_name": "Varanasi",
                    "estimated_cost": 2500000.00,
                    "latitude": 25.3176,
                    "longitude": 82.9739,
                    "recommendation_date": "2024-01-15",
                    "target_completion_date": "2024-08-30",
                }
            ]
        ],
    ),
    db: AsyncSession = Depends(get_db),
) -> IngestionSummary:
    """Process a batch of MPLADS project records."""
    if not records:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Records array cannot be empty.",
        )
    return await service.process_batch(db, records)


@router.post(
    "/csv",
    response_model=IngestionSummary,
    status_code=status.HTTP_200_OK,
    summary="Ingest raw CSV records",
    description="Parse and process a raw CSV string containing MPLADS project records.",
)
async def ingest_csv(
    csv_content: str = Body(
        ...,
        media_type="text/plain",
        description="CSV formatted string with headers",
    ),
    db: AsyncSession = Depends(get_db),
) -> IngestionSummary:
    """Parse raw CSV text and process into database."""
    parsed_rows = service.parse_csv_stream(csv_content)
    if not parsed_rows:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="CSV content could not be parsed or contains no rows.",
        )
    return await service.process_batch(db, parsed_rows)


@router.post(
    "/seed-sample",
    response_model=IngestionSummary,
    status_code=status.HTTP_200_OK,
    summary="Seed sample MPLADS developmental projects",
    description="Pre-populates the database with realistic multi-state MPLADS works for demonstration and ML testing.",
)
async def seed_sample_projects(
    db: AsyncSession = Depends(get_db),
) -> IngestionSummary:
    """Seed foundational sample projects into the database."""
    seed_records = service.get_seed_dataset()
    return await service.process_batch(db, seed_records)


@router.get(
    "/stats",
    response_model=Dict[str, Any],
    status_code=status.HTTP_200_OK,
    summary="Ingestion & database statistics",
    description="Returns aggregate entity counts currently persisted in PostgreSQL.",
)
async def get_ingestion_stats(
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """Retrieve aggregate counts across core relational models."""
    try:
        project_count = (await db.execute(select(func.count(Project.id)))).scalar_one()
        constituency_count = (await db.execute(select(func.count(Constituency.id)))).scalar_one()
        district_count = (await db.execute(select(func.count(District.id)))).scalar_one()
        agency_count = (await db.execute(select(func.count(ImplementingAgency.id)))).scalar_one()

        return {
            "status": "healthy",
            "counts": {
                "projects": project_count,
                "constituencies": constituency_count,
                "districts": district_count,
                "implementing_agencies": agency_count,
            },
        }
    except Exception as exc:
        return {
            "status": "unreachable",
            "message": str(exc),
            "counts": {
                "projects": 0,
                "constituencies": 0,
                "districts": 0,
                "implementing_agencies": 0,
            },
        }
