"""User service — business logic for user operations."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.user_repo import UserRepository


class UserService:
    """Coordinates user-related business logic.

    Advanced workflows (password hashing, OAuth linking, etc.) will be
    added in future milestones.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    async def get_user(self, user_id: uuid.UUID) -> User | None:
        return await self._repo.get_by_id(user_id)

    async def get_user_by_email(self, email: str) -> User | None:
        return await self._repo.get_by_email(email)
