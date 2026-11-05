"""Constituency ORM Model for Parliamentary Constituencies."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, List
from decimal import Decimal
from sqlalchemy import Numeric, String, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.user import User
    from app.models.project import Project
    from app.models.fund import MPLADSFund


class Constituency(Base):
    __tablename__ = "constituencies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    code: Mapped[str] = mapped_column(String(32), unique=True, nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    state: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)  # 'LOK_SABHA' or 'RAJYA_SABHA'
    current_mp_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    current_mp_party: Mapped[str | None] = mapped_column(String(64), nullable=True)
    annual_entitlement: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("50000000.00"), nullable=False
    )
    sc_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    st_percentage: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    users: Mapped[List[User]] = relationship("User", back_populates="constituency")
    projects: Mapped[List[Project]] = relationship("Project", back_populates="constituency")
    funds: Mapped[List[MPLADSFund]] = relationship("MPLADSFund", back_populates="constituency")
