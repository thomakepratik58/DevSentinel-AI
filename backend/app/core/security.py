"""Security utilities — password hashing and JWT token operations.

All cryptographic operations are centralised here so the rest of the
codebase never touches raw secrets or algorithm parameters directly.

Design decisions:
  - Argon2id for password hashing (OWASP recommended, memory-hard).
  - HS256 JWTs for access tokens (short-lived, 15 min default).
  - SHA-256 hash of the raw refresh token stored in DB — never the raw value.
  - Refresh tokens are opaque random strings (secrets.token_urlsafe).
"""

from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError

from app.core.config import settings
from app.core.errors import UnauthorizedError

# ── Argon2id configuration ──────────────────────────────────────
#
# These parameters meet OWASP minimum recommendations for Argon2id.
# time_cost=2, memory_cost=65536 (64 MiB), parallelism=2
#
_hasher = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
)


def hash_password(plain_text: str) -> str:
    """Return an Argon2id hash of the given plain-text password.

    The returned string is safe to store directly in the database;
    it encodes the algorithm parameters and salt.
    """
    return _hasher.hash(plain_text)


def verify_password(plain_text: str, hashed: str) -> bool:
    """Return True if *plain_text* matches the stored *hashed* value.

    Returns False (never raises) on any mismatch so callers always
    get a boolean and handle login failure consistently.
    """
    try:
        return _hasher.verify(hashed, plain_text)
    except (VerifyMismatchError, InvalidHashError, Exception):
        return False


# ── JWT access tokens ───────────────────────────────────────────

_ALGORITHM = "HS256"
_TOKEN_TYPE = "Bearer"


def create_access_token(
    subject: str,
    *,
    extra_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    """Issue a signed JWT access token.

    Args:
        subject:      The user's UUID as a string (stored in ``sub``).
        extra_claims: Optional additional claims merged into the payload.
        expires_delta: Override the default expiry from settings.

    Returns:
        A compact, URL-safe JWT string.
    """
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": now,
        "exp": expire,
        "type": "access",
    }
    if extra_claims:
        payload.update(extra_claims)

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=_ALGORITHM)


def decode_access_token(token: str) -> dict[str, Any]:
    """Decode and verify a JWT access token.

    Raises:
        UnauthorizedError: If the token is expired, malformed, or has
                           an invalid signature.  Never leaks internals.
    """
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[_ALGORITHM],
        )
        if payload.get("type") != "access":
            raise UnauthorizedError("Invalid token type.")
        return payload
    except jwt.ExpiredSignatureError:
        raise UnauthorizedError("Access token has expired.")
    except jwt.InvalidTokenError:
        raise UnauthorizedError("Invalid access token.")


# ── Refresh tokens ──────────────────────────────────────────────


def generate_refresh_token() -> tuple[str, str]:
    """Generate an opaque refresh token and its SHA-256 hash.

    Returns:
        A tuple of (raw_token, token_hash).  Store only the hash in the
        database; deliver the raw token to the client via HttpOnly cookie.
    """
    raw = secrets.token_urlsafe(48)
    token_hash = hashlib.sha256(raw.encode()).hexdigest()
    return raw, token_hash


def hash_refresh_token(raw_token: str) -> str:
    """Return the SHA-256 hex-digest of a raw refresh token."""
    return hashlib.sha256(raw_token.encode()).hexdigest()


# ── Bearer header extraction ────────────────────────────────────


def extract_bearer_token(authorization: str | None) -> str:
    """Parse the raw ``Authorization`` header and return the token.

    Raises:
        UnauthorizedError: If the header is absent or not in
                           ``Bearer <token>`` format.
    """
    if not authorization:
        raise UnauthorizedError("Authorization header is missing.")
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise UnauthorizedError(
            "Authorization header must follow the 'Bearer <token>' format."
        )
    return parts[1]
