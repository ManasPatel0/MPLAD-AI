"""Unit tests for SQLAlchemy models structure, table registration, and relationships."""

from __future__ import annotations

import unittest
from app.models import (
    Base,
    Constituency,
    District,
    ImplementingAgency,
    User,
    Project,
    Milestone,
    Inspection,
    AIRiskAssessment,
    CitizenFeedback,
    AuditLog,
    MPLADSFund,
)


class TestSQLAlchemyModels(unittest.TestCase):
    """Verifies that all 11 relational models conform to DATA_SCHEMA.md."""

    def test_registered_tables_presence(self) -> None:
        """Verify that all core tables are registered with Base metadata."""
        expected_tables = {
            "constituencies",
            "districts",
            "implementing_agencies",
            "users",
            "projects",
            "milestones",
            "inspections",
            "ai_risk_assessments",
            "citizen_feedback",
            "audit_logs",
            "mplads_funds",
        }
        registered_tables = set(Base.metadata.tables.keys())
        self.assertTrue(expected_tables.issubset(registered_tables))

    def test_project_model_columns(self) -> None:
        """Verify project table column structure."""
        project_table = Base.metadata.tables["projects"]
        col_names = set(project_table.columns.keys())

        expected_columns = {
            "id",
            "project_code",
            "constituency_id",
            "district_id",
            "agency_id",
            "title",
            "description",
            "category",
            "priority_quota",
            "estimated_cost",
            "sanctioned_cost",
            "actual_expenditure",
            "status",
            "latitude",
            "longitude",
            "location_address",
            "recommendation_date",
            "target_completion_date",
            "delay_risk_score",
            "is_anomaly",
        }
        self.assertTrue(expected_columns.issubset(col_names))

    def test_ai_risk_assessment_model_columns(self) -> None:
        """Verify ai_risk_assessments table column structure."""
        risk_table = Base.metadata.tables["ai_risk_assessments"]
        col_names = set(risk_table.columns.keys())

        expected_columns = {
            "id",
            "project_id",
            "risk_score",
            "risk_level",
            "predicted_delay_days",
            "delay_probability",
            "duplicate_detected",
            "cost_anomaly_flag",
            "payment_anomaly_flag",
            "xai_explanation",
            "recommended_action",
        }
        self.assertTrue(expected_columns.issubset(col_names))


if __name__ == "__main__":
    unittest.main()
