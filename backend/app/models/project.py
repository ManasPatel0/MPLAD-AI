"""Project ORM Model representing developmental works under MPLADS."""

from __future__ import annotations

import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.constituency import Constituency
    from app.models.district import District
    from app.models.agency import ImplementingAgency
    from app.models.user import User
    from app.models.milestone import Milestone
    from app.models.inspection import Inspection
    from app.models.ai_risk import AIRiskAssessment
    from app.models.citizen import CitizenFeedback
    from app.models.audit_log import AuditLog


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("constituencies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    district_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("implementing_agencies.id", ondelete="SET NULL"), nullable=True
    )
    recommended_by_user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(256), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    category: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # 'DRINKING_WATER', 'EDUCATION', 'PUBLIC_HEALTH', 'SANITATION', 'ROADS_BRIDGES', 'IRRIGATION', 'COMMUNITY_INFRASTRUCTURE', 'OTHER'
    priority_quota: Mapped[str] = mapped_column(
        String(32), nullable=False, default="GENERAL"
    )  # 'GENERAL', 'SC_MANDATE', 'ST_MANDATE'

    estimated_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), nullable=False)
    sanctioned_cost: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    actual_expenditure: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))

    status: Mapped[str] = mapped_column(
        String(32), default="PROPOSED", nullable=False, index=True
    )  # 'PROPOSED', 'SCRUTINIZED', 'SANCTIONED', 'WORK_ORDERED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED', 'STALLED'

    latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    location_address: Mapped[str] = mapped_column(Text, nullable=False)

    recommendation_date: Mapped[date] = mapped_column(Date, nullable=False)
    sanction_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    work_order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    actual_completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    delay_risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))  # 0 to 100
    is_anomaly: Mapped[bool] = mapped_column(Boolean, default=False, index=True)

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    constituency: Mapped[Constituency] = relationship("Constituency", back_populates="projects")
    district: Mapped[District] = relationship("District", back_populates="projects")
    agency: Mapped[ImplementingAgency | None] = relationship("ImplementingAgency", back_populates="projects")
    recommended_by: Mapped[User | None] = relationship("User", back_populates="recommended_projects")

    milestones: Mapped[List[Milestone]] = relationship("Milestone", back_populates="project", cascade="all, delete-orphan")
    inspections: Mapped[List[Inspection]] = relationship("Inspection", back_populates="project", cascade="all, delete-orphan")
    ai_assessments: Mapped[List[AIRiskAssessment]] = relationship("AIRiskAssessment", back_populates="project", cascade="all, delete-orphan")
    feedback: Mapped[List[CitizenFeedback]] = relationship("CitizenFeedback", back_populates="project", cascade="all, delete-orphan")
    audit_logs: Mapped[List[AuditLog]] = relationship("AuditLog", back_populates="project", cascade="all, delete-orphan")
