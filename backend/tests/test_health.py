"""Unit tests for the health check and diagnostic endpoint."""

import unittest
from starlette.testclient import TestClient

from app.main import app


class TestHealthEndpoint(unittest.TestCase):
    """Verifies that the /api/v1/health endpoint adheres to Phase 1 contracts."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_root_endpoint_returns_200(self) -> None:
        """Root endpoint should return 200 with service metadata."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertEqual(data.get("status"), "online")
        self.assertEqual(data.get("health_check"), "/api/v1/health")

    def test_health_endpoint_returns_200(self) -> None:
        """GET /api/v1/health should respond with HTTP 200 OK."""
        response = self.client.get("/api/v1/health")
        self.assertEqual(response.status_code, 200)

    def test_health_endpoint_payload_structure(self) -> None:
        """Verify the health response adheres to the required contract keys."""
        response = self.client.get("/api/v1/health")
        data = response.json()

        self.assertEqual(data.get("status"), "healthy")
        self.assertIn("app_name", data)
        self.assertIn("version", data)
        self.assertIn("environment", data)
        self.assertIn("timestamp", data)
        self.assertIn("database", data)
        self.assertIn("services", data)
        self.assertIn("python_version", data)

        # Database health payload check
        db_info = data["database"]
        self.assertIn("status", db_info)
        self.assertIn(db_info["status"], ["connected", "disconnected"])
        self.assertEqual(db_info.get("dialect"), "postgresql")

        # Services readiness check
        services = data["services"]
        self.assertEqual(services.get("api_gateway"), "online")
        self.assertEqual(services.get("ml_engine"), "phase_1_standby")

    def test_standard_404_error_contract(self) -> None:
        """Verify unmapped routes return standardized error JSON matching API_CONTRACTS.md."""
        response = self.client.get("/api/v1/nonexistent-route")
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn("detail", data)
        self.assertEqual(data.get("error_code"), "RESOURCE_NOT_FOUND")
        self.assertIn("timestamp", data)


if __name__ == "__main__":
    unittest.main()
