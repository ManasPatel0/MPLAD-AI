"""Unit tests for Neon Cloud PostgreSQL database configuration, URL normalization, and pooling."""

from __future__ import annotations

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.core.config import Settings, normalize_database_url
from app.core.database import get_engine, mask_db_url, reset_engine


class TestDatabaseConfiguration(unittest.TestCase):
    """Test suite covering database URL normalization and settings defaults."""

    def setUp(self) -> None:
        reset_engine()

    def tearDown(self) -> None:
        reset_engine()

    def test_normalize_database_url_schemes(self) -> None:
        """Verify driver prefix normalization for asyncpg and sync drivers."""
        # Async conversions
        neon_raw = "postgres://user:pass@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb"
        self.assertEqual(
            normalize_database_url(neon_raw, is_async=True),
            "postgresql+asyncpg://user:pass@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb?ssl=require",
        )

        std_postgres = "postgresql://user:pass@localhost:5432/testdb"
        self.assertEqual(
            normalize_database_url(std_postgres, is_async=True),
            "postgresql+asyncpg://user:pass@localhost:5432/testdb",
        )

        psycopg2_url = "postgresql+psycopg2://user:pass@localhost:5432/testdb"
        self.assertEqual(
            normalize_database_url(psycopg2_url, is_async=True),
            "postgresql+asyncpg://user:pass@localhost:5432/testdb",
        )

        # Sync conversions
        self.assertEqual(
            normalize_database_url("postgres://user:pass@localhost:5432/testdb", is_async=False),
            "postgresql://user:pass@localhost:5432/testdb",
        )
        self.assertEqual(
            normalize_database_url(
                "postgresql+asyncpg://user:pass@localhost:5432/testdb", is_async=False
            ),
            "postgresql://user:pass@localhost:5432/testdb",
        )

    def test_normalize_database_url_sslmode_translation(self) -> None:
        """Verify sslmode=require from Neon is translated to ssl=require for asyncpg."""
        url_with_sslmode = (
            "postgresql://user:pass@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb?sslmode=require"
        )
        normalized = normalize_database_url(url_with_sslmode, is_async=True)
        self.assertEqual(
            normalized,
            "postgresql+asyncpg://user:pass@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb?ssl=require",
        )

    def test_settings_defaults_and_validation(self) -> None:
        """Verify default connection timeout is 10.0 seconds and validator normalizes URLs."""
        s = Settings(
            DATABASE_URL="postgresql://user:secret@ep-demo-123456.us-east-2.aws.neon.tech/neondb?sslmode=require",
            DATABASE_SYNC_URL="postgres://user:secret@ep-demo-123456.us-east-2.aws.neon.tech/neondb?sslmode=require",
        )
        self.assertEqual(s.DB_CONNECT_TIMEOUT_SECONDS, 10.0)
        self.assertTrue(s.DATABASE_URL.startswith("postgresql+asyncpg://"))
        self.assertIn("ssl=require", s.DATABASE_URL)
        self.assertTrue(s.DATABASE_SYNC_URL.startswith("postgresql://"))

    def test_mask_db_url_redacts_credentials(self) -> None:
        """Verify credentials masking for both direct and pooled Neon URLs."""
        raw_url = "postgresql+asyncpg://neon_user:SuperSecretPassword123@ep-cool-fog-123.us-east-2.aws.neon.tech/neondb?ssl=require"
        masked = mask_db_url(raw_url)
        self.assertNotIn("SuperSecretPassword123", masked)
        self.assertIn("neon_user:***@ep-cool-fog-123.us-east-2.aws.neon.tech", masked)
        self.assertIn("ssl=require", masked)

        pooled_url = "postgresql+asyncpg://neon_owner:SecretPass456@ep-cool-fog-123-pooler.us-east-2.aws.neon.tech:5432/neondb?ssl=require"
        masked_pooled = mask_db_url(pooled_url)
        self.assertNotIn("SecretPass456", masked_pooled)
        self.assertIn("neon_owner:***@ep-cool-fog-123-pooler.us-east-2.aws.neon.tech:5432", masked_pooled)


class TestDatabaseEngineAndProbes(unittest.IsolatedAsyncioTestCase):
    """Test suite covering engine instantiation parameters and probe diagnostics using mocks."""

    def setUp(self) -> None:
        reset_engine()

    def tearDown(self) -> None:
        reset_engine()

    @patch("sqlalchemy.ext.asyncio.create_async_engine")
    @patch("sqlalchemy.ext.asyncio.async_sessionmaker")
    def test_get_engine_neon_pooler_arguments(
        self, mock_sessionmaker: MagicMock, mock_create_engine: MagicMock
    ) -> None:
        """Verify pool_pre_ping, pool_recycle, timeout, and statement_cache_size for pooled connections."""
        mock_engine = MagicMock()
        mock_create_engine.return_value = mock_engine

        test_pooler_url = (
            "postgresql+asyncpg://user:pass@ep-test-123-pooler.us-east-2.aws.neon.tech/neondb?ssl=require"
        )

        with patch("app.core.database.settings.DATABASE_URL", test_pooler_url), \
             patch("app.core.database.settings.DB_CONNECT_TIMEOUT_SECONDS", 10.0):
            engine = get_engine()
            self.assertIsNotNone(engine)

            mock_create_engine.assert_called_once()
            _, kwargs = mock_create_engine.call_args

            self.assertTrue(kwargs.get("pool_pre_ping"))
            self.assertEqual(kwargs.get("pool_recycle"), 300)
            connect_args = kwargs.get("connect_args", {})
            self.assertEqual(connect_args.get("timeout"), 10.0)
            # Must disable statement caching on pooled PgBouncer endpoint
            self.assertEqual(connect_args.get("statement_cache_size"), 0)
            self.assertEqual(connect_args.get("prepared_statement_cache_size"), 0)
            self.assertEqual(connect_args.get("ssl"), "require")

    @patch("app.core.database.get_engine")
    async def test_check_db_connection_success(self, mock_get_engine: MagicMock) -> None:
        """Verify check_db_connection reports connected when query returns 1."""
        from app.core.database import check_db_connection

        mock_conn = AsyncMock()
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1
        mock_conn.execute.return_value = mock_result

        # Async context manager mock for engine.connect()
        mock_engine = MagicMock()
        mock_engine.dialect.driver = "asyncpg"
        mock_engine.connect.return_value.__aenter__.return_value = mock_conn
        mock_get_engine.return_value = mock_engine

        status = await check_db_connection()
        self.assertEqual(status["status"], "connected")
        self.assertEqual(status["dialect"], "postgresql")
        self.assertIn("connection established", status["message"])

    @patch("app.core.database.get_engine")
    async def test_check_db_connection_graceful_failure(self, mock_get_engine: MagicMock) -> None:
        """Verify check_db_connection reports disconnected gracefully when offline."""
        from app.core.database import check_db_connection

        mock_engine = MagicMock()
        mock_engine.connect.side_effect = Exception("Connection timed out to Neon cloud")
        mock_get_engine.return_value = mock_engine

        status = await check_db_connection()
        self.assertEqual(status["status"], "disconnected")
        self.assertIn("Development standalone mode active", status["message"])
        self.assertIn("Connection timed out", status["error_detail"])


if __name__ == "__main__":
    unittest.main()
