"""Repository API routes — list, get, create, delete.

All repository endpoints are scoped under a workspace.  Access is
verified by checking the user's workspace membership.
"""

from __future__ import annotations

import uuid

from fastapi import APIRouter, Depends, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import CurrentUserDep
from app.api.v1.schemas.repository import (
    CreateRepositoryRequest,
    RepositoryListResponse,
    RepositoryResponse,
)
from app.core.errors import ConflictError, NotFoundError
from app.db.engine import get_db
from app.repositories.repository_repo import RepositoryRepository
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


# ── GET /workspaces/{workspace_id}/repositories ─────────────────


@router.get(
    "",
    response_model=RepositoryListResponse,
    summary="List repositories in a workspace",
)
async def list_repositories(
    workspace_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> RepositoryListResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
    repo = RepositoryRepository(db)
    repositories = await repo.list_repositories_for_workspace(workspace_id)
    return RepositoryListResponse(
        repositories=[
            RepositoryResponse.model_validate(r) for r in repositories
        ],
        count=len(repositories),
    )


# ── GET /workspaces/{workspace_id}/repositories/{repository_id} ─


@router.get(
    "/{repository_id}",
    response_model=RepositoryResponse,
    summary="Get repository details",
)
async def get_repository(
    workspace_id: uuid.UUID,
    repository_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> RepositoryResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
    repo = RepositoryRepository(db)
    record = await repo.get_repository_for_workspace(repository_id, workspace_id)
    if record is None:
        raise NotFoundError("Repository", str(repository_id))
    return RepositoryResponse.model_validate(record)


# ── POST /workspaces/{workspace_id}/repositories ────────────────


@router.post(
    "",
    response_model=RepositoryResponse,
    status_code=201,
    summary="Connect a new repository",
    description=(
        "Register a source-code repository within the workspace. "
        "The repository status will be set to 'pending' until an import job runs."
    ),
)
async def create_repository(
    workspace_id: uuid.UUID,
    payload: CreateRepositoryRequest,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> RepositoryResponse:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
    repo = RepositoryRepository(db)

    # Check for duplicate
    existing = await repo.get_by_full_name(workspace_id, payload.full_name)
    if existing is not None:
        raise ConflictError(
            f"Repository '{payload.full_name}' is already connected to this workspace.",
            error_code="repository_already_connected",
        )

    record = await repo.create_repository(
        workspace_id=workspace_id,
        name=payload.name,
        full_name=payload.full_name,
        clone_url=payload.clone_url,
        default_branch=payload.default_branch,
        description=payload.description,
    )
    await db.commit()
    return RepositoryResponse.model_validate(record)


# ── DELETE /workspaces/{workspace_id}/repositories/{repository_id}


@router.delete(
    "/{repository_id}",
    status_code=204,
    response_class=Response,
    summary="Remove a repository",
    description="Delete a repository and all its indexed data.",
)
async def delete_repository(
    workspace_id: uuid.UUID,
    repository_id: uuid.UUID,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> Response:
    await _verify_workspace_membership(workspace_id, current_user.id, db)
    repo = RepositoryRepository(db)
    record = await repo.get_repository_for_workspace(repository_id, workspace_id)
    if record is None:
        raise NotFoundError("Repository", str(repository_id))
    await repo.delete(record)
    await db.commit()
    return Response(status_code=204)
