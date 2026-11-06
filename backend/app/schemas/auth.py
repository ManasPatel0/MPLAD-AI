"""Pydantic schemas for authentication and user management.

Smart India Hackathon 2026 | Problem Statement ID: 26102
"""

from __future__ import annotations

import re
import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator

from app.core.security import SystemRole

EMAIL_REGEX = re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$")


class UserLoginRequest(BaseModel):
    """Payload for user authentication."""

    email: str = Field(..., description="Registered official email address")
    password: str = Field(..., min_length=6, description="User password")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError(f"Invalid email address format: '{v}'")
        return clean


class UserRegisterRequest(BaseModel):
    """Payload for new user registration."""

    email: str = Field(..., description="Official government or user email")
    password: str = Field(..., min_length=6, description="Password (min 6 characters)")
    full_name: str = Field(..., min_length=2, max_length=128, description="User's full name")
    role: str = Field(
        default=SystemRole.CITIZEN,
        description="Designated system role (MOSPI_ADMIN, DISTRICT_COLLECTOR, MP, AUDITOR, IMPLEMENTING_AGENCY, CITIZEN)",
    )
    constituency_id: Optional[uuid.UUID] = Field(default=None, description="Linked constituency UUID")
    district_id: Optional[uuid.UUID] = Field(default=None, description="Linked district UUID")
    agency_id: Optional[uuid.UUID] = Field(default=None, description="Linked implementing agency UUID")

    @field_validator("email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        clean = v.strip().lower()
        if not EMAIL_REGEX.match(clean):
            raise ValueError(f"Invalid email address format: '{v}'")
        return clean

    @field_validator("role")
    @classmethod
    def validate_role(cls, v: str) -> str:
        role_upper = v.strip().upper()
        if role_upper not in SystemRole.ALL_ROLES:
            raise ValueError(
                f"Invalid role '{v}'. Permitted roles: {SystemRole.ALL_ROLES}"
            )
        return role_upper


class UserResponse(BaseModel):
    """Public representation of user identity."""

    id: uuid.UUID
    email: str
    full_name: str
    role: str
    constituency_id: Optional[uuid.UUID] = None
    district_id: Optional[uuid.UUID] = None
    agency_id: Optional[uuid.UUID] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Token response on successful login or registration."""

    access_token: str
    token_type: str = "bearer"
    user: UserResponse
