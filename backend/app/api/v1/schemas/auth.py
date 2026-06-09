"""Pydantic request/response schemas for the authentication API.

Domain models (SQLAlchemy ORM) are kept separate from these API
contracts to maintain a clean boundary between persistence and
the external interface.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator


# ── Request schemas ─────────────────────────────────────────────


class RegisterRequest(BaseModel):
    """Payload for ``POST /auth/register``."""

    email: EmailStr = Field(..., description="User's email address.")
    display_name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Display name shown in the UI.",
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Plain-text password (min 8 chars, never stored raw).",
    )

    @field_validator("password")
    @classmethod
    def password_must_have_minimum_complexity(cls, value: str) -> str:
        """Require at least one letter and one digit."""
        has_letter = any(c.isalpha() for c in value)
        has_digit = any(c.isdigit() for c in value)
        if not (has_letter and has_digit):
            raise ValueError(
                "Password must contain at least one letter and one digit."
            )
        return value

    @field_validator("display_name")
    @classmethod
    def display_name_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("Display name cannot be blank.")
        return value.strip()


class LoginRequest(BaseModel):
    """Payload for ``POST /auth/login``."""

    email: EmailStr = Field(..., description="Registered email address.")
    password: str = Field(..., min_length=1, description="Account password.")


class RefreshRequest(BaseModel):
    """Optional explicit body for ``POST /auth/refresh``.

    The refresh token is preferentially read from the HttpOnly cookie;
    this schema is a fallback for non-browser clients.
    """

    refresh_token: str | None = Field(
        default=None,
        description="Raw refresh token (only used when cookie is unavailable).",
    )


# ── Response schemas ────────────────────────────────────────────


class UserResponse(BaseModel):
    """Public user profile returned from authenticated endpoints."""

    id: uuid.UUID
    email: str
    display_name: str
    avatar_url: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    """Access token issued after successful register or login."""

    access_token: str = Field(..., description="Short-lived JWT access token.")
    token_type: str = Field(default="Bearer")
    expires_in: int = Field(
        ..., description="Seconds until the access token expires."
    )
    user: UserResponse


class RefreshResponse(BaseModel):
    """New access token issued after a valid refresh."""

    access_token: str
    token_type: str = "Bearer"
    expires_in: int


class MessageResponse(BaseModel):
    """Generic success acknowledgement."""

    message: str
