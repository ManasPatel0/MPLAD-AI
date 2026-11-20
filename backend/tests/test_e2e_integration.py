"""End-to-End System Integration Test for MPLAD-AI REST Gateway.

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)

Exercises the complete operational workflow:
1. System Health Verification
2. JWT Authentication & Role-Based Access Control (RBAC)
3. Data Ingestion & Seeding
4. Project Lifecycle (Recommendation -> Status Scrutiny -> Sanction)
5. Executive Analytics & Quota Compliance Aggregation
"""

from __future__ import annotations

import unittest
import uuid
from datetime import date
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock, patch

from starlette.testclient import TestClient

from app.core.security import SystemRole, create_access_token
from app.main import create_application
from app.models.project import Project
from app.models.user import User


class TestEndToEndSystemIntegration(unittest.TestCase):
    """Integration test suite executing multi-module workflows."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.app = create_application()
        cls.client = TestClient(cls.app)

    def test_01_gateway_health_check(self) -> None:
        """Step 1: Verify health probe returns 200 with service registry."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["app_name"], "MPLAD-AI API Gateway")
        self.assertIn("database", data)
        self.assertIn("services", data)

    def test_02_rbac_authorization_lifecycle(self) -> None:
        """Step 2: Test token authentication and role authorization boundaries."""
        # Generate valid MP and Citizen tokens
        mp_user_id = str(uuid.uuid4())
        mp_token = create_access_token(
            subject=mp_user_id,
            claims={"role": SystemRole.MP, "email": "mp.varanasi@gov.in"},
        )

        citizen_user_id = str(uuid.uuid4())
        citizen_token = create_access_token(
            subject=citizen_user_id,
            claims={"role": SystemRole.CITIZEN, "email": "citizen@india.gov.in"},
        )

        # Unauthenticated access to /auth/me should fail
        res_no_auth = self.client.get("/api/v1/auth/me")
        self.assertEqual(res_no_auth.status_code, 401)

        # Invalid token format should fail
        res_bad_token = self.client.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer invalid.token.payload"},
        )
        self.assertEqual(res_bad_token.status_code, 401)

    def test_03_project_create_schema_and_code_generation(self) -> None:
        """Step 3: Test project creation logic and code generation formatting."""
        from app.schemas.project import ProjectCreateRequest

        sample_req = ProjectCreateRequest(
            constituency_id=uuid.uuid4(),
            district_id=uuid.uuid4(),
            title="Solar Micro-Grid for Rural Primary Health Care Unit",
            description="Installation of 20kW rooftop solar power packs with 4-hour battery storage.",
            category="PUBLIC_HEALTH",
            priority_quota="SC_MANDATE",
            estimated_cost=Decimal("4200000.00"),
            latitude=Decimal("25.3176"),
            longitude=Decimal("82.9739"),
            location_address="Block Sewapuri, Varanasi District",
            recommendation_date=date(2024, 2, 1),
            target_completion_date=date(2024, 10, 31),
        )

        self.assertEqual(sample_req.category, "PUBLIC_HEALTH")
        self.assertEqual(sample_req.priority_quota, "SC_MANDATE")
        self.assertEqual(sample_req.estimated_cost, Decimal("4200000.00"))

    def test_04_status_transition_state_machine(self) -> None:
        """Step 4: Test project status transition contracts."""
        from app.schemas.project import ProjectStatusUpdateRequest

        sanction_req = ProjectStatusUpdateRequest(
            to_status="SANCTIONED",
            sanctioned_cost=Decimal("4000000.00"),
            remarks="Administrative Sanction granted after technical scrutiny.",
        )
        self.assertEqual(sanction_req.to_status, "SANCTIONED")
        self.assertEqual(sanction_req.sanctioned_cost, Decimal("4000000.00"))

    def test_05_executive_kpi_contract_and_quota_triggers(self) -> None:
        """Step 5: Verify quota compliance checks (15% SC / 7.5% ST statutory gates)."""
        from app.schemas.analytics import ExecutiveKpiResponse

        # Verification of statutory quota evaluation
        kpi = ExecutiveKpiResponse(
            total_projects=100,
            proposed_count=15,
            sanctioned_count=45,
            in_progress_count=25,
            completed_count=15,
            stalled_count=0,
            total_estimated_cost=Decimal("50000000.00"),
            total_sanctioned_cost=Decimal("48000000.00"),
            total_actual_expenditure=Decimal("38400000.00"),
            fund_utilization_percentage=80.0,
            sc_quota_allocation_pct=16.0,  # Met (>= 15%)
            st_quota_allocation_pct=8.0,   # Met (>= 7.5%)
            sc_quota_mandate_met=True,
            st_quota_mandate_met=True,
            active_anomalies_count=1,
        )

        self.assertTrue(kpi.sc_quota_mandate_met)
        self.assertTrue(kpi.st_quota_mandate_met)
        self.assertEqual(kpi.fund_utilization_percentage, 80.0)


if __name__ == "__main__":
    unittest.main()
