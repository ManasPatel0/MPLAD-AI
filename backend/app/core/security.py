"""Security utilities for JWT token handling, password hashing, and Role-Based Access Control (RBAC).

Smart India Hackathon 2026 | Problem Statement ID: 26102
Ministry of Statistics and Programme Implementation (MoSPI)
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Callable, Dict, List, Optional
import uuid

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db

logger = logging.getLogger("mplad_ai.security")

# Cryptographic password hashing context (using secure PBKDF2-SHA256 for cross-platform reliability)
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

# HTTP Bearer authentication scheme
security_bearer = HTTPBearer(auto_error=False)


# Standard System Roles
class SystemRole:
    MOSPI_ADMIN = "MOSPI_ADMIN"
    DISTRICT_COLLECTOR = "DISTRICT_COLLECTOR"
    MP = "MP"
    AUDITOR = "AUDITOR"
    IMPLEMENTING_AGENCY = "IMPLEMENTING_AGENCY"
    CITIZEN = "CITIZEN"

    ALL_ROLES = [
        MOSPI_ADMIN,
        DISTRICT_COLLECTOR,
        MP,
        AUDITOR,
        IMPLEMENTING_AGENCY,
        CITIZEN,
    ]


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a raw plain-text password against a stored hash."""
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as exc:
        logger.warning("Password verification failure: %s", exc)
        return False


def get_password_hash(password: str) -> str:
    """Generate a secure cryptographic password hash."""
    return pwd_context.hash(password)


def create_access_token(
    subject: str,
    claims: Optional[Dict[str, Any]] = None,
    expires_delta: Optional[timedelta] = None,
) -> str:
    """Generate a signed JWT access token for authentication."""
    try:
        from jose import jwt
    except ImportError:
        import jwt  # type: ignore

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode: Dict[str, Any] = {
        "sub": subject,
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    if claims:
        to_encode.update(claims)

    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return str(encoded_jwt)


def decode_access_token(token: str) -> Dict[str, Any]:
    """Decode and validate a signed JWT access token."""
    try:
        from jose import JWTError, jwt
    except ImportError:
        import jwt  # type: ignore
        from jwt import PyJWTError as JWTError  # type: ignore

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        return payload
    except JWTError as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials or token expired.",
            headers={"WWW-Authenticate": "Bearer"},
        ) from err


async def get_current_user(
    auth_credentials: Optional[HTTPAuthorizationCredentials] = Depends(security_bearer),
    db: AsyncSession = Depends(get_db),
) -> Any:
    """Dependency retrieving the authenticated User model from bearer JWT."""
    if not auth_credentials or not auth_credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing Authorization header or Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = auth_credentials.credentials
    payload = decode_access_token(token)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject identity.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_uuid = uuid.UUID(user_id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user token format.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    from app.models.user import User

    stmt = select(User).where(User.id == user_uuid)
    result = await db.execute(stmt)
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User associated with token not found.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def get_current_active_user(
    current_user: Any = Depends(get_current_user),
) -> Any:
    """Dependency verifying that the user account is active."""
    if not getattr(current_user, "is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user account. Contact MoSPI Administrator.",
        )
    return current_user


def require_roles(allowed_roles: List[str]) -> Callable:
    """Role-Based Access Control (RBAC) dependency factory."""

    async def role_checker(
        current_user: Any = Depends(get_current_active_user),
    ) -> Any:
        user_role = getattr(current_user, "role", None)
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"Access denied: Role '{user_role}' does not have permission for this resource. "
                    f"Allowed roles: {allowed_roles}"
                ),
            )
        return current_user

    return role_checker
