"""Pydantic schemas for Executive Analytics, National KPIs, and Quota Compliance.

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

from decimal import Decimal
from typing import List
from pydantic import BaseModel


class ExecutiveKpiResponse(BaseModel):
    """Top-level executive KPIs for MoSPI and District Authority dashboards."""

    total_projects: int
    proposed_count: int
    sanctioned_count: int
    in_progress_count: int
    completed_count: int
    stalled_count: int

    total_estimated_cost: Decimal
    total_sanctioned_cost: Decimal
    total_actual_expenditure: Decimal
    fund_utilization_percentage: float

    sc_quota_allocation_pct: float
    st_quota_allocation_pct: float
    sc_quota_mandate_met: bool
    st_quota_mandate_met: bool

    active_anomalies_count: int


class SectorBreakdownItem(BaseModel):
    """Aggregated project metrics per development sector."""

    category: str
    project_count: int
    sanctioned_amount: Decimal
    expenditure_amount: Decimal


class AgencyRankingItem(BaseModel):
    """Implementing agency performance and efficiency ranking."""

    agency_code: str
    agency_name: str
    department: str
    project_count: int
    efficiency_rating: float
    avg_delay_days: float
