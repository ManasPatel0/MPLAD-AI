"""Health check and diagnostic endpoint."""

from __future__ import annotations

import sys
from typing import Any, Dict, Optional

from fastapi import APIRouter, status
from pydantic import BaseModel, Field

from app.core.config import settings
from app.core.database import check_db_connection
from app.core.exceptions import utc_now_iso

router = APIRouter()


class DatabaseHealth(BaseModel):
    status: str = Field(description="Connection status: connected or disconnected")
    dialect: str = Field(default="postgresql")
    target: str = Field(description="Target host with masked credentials")
    message: Optional[str] = None
    error_detail: Optional[str] = None


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Overall health state")
    app_name: str
    version: str
    environment: str
    timestamp: str
    database: Dict[str, Any]
    services: Dict[str, str]
    python_version: str


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="System Health & Diagnostic Status",
    description=(
        "Returns comprehensive gateway health, PostgreSQL connection status, "
        "and sub-service readiness for SIH 2026 MPLAD-AI monitoring."
    ),
    tags=["System"],
)
async def get_system_health() -> HealthResponse:
    db_status = await check_db_connection()

    return HealthResponse(
        status="healthy",
        app_name=settings.PROJECT_NAME,
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=utc_now_iso(),
        database=db_status,
        services={
            "api_gateway": "online",
            "rbac_guard": "initialized",
            "ml_engine": "phase_1_standby",
            "gis_service": "phase_1_standby",
        },
        python_version=sys.version.split()[0],
    )
