"""Authentication and user identity service.

Coordinates all auth use cases:
  - Email/password registration with automatic workspace creation
  - Login with refresh token issuance
  - Logout (single-session revocation)
  - Refresh token rotation (revoke old → issue new)
  - Current user profile retrieval

Design rules followed (per instructions.md):
  - Services enforce business rules; routes stay thin.
  - Passwords are never returned or logged.
  - Refresh tokens are stored as SHA-256 hashes — raw tokens only
    travel to the client over HttpOnly cookies.
  - Every auth event writes to the audit log.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import NamedTuple

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.errors import ConflictError, UnauthorizedError
from app.core.logging import logger
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repo import UserRepository
from app.repositories.workspace_repo import WorkspaceRepository


class AuthTokenPair(NamedTuple):
    """Pair of issued tokens returned after a successful auth event."""

    access_token: str
    raw_refresh_token: str
    expires_in: int  # seconds until access token expires


class AuthService:
    """Handles all authentication and user identity operations.

    Instantiate with an active ``AsyncSession``; the service manages
    its own repository instances and flushes/commits as needed.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._user_repo = UserRepository(session)
        self._workspace_repo = WorkspaceRepository(session)

    # ── Registration ─────────────────────────────────────────────

    async def register_user(
        self,
        *,
        email: str,
        display_name: str,
        password: str,
    ) -> tuple[User, AuthTokenPair]:
        """Register a new user and provision a default workspace.

        Args:
            email:        Must be unique across all accounts.
            display_name: Shown in the UI; trimmed of whitespace.
            password:     Plain-text — hashed before any persistence.

        Returns:
            (user, token_pair) ready to be sent to the client.

        Raises:
            ConflictError: If the email is already registered.
        """
        existing = await self._user_repo.get_by_email(email.lower())
        if existing is not None:
            raise ConflictError(
                "An account with this email address already exists.",
                error_code="email_already_registered",
            )

        password_hash = hash_password(password)

        user = await self._user_repo.create_user(
            email=email.lower(),
            display_name=display_name.strip(),
            password_hash=password_hash,
        )

        # Every user starts with a personal workspace
        workspace_name = f"{display_name.strip()}'s Workspace"
        await self._workspace_repo.create_workspace(
            name=workspace_name,
            owner_id=user.id,
        )
        await self._session.commit()

        logger.info(
            "user_registered  user_id=%s  email=%s",
            user.id,
            user.email,
        )

        token_pair = await self._issue_token_pair(user.id)
        return user, token_pair

    # ── Login ─────────────────────────────────────────────────────

    async def login_user(
        self,
        *,
        email: str,
        password: str,
    ) -> tuple[User, AuthTokenPair]:
        """Authenticate a user with email and password.

        Deliberately returns the same error for wrong email and wrong
        password to prevent user enumeration.

        Returns:
            (user, token_pair) on success.

        Raises:
            UnauthorizedError: On any credential mismatch or inactive account.
        """
        _invalid_credentials_message = (
            "The email address or password is incorrect."
        )

        user = await self._user_repo.get_by_email(email.lower())
        if user is None:
            # Time-constant failure — prevents timing attacks
            hash_password("dummy_constant_work")
            raise UnauthorizedError(_invalid_credentials_message)

        if not user.is_active:
            raise UnauthorizedError(
                "This account has been deactivated. Contact support if you "
                "believe this is an error."
            )

        if user.password_hash is None or not verify_password(
            password, user.password_hash
        ):
            raise UnauthorizedError(_invalid_credentials_message)

        await self._user_repo.update_last_login(user.id)
        await self._session.commit()

        logger.info("user_login  user_id=%s", user.id)

        token_pair = await self._issue_token_pair(user.id)
        return user, token_pair

    # ── Logout ────────────────────────────────────────────────────

    async def logout_user(
        self,
        *,
        user_id: uuid.UUID,
        raw_refresh_token: str,
    ) -> None:
        """Revoke a single refresh token session.

        Silently succeeds if the token is already revoked or expired,
        so double-logout calls are safe.
        """
        token_hash = hash_refresh_token(raw_refresh_token)
        await self._user_repo.revoke_refresh_token(token_hash)
        await self._session.commit()
        logger.info("user_logout  user_id=%s", user_id)

    # ── Token refresh ─────────────────────────────────────────────

    async def refresh_access_token(
        self,
        *,
        raw_refresh_token: str,
    ) -> AuthTokenPair:
        """Rotate a refresh token and issue a new access token.

        Rotation strategy:
          1. Validate the incoming token (hash lookup, expiry, revoked check).
          2. Revoke the old token immediately.
          3. Issue a new access token + new refresh token.

        This ensures each refresh token can only be used once, and any
        replay of a revoked token surfaces as an auth failure.

        Raises:
            UnauthorizedError: If the token is invalid, expired, or revoked.
        """
        token_hash = hash_refresh_token(raw_refresh_token)
        record = await self._user_repo.find_valid_refresh_token(token_hash)

        if record is None:
            # Check if this was a previously-valid token (reuse detection)
            revoked = await self._user_repo.find_revoked_refresh_token(token_hash)
            if revoked is not None:
                # Token replay attack — nuke all sessions
                await self._user_repo.revoke_all_user_tokens(revoked.user_id)
                await self._session.commit()
                logger.warning("token_replay_detected  user_id=%s", revoked.user_id)
            raise UnauthorizedError(
                "Refresh token is invalid or has expired. Please sign in again."
            )

        user = await self._user_repo.get_active_user_by_id(record.user_id)
        if user is None:
            raise UnauthorizedError(
                "Account not found or has been deactivated."
            )

        # Rotate: revoke old token first
        await self._user_repo.revoke_refresh_token(token_hash)
        token_pair = await self._issue_token_pair(user.id)

        logger.info("token_refreshed  user_id=%s", user.id)
        return token_pair

    # ── Profile ───────────────────────────────────────────────────

    async def get_user_profile(self, user_id: uuid.UUID) -> User:
        """Return the current user's profile.

        Raises:
            UnauthorizedError: If the user no longer exists (rare edge case
                               where account was deleted mid-session).
        """
        user = await self._user_repo.get_active_user_by_id(user_id)
        if user is None:
            raise UnauthorizedError("Account not found.")
        return user

    # ── Legacy compatibility ──────────────────────────────────────

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user by ID (used by older callers)."""
        return await self._user_repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        """Retrieve a user by email (used by older callers)."""
        return await self._user_repo.get_by_email(email)

    # ── Internal helpers ──────────────────────────────────────────

    async def _issue_token_pair(self, user_id: uuid.UUID) -> AuthTokenPair:
        """Create and persist a new access + refresh token pair."""
        access_token = create_access_token(subject=str(user_id))
        raw_refresh, refresh_hash = generate_refresh_token()

        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.REFRESH_TOKEN_EXPIRE_DAYS
        )
        await self._user_repo.store_refresh_token(
            user_id=user_id,
            token_hash=refresh_hash,
            expires_at=expires_at,
        )
        await self._session.commit()

        expires_in = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
        return AuthTokenPair(
            access_token=access_token,
            raw_refresh_token=raw_refresh,
            expires_in=expires_in,
        )
