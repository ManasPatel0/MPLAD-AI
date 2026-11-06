"""Analytics, Executive KPIs, and Compliance metrics endpoints.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)
"""

from __future__ import annotations

from decimal import Decimal
from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.agency import ImplementingAgency
from app.models.project import Project
from app.schemas.analytics import AgencyRankingItem, ExecutiveKpiResponse, SectorBreakdownItem

router = APIRouter(prefix="/analytics", tags=["Analytics & Executive Dashboards"])


@router.get(
    "/kpis",
    response_model=ExecutiveKpiResponse,
    status_code=status.HTTP_200_OK,
    summary="Get executive dashboard summary KPIs",
    description="Returns aggregate project counts, financial totals, quota compliance, and active anomalies.",
)
async def get_executive_kpis(
    db: AsyncSession = Depends(get_db),
) -> ExecutiveKpiResponse:
    """Calculate executive indicators across all projects."""
    # Project status counts
    total_q = await db.execute(select(func.count(Project.id)))
    total_projects = total_q.scalar_one() or 0

    if total_projects == 0:
        return ExecutiveKpiResponse(
            total_projects=0,
            proposed_count=0,
            sanctioned_count=0,
            in_progress_count=0,
            completed_count=0,
            stalled_count=0,
            total_estimated_cost=Decimal("0.00"),
            total_sanctioned_cost=Decimal("0.00"),
            total_actual_expenditure=Decimal("0.00"),
            fund_utilization_percentage=0.0,
            sc_quota_allocation_pct=0.0,
            st_quota_allocation_pct=0.0,
            sc_quota_mandate_met=False,
            st_quota_mandate_met=False,
            active_anomalies_count=0,
        )

    # Status breakdown
    proposed_q = await db.execute(select(func.count(Project.id)).where(Project.status == "PROPOSED"))
    sanctioned_q = await db.execute(select(func.count(Project.id)).where(Project.status == "SANCTIONED"))
    in_progress_q = await db.execute(select(func.count(Project.id)).where(Project.status == "IN_PROGRESS"))
    completed_q = await db.execute(select(func.count(Project.id)).where(Project.status == "COMPLETED"))
    stalled_q = await db.execute(select(func.count(Project.id)).where(Project.status == "STALLED"))

    # Financial sums
    sum_est_q = await db.execute(select(func.sum(Project.estimated_cost)))
    sum_sanct_q = await db.execute(select(func.sum(Project.sanctioned_cost)))
    sum_exp_q = await db.execute(select(func.sum(Project.actual_expenditure)))

    total_est = sum_est_q.scalar_one() or Decimal("0.00")
    total_sanct = sum_sanct_q.scalar_one() or Decimal("0.00")
    total_exp = sum_exp_q.scalar_one() or Decimal("0.00")

    utilization_pct = 0.0
    if total_sanct > Decimal("0.00"):
        utilization_pct = float(round((total_exp / total_sanct) * 100, 2))

    # Quota calculations
    sc_count_q = await db.execute(select(func.count(Project.id)).where(Project.priority_quota == "SC_MANDATE"))
    st_count_q = await db.execute(select(func.count(Project.id)).where(Project.priority_quota == "ST_MANDATE"))
    sc_count = sc_count_q.scalar_one() or 0
    st_count = st_count_q.scalar_one() or 0

    sc_pct = float(round((sc_count / total_projects) * 100, 2))
    st_pct = float(round((st_count / total_projects) * 100, 2))

    # Anomalies
    anomaly_q = await db.execute(select(func.count(Project.id)).where(Project.is_anomaly == True))  # noqa: E712
    anomaly_count = anomaly_q.scalar_one() or 0

    return ExecutiveKpiResponse(
        total_projects=total_projects,
        proposed_count=proposed_q.scalar_one() or 0,
        sanctioned_count=sanctioned_q.scalar_one() or 0,
        in_progress_count=in_progress_q.scalar_one() or 0,
        completed_count=completed_q.scalar_one() or 0,
        stalled_count=stalled_q.scalar_one() or 0,
        total_estimated_cost=total_est,
        total_sanctioned_cost=total_sanct,
        total_actual_expenditure=total_exp,
        fund_utilization_percentage=utilization_pct,
        sc_quota_allocation_pct=sc_pct,
        st_quota_allocation_pct=st_pct,
        sc_quota_mandate_met=(sc_pct >= 15.0),
        st_quota_mandate_met=(st_pct >= 7.5),
        active_anomalies_count=anomaly_count,
    )


@router.get(
    "/sectors",
    response_model=List[SectorBreakdownItem],
    status_code=status.HTTP_200_OK,
    summary="Get project and funding distribution by sector",
)
async def get_sector_breakdown(
    db: AsyncSession = Depends(get_db),
) -> List[SectorBreakdownItem]:
    """Aggregate project count and expenditures grouped by category."""
    stmt = (
        select(
            Project.category,
            func.count(Project.id).label("count"),
            func.coalesce(func.sum(Project.sanctioned_cost), Decimal("0.00")).label("sanctioned"),
            func.coalesce(func.sum(Project.actual_expenditure), Decimal("0.00")).label("expenditure"),
        )
        .group_by(Project.category)
        .order_by(func.count(Project.id).desc())
    )
    results = (await db.execute(stmt)).all()

    return [
        SectorBreakdownItem(
            category=row.category,
            project_count=row.count,
            sanctioned_amount=row.sanctioned,
            expenditure_amount=row.expenditure,
        )
        for row in results
    ]


@router.get(
    "/agencies",
    response_model=List[AgencyRankingItem],
    status_code=status.HTTP_200_OK,
    summary="Get implementing agencies performance ranking",
)
async def get_agencies_ranking(
    db: AsyncSession = Depends(get_db),
) -> List[AgencyRankingItem]:
    """Retrieve implementing agency efficiency ranking."""
    stmt = (
        select(
            ImplementingAgency.code,
            ImplementingAgency.name,
            ImplementingAgency.department,
            ImplementingAgency.efficiency_rating,
            ImplementingAgency.avg_historical_delay_days,
            func.count(Project.id).label("project_count"),
        )
        .outerjoin(Project, Project.agency_id == ImplementingAgency.id)
        .group_by(
            ImplementingAgency.code,
            ImplementingAgency.name,
            ImplementingAgency.department,
            ImplementingAgency.efficiency_rating,
            ImplementingAgency.avg_historical_delay_days,
        )
        .order_by(ImplementingAgency.efficiency_rating.desc())
    )
    results = (await db.execute(stmt)).all()

    return [
        AgencyRankingItem(
            agency_code=row.code,
            agency_name=row.name,
            department=row.department,
            project_count=row.project_count,
            efficiency_rating=float(row.efficiency_rating or 3.0),
            avg_delay_days=float(row.avg_historical_delay_days or 0.0),
        )
        for row in results
    ]
