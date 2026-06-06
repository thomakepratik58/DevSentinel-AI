"""Workspace repository — data access for Workspace and WorkspaceMember."""

from __future__ import annotations

import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.enums import WorkspaceRole
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.base import BaseRepository


class WorkspaceRepository(BaseRepository[Workspace]):
    model = Workspace

    # ── Read ─────────────────────────────────────────────────────

    async def get_by_slug(self, slug: str) -> Workspace | None:
        """Retrieve a workspace by its unique URL slug."""
        stmt = select(Workspace).where(Workspace.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_workspaces_for_user(self, user_id: uuid.UUID) -> list[Workspace]:
        """Return all workspaces the user is a member of, in creation order."""
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(WorkspaceMember.user_id == user_id)
            .order_by(Workspace.created_at.asc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def get_workspace_for_user(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> Workspace | None:
        """Return a workspace only if the given user is a member."""
        stmt = (
            select(Workspace)
            .join(WorkspaceMember, WorkspaceMember.workspace_id == Workspace.id)
            .where(
                Workspace.id == workspace_id,
                WorkspaceMember.user_id == user_id,
            )
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_member_role(
        self,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
    ) -> WorkspaceRole | None:
        """Return the role of a user within a workspace, or None if not a member."""
        stmt = select(WorkspaceMember.role).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        result = await self.session.execute(stmt)
        row = result.scalar_one_or_none()
        return row  # type: ignore[return-value]

    # ── Write ─────────────────────────────────────────────────────

    async def create_workspace(
        self,
        *,
        name: str,
        owner_id: uuid.UUID,
        description: str | None = None,
    ) -> Workspace:
        """Create a workspace and automatically add the owner as a member."""
        slug = self._slugify(name)
        slug = await self._ensure_unique_slug(slug)

        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            owner_id=owner_id,
        )
        self.session.add(workspace)
        await self.session.flush()
        await self.session.refresh(workspace)

        # Owner is automatically a member with the OWNER role
        await self.add_workspace_member(
            workspace_id=workspace.id,
            user_id=owner_id,
            role=WorkspaceRole.OWNER,
        )
        return workspace

    async def add_workspace_member(
        self,
        *,
        workspace_id: uuid.UUID,
        user_id: uuid.UUID,
        role: WorkspaceRole = WorkspaceRole.MEMBER,
    ) -> WorkspaceMember:
        """Add a user to a workspace with the specified role."""
        member = WorkspaceMember(
            workspace_id=workspace_id,
            user_id=user_id,
            role=role,
        )
        self.session.add(member)
        await self.session.flush()
        await self.session.refresh(member)
        return member

    # ── Helpers ───────────────────────────────────────────────────

    @staticmethod
    def _slugify(name: str) -> str:
        """Convert a workspace name to a URL-safe slug."""
        slug = name.lower().strip()
        slug = re.sub(r"[^\w\s-]", "", slug)
        slug = re.sub(r"[\s_-]+", "-", slug)
        slug = slug.strip("-")
        return slug[:50]  # max length

    async def _ensure_unique_slug(self, base_slug: str) -> str:
        """Append a numeric suffix if the slug already exists."""
        candidate = base_slug
        counter = 1
        while True:
            exists = await self.get_by_slug(candidate)
            if exists is None:
                return candidate
            candidate = f"{base_slug}-{counter}"
            counter += 1
