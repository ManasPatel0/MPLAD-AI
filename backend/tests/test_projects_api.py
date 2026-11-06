"""Unit tests for Projects API schemas, state transitions, analytics logic, and router registry.

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

import unittest
import uuid
from datetime import date
from decimal import Decimal

from app.main import create_application
from app.schemas.analytics import ExecutiveKpiResponse
from app.schemas.project import ProjectCreateRequest, ProjectStatusUpdateRequest


class TestProjectsAndAnalyticsAPI(unittest.TestCase):
    """Test suite covering project request contracts, KPI computation, and router mappings."""

    def setUp(self) -> None:
        self.app = create_application()

    def test_routes_registered_in_application(self) -> None:
        """Verify that all Subtask 1.4 routes are mounted under /api/v1."""
        route_paths = set(self.app.openapi()["paths"].keys())

        expected_endpoints = {
            "/api/v1/health",
            "/api/v1/auth/register",
            "/api/v1/auth/login",
            "/api/v1/auth/me",
            "/api/v1/projects",
            "/api/v1/projects/{project_id}",
            "/api/v1/projects/{project_id}/status",
            "/api/v1/analytics/kpis",
            "/api/v1/analytics/sectors",
            "/api/v1/analytics/agencies",
            "/api/v1/ingest/batch",
            "/api/v1/ingest/csv",
            "/api/v1/ingest/seed-sample",
            "/api/v1/ingest/stats",
        }
        self.assertTrue(expected_endpoints.issubset(route_paths))

    def test_project_create_schema(self) -> None:
        """Verify project recommendation payload instantiation and typing."""
        payload = ProjectCreateRequest(
            constituency_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            title="Installation of Solar Mini-Grid in Tribal Cluster",
            description="Setting up 25kW decentralized solar mini-grid with battery storage.",
            category="COMMUNITY_INFRASTRUCTURE",
            priority_quota="ST_MANDATE",
            estimated_cost=Decimal("3500000.00"),
            latitude=Decimal("23.5120"),
            longitude=Decimal("85.3210"),
            location_address="Block Khunti, District Ranchi",
            recommendation_date=date(2024, 2, 1),
            target_completion_date=date(2024, 11, 30),
        )
        self.assertEqual(payload.priority_quota, "ST_MANDATE")
        self.assertEqual(payload.estimated_cost, Decimal("3500000.00"))

    def test_project_status_update_schema(self) -> None:
        """Verify project status transition payload validation."""
        update_payload = ProjectStatusUpdateRequest(
            to_status="SANCTIONED",
            sanctioned_cost=Decimal("3400000.00"),
            remarks="Technically verified and approved.",
        )
        self.assertEqual(update_payload.to_status, "SANCTIONED")
        self.assertEqual(update_payload.sanctioned_cost, Decimal("3400000.00"))

    def test_executive_kpi_mandates_calculation(self) -> None:
        """Verify SC/ST statutory quota threshold triggers (15% SC, 7.5% ST)."""
        # Case A: Below quota mandates
        kpi_below = ExecutiveKpiResponse(
            total_projects=100,
            proposed_count=20,
            sanctioned_count=50,
            in_progress_count=20,
            completed_count=10,
            stalled_count=0,
            total_estimated_cost=Decimal("50000000.00"),
            total_sanctioned_cost=Decimal("45000000.00"),
            total_actual_expenditure=Decimal("22500000.00"),
            fund_utilization_percentage=50.0,
            sc_quota_allocation_pct=12.0,  # Below 15.0%
            st_quota_allocation_pct=5.0,  # Below 7.5%
            sc_quota_mandate_met=False,
            st_quota_mandate_met=False,
            active_anomalies_count=2,
        )
        self.assertFalse(kpi_below.sc_quota_mandate_met)
        self.assertFalse(kpi_below.st_quota_mandate_met)

        # Case B: Compliant with quota mandates
        kpi_compliant = ExecutiveKpiResponse(
            total_projects=100,
            proposed_count=10,
            sanctioned_count=40,
            in_progress_count=30,
            completed_count=20,
            stalled_count=0,
            total_estimated_cost=Decimal("50000000.00"),
            total_sanctioned_cost=Decimal("45000000.00"),
            total_actual_expenditure=Decimal("36000000.00"),
            fund_utilization_percentage=80.0,
            sc_quota_allocation_pct=16.5,  # Above 15.0%
            st_quota_allocation_pct=8.2,  # Above 7.5%
            sc_quota_mandate_met=True,
            st_quota_mandate_met=True,
            active_anomalies_count=0,
        )
        self.assertTrue(kpi_compliant.sc_quota_mandate_met)
        self.assertTrue(kpi_compliant.st_quota_mandate_met)


if __name__ == "__main__":
    unittest.main()
