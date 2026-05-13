"""Incident repository."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.incident import Incident
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    model = Incident

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Incident]:
        stmt = (
            select(Incident)
            .where(Incident.workspace_id == workspace_id)
            .order_by(Incident.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
