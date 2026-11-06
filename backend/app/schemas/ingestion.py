"""Pydantic validation schemas for MPLADS Data Ingestion and ETL.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Validates incoming project records from CSV, JSON, and official MoSPI portals.
"""

from __future__ import annotations

import re
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator, model_validator


VALID_CATEGORIES = {
    "DRINKING_WATER",
    "EDUCATION",
    "PUBLIC_HEALTH",
    "SANITATION",
    "ROADS_BRIDGES",
    "IRRIGATION",
    "COMMUNITY_INFRASTRUCTURE",
    "OTHER",
}

VALID_STATUSES = {
    "PROPOSED",
    "SCRUTINIZED",
    "SANCTIONED",
    "WORK_ORDERED",
    "IN_PROGRESS",
    "COMPLETED",
    "REJECTED",
    "STALLED",
}

VALID_QUOTAS = {"GENERAL", "SC_MANDATE", "ST_MANDATE"}


class ProjectIngestRecord(BaseModel):
    """Schema representing an individual project record parsed from CSV or JSON."""

    project_code: str = Field(..., description="Unique MPLADS work code (e.g. MP-2024-UP-001)")
    title: str = Field(..., min_length=3, max_length=256, description="Official project title")
    description: str = Field(default="", description="Detailed scope of developmental work")
    category: str = Field(default="COMMUNITY_INFRASTRUCTURE", description="Work category")
    priority_quota: str = Field(default="GENERAL", description="Statutory mandate quota")

    state: str = Field(..., description="State or Union Territory name")
    constituency_code: str = Field(..., description="Unique constituency code (e.g. PC-UP-77)")
    constituency_name: str = Field(..., description="Parliamentary constituency name")
    constituency_type: str = Field(default="LOK_SABHA", description="LOK_SABHA or RAJYA_SABHA")
    mp_name: Optional[str] = Field(default=None, description="Hon'ble MP name")

    district_name: str = Field(..., description="Nodal administrative district name")
    agency_code: Optional[str] = Field(default=None, description="Implementing agency code")
    agency_name: Optional[str] = Field(default=None, description="Implementing agency name (PWD, etc.)")
    agency_dept: Optional[str] = Field(default="Rural Development", description="Agency department")

    estimated_cost: Decimal = Field(..., ge=0, description="Estimated work cost in INR")
    sanctioned_cost: Decimal = Field(default=Decimal("0.00"), ge=0, description="Sanctioned amount in INR")
    actual_expenditure: Decimal = Field(default=Decimal("0.00"), ge=0, description="Cumulative expenditure in INR")

    status: str = Field(default="PROPOSED", description="Lifecycle status")

    latitude: Decimal = Field(..., ge=-90, le=90, description="GPS Latitude (-90 to +90)")
    longitude: Decimal = Field(..., ge=-180, le=180, description="GPS Longitude (-180 to +180)")
    location_address: str = Field(default="", description="Village, Ward or Landmark address")

    recommendation_date: date = Field(..., description="Date MP recommended the work")
    sanction_date: Optional[date] = Field(default=None, description="Date District Authority sanctioned work")
    work_order_date: Optional[date] = Field(default=None, description="Date work order was issued")
    target_completion_date: date = Field(..., description="Target completion deadline")
    actual_completion_date: Optional[date] = Field(default=None, description="Actual completion date if finished")

    @field_validator("project_code")
    @classmethod
    def clean_project_code(cls, v: str) -> str:
        cleaned = re.sub(r"\s+", "-", v.strip().upper())
        if not cleaned:
            raise ValueError("project_code cannot be empty")
        return cleaned

    @field_validator("category")
    @classmethod
    def validate_category(cls, v: str) -> str:
        normalized = v.strip().upper().replace(" ", "_")
        if normalized not in VALID_CATEGORIES:
            return "COMMUNITY_INFRASTRUCTURE"
        return normalized

    @field_validator("priority_quota")
    @classmethod
    def validate_quota(cls, v: str) -> str:
        normalized = v.strip().upper().replace(" ", "_")
        if normalized not in VALID_QUOTAS:
            return "GENERAL"
        return normalized

    @field_validator("status")
    @classmethod
    def validate_status(cls, v: str) -> str:
        normalized = v.strip().upper().replace(" ", "_")
        if normalized not in VALID_STATUSES:
            return "PROPOSED"
        return normalized

    @model_validator(mode="after")
    def validate_chronology_and_costs(self) -> ProjectIngestRecord:
        # Fill description with title if blank
        if not self.description:
            self.description = self.title

        # Validate date chronology
        if self.target_completion_date < self.recommendation_date:
            raise ValueError(
                f"target_completion_date ({self.target_completion_date}) cannot be earlier than "
                f"recommendation_date ({self.recommendation_date})"
            )
        return self


class IngestionSummary(BaseModel):
    """Response returned upon completion of an ingestion run."""

    status: str = Field(default="success")
    batch_id: str
    total_records: int
    inserted_records: int
    updated_records: int
    failed_records: int
    constituencies_created: int
    districts_created: int
    agencies_created: int
    errors: List[Dict[str, Any]] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
