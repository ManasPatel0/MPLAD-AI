"""MPLADS Annual Fund Accounting ORM Model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.constituency import Constituency


class MPLADSFund(Base):
    __tablename__ = "mplads_funds"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    constituency_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("constituencies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    fiscal_year: Mapped[str] = mapped_column(String(16), nullable=False)  # e.g., '2026-2027'
    total_entitlement: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), default=Decimal("50000000.00"), nullable=False
    )
    released_by_mospi: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    sanctioned_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    expenditure_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    sc_expenditure_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    st_expenditure_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    __table_args__ = (
        UniqueConstraint("constituency_id", "fiscal_year", name="uq_constituency_fiscal"),
    )

    # Relationships
    constituency: Mapped[Constituency] = relationship("Constituency", back_populates="funds")
