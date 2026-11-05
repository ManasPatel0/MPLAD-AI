"""AI Risk Assessment ORM Model."""

from __future__ import annotations

import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING
from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, utc_now

if TYPE_CHECKING:
    from app.models.project import Project


class AIRiskAssessment(Base):
    __tablename__ = "ai_risk_assessments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    risk_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"), nullable=False)  # 0 to 100
    risk_level: Mapped[str] = mapped_column(
        String(32), default="LOW", nullable=False, index=True
    )  # 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL'

    predicted_delay_days: Mapped[Decimal] = mapped_column(Numeric(6, 1), default=Decimal("0.0"))
    delay_probability: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.000"))

    duplicate_detected: Mapped[bool] = mapped_column(Boolean, default=False)
    duplicate_ref_project_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="SET NULL"), nullable=True
    )
    duplicate_similarity_score: Mapped[Decimal] = mapped_column(Numeric(4, 3), default=Decimal("0.000"))

    cost_anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False)
    cost_variance_zscore: Mapped[Decimal] = mapped_column(Numeric(6, 2), default=Decimal("0.00"))

    payment_anomaly_flag: Mapped[bool] = mapped_column(Boolean, default=False)

    anomaly_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    xai_explanation: Mapped[str | None] = mapped_column(Text, nullable=True)  # Plain text reason why flagged
    recommended_action: Mapped[str | None] = mapped_column(Text, nullable=True)

    factor_breakdown: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utc_now)

    # Relationships
    project: Mapped[Project] = relationship("Project", back_populates="ai_assessments", foreign_keys=[project_id])
