"""Repository (source-code repo) repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.repository import Repository
from app.repositories.base import BaseRepository


class RepositoryRepository(BaseRepository[Repository]):
    model = Repository

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Repository]:
        stmt = select(Repository).where(
            Repository.workspace_id == workspace_id
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
