"""User ORM Model supporting Role-Based Access Control (RBAC)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import Boolean, ForeignKey, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.constituency import Constituency
    from app.models.district import District
    from app.models.agency import ImplementingAgency
    from app.models.project import Project


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(String(128), unique=True, nullable=False, index=True)
    password_hash: Mapped[str] = mapped_column(String(256), nullable=False)
    full_name: Mapped[str] = mapped_column(String(128), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        index=True,
    )  # 'MOSPI_ADMIN', 'MP', 'DISTRICT_COLLECTOR', 'IMPLEMENTING_AGENCY', 'AUDITOR', 'CITIZEN'
    constituency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("constituencies.id", ondelete="SET NULL"), nullable=True
    )
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="SET NULL"), nullable=True
    )
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("implementing_agencies.id", ondelete="SET NULL"), nullable=True
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    constituency: Mapped[Constituency | None] = relationship("Constituency", back_populates="users")
    district: Mapped[District | None] = relationship("District", back_populates="users")
    agency: Mapped[ImplementingAgency | None] = relationship("ImplementingAgency", back_populates="users")
    recommended_projects: Mapped[List[Project]] = relationship("Project", back_populates="recommended_by")
