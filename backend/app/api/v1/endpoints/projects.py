"""Projects lifecycle, recommendation, and status transition endpoints.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)
"""

from __future__ import annotations

import uuid
from datetime import date
from decimal import Decimal
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import SystemRole, get_current_active_user, require_roles
from app.models.project import Project
from app.models.user import User
from app.schemas.project import (
    ProjectCreateRequest,
    ProjectListResponse,
    ProjectResponse,
    ProjectStatusUpdateRequest,
)

router = APIRouter(prefix="/projects", tags=["Projects Management"])


@router.get(
    "",
    response_model=ProjectListResponse,
    status_code=status.HTTP_200_OK,
    summary="List and filter developmental projects",
    description="Returns a paginated list of MPLADS projects with multi-criteria filtering.",
)
async def list_projects(
    constituency_id: Optional[uuid.UUID] = Query(default=None, description="Filter by Constituency"),
    district_id: Optional[uuid.UUID] = Query(default=None, description="Filter by District"),
    status_filter: Optional[str] = Query(default=None, alias="status", description="Filter by lifecycle status"),
    category: Optional[str] = Query(default=None, description="Filter by category"),
    priority_quota: Optional[str] = Query(default=None, description="Filter by priority quota"),
    is_anomaly: Optional[bool] = Query(default=None, description="Filter flagged anomalies"),
    page: int = Query(default=1, ge=1, description="Page number"),
    limit: int = Query(default=20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db),
) -> ProjectListResponse:
    """Retrieve filtered list of projects."""
    query = select(Project)

    if constituency_id:
        query = query.where(Project.constituency_id == constituency_id)
    if district_id:
        query = query.where(Project.district_id == district_id)
    if status_filter:
        query = query.where(Project.status == status_filter.upper())
    if category:
        query = query.where(Project.category == category.upper())
    if priority_quota:
        query = query.where(Project.priority_quota == priority_quota.upper())
    if is_anomaly is not None:
        query = query.where(Project.is_anomaly == is_anomaly)

    # Count total matching
    count_query = select(func.count()).select_from(query.subquery())
    total_count = (await db.execute(count_query)).scalar_one()

    # Pagination
    offset = (page - 1) * limit
    paginated_query = query.order_by(Project.created_at.desc()).offset(offset).limit(limit)
    records = (await db.execute(paginated_query)).scalars().all()

    return ProjectListResponse(
        total=total_count,
        page=page,
        limit=limit,
        items=[ProjectResponse.model_validate(p) for p in records],
    )


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Recommend a new developmental project",
    description="Restricted to MP, District Collector, and MoSPI Administrator roles.",
)
async def recommend_project(
    payload: ProjectCreateRequest,
    current_user: User = Depends(
        require_roles([SystemRole.MP, SystemRole.DISTRICT_COLLECTOR, SystemRole.MOSPI_ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Submit a new project recommendation into the lifecycle state machine."""
    # Generate unique project code
    code_suffix = uuid.uuid4().hex[:6].upper()
    project_code = f"MPLADS-{date.today().year}-{code_suffix}"

    new_project = Project(
        id=uuid.uuid4(),
        project_code=project_code,
        constituency_id=payload.constituency_id,
        district_id=payload.district_id,
        agency_id=payload.agency_id,
        recommended_by_user_id=current_user.id,
        title=payload.title.strip(),
        description=payload.description.strip(),
        category=payload.category,
        priority_quota=payload.priority_quota,
        estimated_cost=payload.estimated_cost,
        sanctioned_cost=Decimal("0.00"),
        actual_expenditure=Decimal("0.00"),
        status="PROPOSED",
        latitude=payload.latitude,
        longitude=payload.longitude,
        location_address=payload.location_address.strip(),
        recommendation_date=payload.recommendation_date,
        target_completion_date=payload.target_completion_date,
        delay_risk_score=Decimal("0.00"),
        is_anomaly=False,
    )

    db.add(new_project)
    await db.commit()
    await db.refresh(new_project)

    return ProjectResponse.model_validate(new_project)


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get project details dossier",
    description="Retrieves a single project by UUID.",
)
async def get_project_by_id(
    project_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Fetch project details by primary key."""
    stmt = select(Project).where(Project.id == project_id)
    project = (await db.execute(stmt)).scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )
    return ProjectResponse.model_validate(project)


@router.patch(
    "/{project_id}/status",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Transition project status",
    description="Restricted to District Collector and MoSPI Administrator roles.",
)
async def transition_project_status(
    project_id: uuid.UUID,
    payload: ProjectStatusUpdateRequest,
    current_user: User = Depends(
        require_roles([SystemRole.DISTRICT_COLLECTOR, SystemRole.MOSPI_ADMIN])
    ),
    db: AsyncSession = Depends(get_db),
) -> ProjectResponse:
    """Transition project lifecycle state (e.g., sanctioning or work order issuance)."""
    stmt = select(Project).where(Project.id == project_id)
    project = (await db.execute(stmt)).scalars().first()

    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID '{project_id}' not found.",
        )

    project.status = payload.to_status.upper()

    if payload.sanctioned_cost is not None:
        project.sanctioned_cost = payload.sanctioned_cost
        if not project.sanction_date:
            project.sanction_date = date.today()

    if payload.agency_id is not None:
        project.agency_id = payload.agency_id

    if payload.to_status.upper() == "WORK_ORDERED" and not project.work_order_date:
        project.work_order_date = date.today()

    if payload.to_status.upper() == "COMPLETED" and not project.actual_completion_date:
        project.actual_completion_date = date.today()

    await db.commit()
    await db.refresh(project)

    return ProjectResponse.model_validate(project)
