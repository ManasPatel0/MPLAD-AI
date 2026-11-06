"""Unit tests for MPLADS Data Ingestion, Schema Validation, and ETL Pipeline.

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal

from pydantic import ValidationError

from app.schemas.ingestion import IngestionSummary, ProjectIngestRecord
from app.services.ingestion_service import MPLADSIngestionService


class TestDataIngestionPipeline(unittest.TestCase):
    """Test suite covering ingestion schema validation, CSV parsing, and seed data integrity."""

    def setUp(self) -> None:
        self.service = MPLADSIngestionService()

    def test_valid_project_schema(self) -> None:
        """Verify that a valid project dictionary produces a valid ProjectIngestRecord."""
        record_data = {
            "project_code": "MPLADS-TEST-001",
            "title": "Community Borewell & Solar Pump Installation",
            "description": "Borewell drilling and 5HP solar pump setup",
            "category": "DRINKING_WATER",
            "priority_quota": "SC_MANDATE",
            "state": "Uttar Pradesh",
            "constituency_code": "PC-UP-77",
            "constituency_name": "Varanasi",
            "district_name": "Varanasi",
            "estimated_cost": Decimal("1500000.00"),
            "sanctioned_cost": Decimal("1450000.00"),
            "latitude": Decimal("25.3176"),
            "longitude": Decimal("82.9739"),
            "recommendation_date": date(2024, 1, 10),
            "target_completion_date": date(2024, 8, 30),
        }
        record = ProjectIngestRecord(**record_data)
        self.assertEqual(record.project_code, "MPLADS-TEST-001")
        self.assertEqual(record.category, "DRINKING_WATER")
        self.assertEqual(record.priority_quota, "SC_MANDATE")
        self.assertEqual(record.status, "PROPOSED")

    def test_invalid_date_chronology(self) -> None:
        """Verify that target_completion_date earlier than recommendation_date is rejected."""
        record_data = {
            "project_code": "MPLADS-INVALID-DATE",
            "title": "Invalid Chronology Project",
            "state": "Delhi",
            "constituency_code": "PC-DL-01",
            "constituency_name": "Chandni Chowk",
            "district_name": "North Delhi",
            "estimated_cost": Decimal("100000.00"),
            "latitude": Decimal("28.6500"),
            "longitude": Decimal("77.2300"),
            "recommendation_date": date(2024, 6, 1),
            "target_completion_date": date(2024, 1, 1),  # Earlier than recommendation
        }
        with self.assertRaises(ValidationError):
            ProjectIngestRecord(**record_data)

    def test_category_normalization_fallback(self) -> None:
        """Verify that unknown categories gracefully fall back to COMMUNITY_INFRASTRUCTURE."""
        record_data = {
            "project_code": "MPLADS-UNKNOWN-CAT",
            "title": "Miscellaneous Project",
            "category": "NON_EXISTENT_CATEGORY",
            "state": "Bihar",
            "constituency_code": "PC-BR-01",
            "constituency_name": "Patna Sahib",
            "district_name": "Patna",
            "estimated_cost": Decimal("500000.00"),
            "latitude": Decimal("25.5941"),
            "longitude": Decimal("85.1376"),
            "recommendation_date": date(2024, 2, 1),
            "target_completion_date": date(2024, 9, 30),
        }
        record = ProjectIngestRecord(**record_data)
        self.assertEqual(record.category, "COMMUNITY_INFRASTRUCTURE")

    def test_csv_stream_parsing(self) -> None:
        """Verify that raw CSV stream is properly parsed into normalized dict records."""
        sample_csv = (
            "project_code,title,category,state,constituency_code,constituency_name,"
            "district_name,estimated_cost,latitude,longitude,recommendation_date,target_completion_date\n"
            "CSV-PROJ-1,Village Road Work,ROADS_BRIDGES,Punjab,PC-PB-03,Jalandhar,Jalandhar,"
            "2000000.00,31.3260,75.5762,2024-01-01,2024-10-31\n"
        )
        parsed = self.service.parse_csv_stream(sample_csv)
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["project_code"], "CSV-PROJ-1")
        self.assertEqual(parsed[0]["category"], "ROADS_BRIDGES")
        self.assertEqual(parsed[0]["state"], "Punjab")

    def test_seed_dataset_validation(self) -> None:
        """Verify that every record in the built-in seed dataset validates cleanly."""
        seed_data = self.service.get_seed_dataset()
        self.assertGreater(len(seed_data), 0)
        for item in seed_data:
            record = ProjectIngestRecord(**item)
            self.assertIsNotNone(record.project_code)
            self.assertIsNotNone(record.title)
            self.assertGreater(record.estimated_cost, 0)
            self.assertGreater(record.target_completion_date, record.recommendation_date)


if __name__ == "__main__":
    unittest.main()
