"""Geotagged Field Inspection ORM Model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.user import User


class Inspection(Base):
    __tablename__ = "inspections"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    inspector_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    inspection_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    physical_progress_pct: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)
    photo_url: Mapped[str] = mapped_column(Text, nullable=False)
    photo_latitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    photo_longitude: Mapped[Decimal] = mapped_column(Numeric(10, 7), nullable=False)
    geo_distance_meters: Mapped[Decimal | None] = mapped_column(Numeric(8, 2), nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="inspections")
    inspector: Mapped[User | None] = relationship("User")
