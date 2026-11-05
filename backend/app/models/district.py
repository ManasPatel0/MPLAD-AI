"""District ORM Model for administrative districts."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from sqlalchemy import String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.project import Project
    from app.models.agency import ImplementingAgency
    from app.models.user import User


class District(Base):
    __tablename__ = "districts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(128), nullable=False, index=True)
    state: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    nodal_officer_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nodal_officer_email: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nodal_officer_phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    agencies: Mapped[List[ImplementingAgency]] = relationship("ImplementingAgency", back_populates="district")
    projects: Mapped[List[Project]] = relationship("Project", back_populates="district")
    users: Mapped[List[User]] = relationship("User", back_populates="district")
