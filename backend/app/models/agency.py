"""Implementing Agency ORM Model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from decimal import Decimal
from sqlalchemy import ForeignKey, Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.district import District
    from app.models.project import Project
    from app.models.user import User


class ImplementingAgency(Base):
    __tablename__ = "implementing_agencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    department: Mapped[str] = mapped_column(String(64), nullable=False)  # PWD, Rural Dev, etc.
    district_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("districts.id", ondelete="SET NULL"), nullable=True
    )
    efficiency_rating: Mapped[Decimal] = mapped_column(Numeric(3, 2), default=Decimal("3.00"))
    avg_historical_delay_days: Mapped[Decimal] = mapped_column(Numeric(6, 1), default=Decimal("0.0"))
    contact_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    district: Mapped[District | None] = relationship("District", back_populates="agencies")
    projects: Mapped[List[Project]] = relationship("Project", back_populates="agency")
    users: Mapped[List[User]] = relationship("User", back_populates="agency")
