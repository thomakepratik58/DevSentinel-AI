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
from app.models.enums import IncidentSeverity, IncidentStatus
from app.repositories.incident_repo import IncidentRepository
from app.repositories.workspace_repo import WorkspaceRepository

router = APIRouter()


# ── Helpers ──────────────────────────────────────────────────────


async def _verify_workspace_membership(
    workspace_id: uuid.UUID,
    user_id: uuid.UUID,
    db: AsyncSession,
) -> None:
    """Raise NotFoundError if the user is not a member of the workspace."""
    ws_repo = WorkspaceRepository(db)
    ws = await ws_repo.get_workspace_for_user(workspace_id, user_id)
    if ws is None:
        raise NotFoundError("Workspace", str(workspace_id))


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
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> IncidentListResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
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
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
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
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
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
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> IncidentResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
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
