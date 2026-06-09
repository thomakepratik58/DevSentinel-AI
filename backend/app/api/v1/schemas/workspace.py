"""Pydantic request/response schemas for the workspace API.

Keeps API contracts separate from the SQLAlchemy ORM models so that
internal schema changes don't leak to the frontend.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Request schemas ─────────────────────────────────────────────


class CreateWorkspaceRequest(BaseModel):
    """Payload for ``POST /workspaces``."""

    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Human-readable workspace name.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional description of the workspace.",
    )


# ── Response schemas ────────────────────────────────────────────


class WorkspaceResponse(BaseModel):
    """Single workspace returned from the API."""

    id: uuid.UUID
    name: str
    slug: str
    description: str | None
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class WorkspaceListResponse(BaseModel):
    """Paginated list of workspaces."""

    workspaces: list[WorkspaceResponse]
    count: int
