"""Incident repository — data access for Incident and related models."""

from __future__ import annotations

import uuid

from sqlalchemy import select

from app.models.enums import IncidentSeverity, IncidentStatus
from app.models.incident import Incident
from app.repositories.base import BaseRepository


class IncidentRepository(BaseRepository[Incident]):
    model = Incident

    # ── Read ─────────────────────────────────────────────────────

    async def get_incident_for_workspace(
        self,
        incident_id: uuid.UUID,
        workspace_id: uuid.UUID,
    ) -> Incident | None:
        """Return an incident only if it belongs to the given workspace."""
        stmt = select(Incident).where(
            Incident.id == incident_id,
            Incident.workspace_id == workspace_id,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_open_incidents_by_workspace(
        self,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Incident]:
        """Return non-resolved incidents for a workspace, newest first."""
        stmt = (
            select(Incident)
            .where(
                Incident.workspace_id == workspace_id,
                Incident.status.not_in(
                    [IncidentStatus.RESOLVED, IncidentStatus.CLOSED]
                ),
            )
            .order_by(Incident.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_incidents_by_workspace(
        self,
        workspace_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[Incident]:
        """Return all incidents for a workspace, newest first."""
        stmt = (
            select(Incident)
            .where(Incident.workspace_id == workspace_id)
            .order_by(Incident.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def list_for_workspace(self, workspace_id: uuid.UUID) -> list[Incident]:
        """Alias kept for backward compatibility with existing stubs."""
        return await self.list_incidents_by_workspace(workspace_id)

    # ── Write ─────────────────────────────────────────────────────

    async def create_incident(
        self,
        *,
        workspace_id: uuid.UUID,
        repository_id: uuid.UUID | None,
        title: str,
        description: str | None = None,
        severity: IncidentSeverity = IncidentSeverity.MEDIUM,
        created_by: uuid.UUID,
    ) -> Incident:
        """Persist a new incident and return the saved record."""
        incident = Incident(
            workspace_id=workspace_id,
            repository_id=repository_id,
            title=title,
            description=description,
            severity=severity,
            status=IncidentStatus.OPEN,
            created_by_id=created_by,
        )
        return await self.create(incident)
