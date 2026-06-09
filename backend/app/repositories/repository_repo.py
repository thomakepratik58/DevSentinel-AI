"""Repository (source-code repo) repository — data access layer."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.enums import RepositoryStatus
from app.models.repository import Repository
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    model = Repository

    # ── Read ─────────────────────────────────────────────────────

    async def get_repository_for_workspace(
        self,
        repository_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> Repository | None:
        """Return a repository only if it belongs to the given workspace."""
        stmt = select(Repository).where(
            Repository.id == repository_id,
            Repository.workspace_id == workspace_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_repositories_for_workspace(
        self,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Repository]:
        """Return all repositories for a workspace, ordered by name."""
        stmt = (
            select(Repository)
            .where(Repository.workspace_id == workspace_id)
            .order_by(Repository.name.asc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Repository]:
        """Alias for backward compatibility with existing stubs."""
        return await self.list_repositories_for_workspace(workspace_id)

    async def get_by_full_name(
        self,
        workspace_id: uuid.UUID,
        full_name: str,
    ) -> Repository | None:
        """Find a repository by its provider full name (e.g. 'org/repo')."""
        stmt = select(Repository).where(
            Repository.workspace_id == workspace_id,
            Repository.full_name == full_name,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    # ── Write ─────────────────────────────────────────────────────

    async def create_repository(
        self,
        *,
        workspace_id: uuid.UUID,
        name: str,
        full_name: str,
        clone_url: str,
        default_branch: str = "main",
        description: str | None = None,
    ) -> Repository:
        """Persist a new connected repository."""
        repo = Repository(
            workspace_id=workspace_id,
            name=name,
            full_name=full_name,
            clone_url=clone_url,
            default_branch=default_branch,
            description=description,
            status=RepositoryStatus.PENDING,
        )
        return await self.create(repo)
