"""Pydantic schemas for Project lifecycle operations, filtering, and status transitions.

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field


class ProjectCreateRequest(BaseModel):
    """Payload for submitting a new developmental project recommendation."""

    constituency_id: uuid.UUID = Field(..., description="Target Parliamentary Constituency UUID")
    district_id: uuid.UUID = Field(..., description="Nodal District UUID")
    agency_id: Optional[uuid.UUID] = Field(default=None, description="Assigned Implementing Agency UUID")

    title: str = Field(..., min_length=3, max_length=256, description="Project title")
    description: str = Field(..., min_length=5, description="Detailed scope of developmental work")
    category: str = Field(
        default="COMMUNITY_INFRASTRUCTURE",
        description="Category (DRINKING_WATER, EDUCATION, PUBLIC_HEALTH, SANITATION, ROADS_BRIDGES, IRRIGATION, COMMUNITY_INFRASTRUCTURE, OTHER)",
    )
    priority_quota: str = Field(
        default="GENERAL",
        description="Priority Quota (GENERAL, SC_MANDATE, ST_MANDATE)",
    )
    estimated_cost: Decimal = Field(..., ge=0, description="Estimated work cost in INR")

    latitude: Decimal = Field(..., ge=-90, le=90, description="GPS Latitude (-90 to +90)")
    longitude: Decimal = Field(..., ge=-180, le=180, description="GPS Longitude (-180 to +180)")
    location_address: str = Field(..., description="Village, Ward, or Site location address")

    recommendation_date: date = Field(default_factory=date.today, description="Date of MP recommendation")
    target_completion_date: date = Field(..., description="Target work completion date")


class ProjectStatusUpdateRequest(BaseModel):
    """Payload for transitioning project status (e.g. Sanctioning, Issuing Work Order)."""

    to_status: str = Field(
        ...,
        description="Target lifecycle status (PROPOSED, SCRUTINIZED, SANCTIONED, WORK_ORDERED, IN_PROGRESS, COMPLETED, REJECTED, STALLED)",
    )
    sanctioned_cost: Optional[Decimal] = Field(default=None, ge=0, description="Sanctioned amount in INR")
    agency_id: Optional[uuid.UUID] = Field(default=None, description="Assigned implementing agency UUID")
    remarks: Optional[str] = Field(default=None, description="Administrative or inspection remarks")


class ProjectResponse(BaseModel):
    """Public representation of a developmental project."""

    id: uuid.UUID
    project_code: str
    constituency_id: uuid.UUID
    district_id: uuid.UUID
    agency_id: Optional[uuid.UUID] = None
    recommended_by_user_id: Optional[uuid.UUID] = None

    title: str
    description: str
    category: str
    priority_quota: str

    estimated_cost: Decimal
    sanctioned_cost: Decimal
    actual_expenditure: Decimal

    status: str
    latitude: Decimal
    longitude: Decimal
    location_address: str

    recommendation_date: date
    sanction_date: Optional[date] = None
    work_order_date: Optional[date] = None
    target_completion_date: date
    actual_completion_date: Optional[date] = None

    delay_risk_score: Decimal
    is_anomaly: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Paginated list of project records."""

    total: int
    page: int
    limit: int
    items: List[ProjectResponse]
