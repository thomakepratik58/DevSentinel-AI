"""Incident API routes — list, get, create, update.

All incident endpoints are scoped under a workspace.  Access is
verified by checking the user's workspace membership.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import CurrentUserDep
from app.api.v1.schemas.incident import (
    CreateIncidentRequest,
    IncidentListResponse,
    IncidentResponse,
    UpdateIncidentRequest,
)
from app.core.errors import NotFoundError
from app.db.engine import get_db
from app.models.enums import IncidentSeverity, IncidentStatus, WorkspaceRole
from app.repositories.incident_repo import IncidentRepository
from app.repositories.repository_repo import RepositoryRepository

router = APIRouter()


from app.api.v1.dependencies.rbac import require_role


def _to_severity(value: str) -> IncidentSeverity:
    """Convert a string to IncidentSeverity, raising ValueError on invalid input."""
    try:
        return IncidentSeverity(value.lower())
    except ValueError:
        valid = ", ".join([s.value for s in IncidentSeverity])
        raise ValueError(f"Invalid severity '{value}'. Must be one of: {valid}")


def _to_status(value: str) -> IncidentStatus:
    """Convert a string to IncidentStatus, raising ValueError on invalid input."""
    try:
        return IncidentStatus(value.lower())
    except ValueError:
        valid = ", ".join([s.value for s in IncidentStatus])
        raise ValueError(f"Invalid status '{value}'. Must be one of: {valid}")


# ── GET /workspaces/{workspace_id}/incidents ────────────────────


@router.get(
    "",
    response_model=IncidentListResponse,
    summary="List incidents in a workspace",
)
async def list_incidents(
    workspace_id: uuid.UUID,
    _role: WorkspaceRole = require_role(
        WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER
    ),
    db: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    repo = IncidentRepository(db)
    incidents = await repo.list_incidents_by_workspace(workspace_id)
    return IncidentListResponse(
        incidents=[
            IncidentResponse.model_validate(i) for i in incidents
        ],
        count=len(incidents),
    )


# ── GET /workspaces/{workspace_id}/incidents/{incident_id} ──────


@router.get(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Get incident details",
)
async def get_incident(
    workspace_id: uuid.UUID,
    incident_id: uuid.UUID,
    _role: WorkspaceRole = require_role(
        WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.DEVELOPER, WorkspaceRole.VIEWER
    ),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    repo = IncidentRepository(db)
    record = await repo.get_incident_for_workspace(incident_id, workspace_id)
    if record is None:
        raise NotFoundError("Incident", str(incident_id))
    return IncidentResponse.model_validate(record)


# ── POST /workspaces/{workspace_id}/incidents ───────────────────


@router.post(
    "",
    response_model=IncidentResponse,
    status_code=201,
    summary="Create a new incident",
    description=(
        "Report a new incident within the workspace. "
        "Optionally link it to a connected repository."
    ),
)
async def create_incident(
    workspace_id: uuid.UUID,
    payload: CreateIncidentRequest,
    current_user: CurrentUserDep,
    _role: WorkspaceRole = require_role(
        WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.DEVELOPER
    ),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    if payload.repository_id:
        repo_repo = RepositoryRepository(db)
        repo = await repo_repo.get_repository_for_workspace(payload.repository_id, workspace_id)
        if repo is None:
            raise NotFoundError("Repository", str(payload.repository_id))

    repo = IncidentRepository(db)
    severity = _to_severity(payload.severity)

    record = await repo.create_incident(
        workspace_id=workspace_id,
        repository_id=payload.repository_id,
        title=payload.title,
        description=payload.description,
        severity=severity,
        created_by=current_user.id,
    )
    await db.commit()
    await db.refresh(record)
    return IncidentResponse.model_validate(record)


# ── PATCH /workspaces/{workspace_id}/incidents/{incident_id} ────


@router.patch(
    "/{incident_id}",
    response_model=IncidentResponse,
    summary="Update an incident",
    description=(
        "Update the title, description, severity, or status of an incident. "
        "Setting status to 'resolved' automatically stamps resolved_at."
    ),
)
async def update_incident(
    workspace_id: uuid.UUID,
    incident_id: uuid.UUID,
    payload: UpdateIncidentRequest,
    _role: WorkspaceRole = require_role(
        WorkspaceRole.OWNER, WorkspaceRole.ADMIN, WorkspaceRole.DEVELOPER
    ),
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    repo = IncidentRepository(db)
    record = await repo.get_incident_for_workspace(incident_id, workspace_id)
    if record is None:
        raise NotFoundError("Incident", str(incident_id))

    if payload.title is not None:
        record.title = payload.title
    if payload.description is not None:
        record.description = payload.description
    if payload.severity is not None:
        record.severity = _to_severity(payload.severity)
    if payload.status is not None:
        new_status = _to_status(payload.status)
        record.status = new_status
        # Auto-stamp resolved_at when status transitions to RESOLVED
        if new_status == IncidentStatus.RESOLVED and record.resolved_at is None:
            record.resolved_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(record)
    return IncidentResponse.model_validate(record)
