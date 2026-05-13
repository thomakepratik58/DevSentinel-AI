"""Incident service — business logic for incident operations."""

from __future__ import annotations

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.incident import Incident
from app.repositories.incident_repo import IncidentRepository


class IncidentService:
    """Coordinates incident-related business logic.

    Analysis triggering, resolution workflows, etc. deferred to future
    milestones.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._repo = IncidentRepository(session)

    async def get_incident(self, incident_id: uuid.UUID) -> Incident | None:
        return await self._repo.get_by_id(incident_id)

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Incident]:
        return await self._repo.list_for_workspace(workspace_id)
