"""Unit tests for Authentication, Password Security, JWT Tokens, and Role-Based Access Control (RBAC).

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

import unittest
import uuid
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi import HTTPException, status

from app.core.security import (
    SystemRole,
    create_access_token,
    decode_access_token,
    get_password_hash,
    require_roles,
    verify_password,
)
from app.models.user import User


class TestSecurityAndRBAC(unittest.TestCase):
    """Test suite for cryptographic security utilities and RBAC role checks."""

    def test_password_hashing_and_verification(self) -> None:
        """Verify that plain passwords generate unique hashes and verify correctly."""
        plain_pw = "MoSPI@Secure2026!"
        hashed = get_password_hash(plain_pw)

        self.assertNotEqual(plain_pw, hashed)
        self.assertTrue(verify_password(plain_pw, hashed))
        self.assertFalse(verify_password("WrongPassword123", hashed))

    def test_jwt_token_creation_and_decoding(self) -> None:
        """Verify JWT token encoding, signature, and claims extraction."""
        test_uuid = str(uuid.uuid4())
        token = create_access_token(
            subject=test_uuid,
            claims={"role": SystemRole.DISTRICT_COLLECTOR, "email": "collector@varanasi.gov.in"},
            expires_delta=timedelta(minutes=15),
        )

        decoded = decode_access_token(token)
        self.assertEqual(decoded["sub"], test_uuid)
        self.assertEqual(decoded["role"], SystemRole.DISTRICT_COLLECTOR)
        self.assertEqual(decoded["email"], "collector@varanasi.gov.in")
        self.assertIn("exp", decoded)

    def test_jwt_invalid_token_raises_401(self) -> None:
        """Verify that malformed or tampered tokens raise HTTP 401."""
        with self.assertRaises(HTTPException) as ctx:
            decode_access_token("invalid.token.payload")
        self.assertEqual(ctx.exception.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_rbac_role_checker_permitted(self) -> None:
        """Verify that a user with an allowed role passes the RBAC dependency."""
        checker = require_roles([SystemRole.DISTRICT_COLLECTOR, SystemRole.MOSPI_ADMIN])

        mock_user = MagicMock(spec=User)
        mock_user.role = SystemRole.DISTRICT_COLLECTOR
        mock_user.is_active = True

        import asyncio

        result = asyncio.run(checker(current_user=mock_user))
        self.assertEqual(result, mock_user)

    def test_rbac_role_checker_forbidden(self) -> None:
        """Verify that a user with an unauthorized role is blocked with HTTP 403."""
        checker = require_roles([SystemRole.MOSPI_ADMIN])

        mock_user = MagicMock(spec=User)
        mock_user.role = SystemRole.CITIZEN
        mock_user.is_active = True

        import asyncio

        with self.assertRaises(HTTPException) as ctx:
            asyncio.run(checker(current_user=mock_user))
        self.assertEqual(ctx.exception.status_code, status.HTTP_403_FORBIDDEN)
        self.assertIn("Access denied", ctx.exception.detail)


if __name__ == "__main__":
    unittest.main()
