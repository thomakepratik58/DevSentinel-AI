"""Workspace service — business logic for workspace operations."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.workspace import Workspace
from app.repositories.workspace_repo import WorkspaceRepository


class WorkspaceService:
    """Coordinates workspace-related business logic.

    Member invitations, role changes, etc. deferred to future milestones.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = WorkspaceRepository(session)

    async def get_workspace(self, workspace_id: uuid.UUID) -> Workspace | None:
        return await self._repo.get_by_id(workspace_id)

    async def get_by_slug(self, slug: str) -> Workspace | None:
        return await self._repo.get_by_slug(slug)

    async def list_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        return await self._repo.list_for_user(user_id)
