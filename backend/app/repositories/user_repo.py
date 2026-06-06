"""User repository — data access for User, OAuthAccount, RefreshToken.

Provides all persistence operations required by the auth service and
any other service that reads user data.  Query methods use explicit,
domain-descriptive names per the instructions.md repository pattern.
"""

from __future__ import annotations

import hashlib
import uuid
from datetime import datetime, timezone

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import RefreshToken, User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    # ── Read ─────────────────────────────────────────────────────

    async def get_by_email(self, email: str) -> User | None:
        """Retrieve an active user by their email address."""
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """Retrieve a user only if their account is active."""
        stmt = select(User).where(User.id == user_id, User.is_active == True)  # noqa: E712
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Write ─────────────────────────────────────────────────────

    async def create_user(
        self,
        *,
        email: str,
        display_name: str,
        password_hash: str,
    ) -> User:
        """Persist a new user record and return it with its generated ID."""
        user = User(
            email=email,
            display_name=display_name,
            password_hash=password_hash,
            is_active=True,
        )
        return await self.create(user)

    async def update_last_login(self, user_id: uuid.UUID) -> None:
        """Stamp the user's last_login_at with the current UTC time."""
        stmt = (
            update(User)
            .where(User.id == user_id)
            .values(last_login_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)

    # ── Refresh token operations ──────────────────────────────────

    async def store_refresh_token(
        self,
        *,
        user_id: uuid.UUID,
        token_hash: str,
        expires_at: datetime,
    ) -> RefreshToken:
        """Persist a hashed refresh token record."""
        record = RefreshToken(
            user_id=user_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        self.session.add(record)
        await self.session.flush()
        await self.session.refresh(record)
        return record

    async def find_valid_refresh_token(self, token_hash: str) -> RefreshToken | None:
        """Return a refresh token record only if it exists, is not revoked,
        and has not expired."""
        now = datetime.now(timezone.utc)
        stmt = select(RefreshToken).where(
            RefreshToken.token_hash == token_hash,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def revoke_refresh_token(self, token_hash: str) -> None:
        """Mark a single refresh token as revoked."""
        stmt = (
            update(RefreshToken)
            .where(RefreshToken.token_hash == token_hash)
            .values(revoked_at=datetime.now(timezone.utc))
        )
        await self.session.execute(stmt)

    async def revoke_all_user_tokens(self, user_id: uuid.UUID) -> None:
        """Revoke all active refresh tokens for a user (full logout)."""
        now = datetime.now(timezone.utc)
        stmt = (
            update(RefreshToken)
            .where(
                RefreshToken.user_id == user_id,
                RefreshToken.revoked_at.is_(None),
            )
            .values(revoked_at=now)
        )
        await self.session.execute(stmt)

    @staticmethod
    def hash_token(raw_token: str) -> str:
        """SHA-256 hash a raw refresh token for safe storage."""
        return hashlib.sha256(raw_token.encode()).hexdigest()
