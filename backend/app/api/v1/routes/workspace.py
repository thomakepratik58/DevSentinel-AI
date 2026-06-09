"""Workspace API routes — list, get, create.

All workspace endpoints require authentication.  The user must be a
member of the workspace to access its resources (enforced by the
service layer).
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import CurrentUserDep
from app.api.v1.schemas.workspace import (
    CreateWorkspaceRequest,
    WorkspaceListResponse,
    WorkspaceResponse,
)
from app.core.errors import ForbiddenError, NotFoundError
from app.db.engine import get_db
from app.repositories.workspace_repo import WorkspaceRepository

router = APIRouter()


# ── GET /workspaces ──────────────────────────────────────────────


@router.get(
    "",
    response_model=WorkspaceListResponse,
    summary="List workspaces for the current user",
    description="Return all workspaces the authenticated user is a member of.",
)
async def list_workspaces(
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> WorkspaceListResponse:
    repo = WorkspaceRepository(db)
    workspaces = await repo.list_workspaces_for_user(current_user.id)
    return WorkspaceListResponse(
        workspaces=[
            WorkspaceResponse.model_validate(ws) for ws in workspaces
        ],
        count=len(workspaces),
    )


# ── GET /workspaces/{workspace_id} ──────────────────────────────


@router.get(
    "/{workspace_id}",
    response_model=WorkspaceResponse,
    summary="Get workspace details",
    description="Return a single workspace if the current user is a member.",
)
async def get_workspace(
    workspace_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.get_workspace_for_user(workspace_id, current_user.id)
    if workspace is None:
        raise NotFoundError("Workspace", str(workspace_id))
    return WorkspaceResponse.model_validate(workspace)


# ── POST /workspaces ─────────────────────────────────────────────


@router.post(
    "",
    response_model=WorkspaceResponse,
    status_code=201,
    summary="Create a new workspace",
    description=(
        "Create a new workspace and add the current user as its owner."
    ),
)
async def create_workspace(
    payload: CreateWorkspaceRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> WorkspaceResponse:
    repo = WorkspaceRepository(db)
    workspace = await repo.create_workspace(
        name=payload.name,
        owner_id=current_user.id,
        description=payload.description,
    )
    await db.commit()
    return WorkspaceResponse.model_validate(workspace)
