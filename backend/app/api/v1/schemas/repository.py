"""Pydantic request/response schemas for the repository API.

Repositories represent connected source-code repos (e.g. GitHub).
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field, field_validator


# ── Request schemas ─────────────────────────────────────────────


class CreateRepositoryRequest(BaseModel):
    """Payload for ``POST /workspaces/{id}/repositories``."""

    name: str = Field(
        ...,
        min_length=1,
        max_length=200,
        description="Short display name (e.g. 'backend-api').",
    )
    full_name: str = Field(
        ...,
        min_length=1,
        max_length=300,
        description="Provider-qualified name (e.g. 'org/repo').",
    )
    clone_url: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="HTTPS clone URL for the repository.",
    )
    default_branch: str = Field(
        default="main",
        max_length=100,
        description="Primary branch name.",
    )
    description: str | None = Field(
        default=None,
        max_length=500,
        description="Optional repository description.",
    )

    @field_validator("clone_url")
    @classmethod
    def clone_url_must_be_valid(cls, value: str) -> str:
        if not (value.startswith("https://") or value.startswith("git@")):
            raise ValueError(
                "Clone URL must start with 'https://' or 'git@'."
            )
        return value


# ── Response schemas ────────────────────────────────────────────


class RepositoryResponse(BaseModel):
    """Single repository returned from the API."""

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    full_name: str
    clone_url: str
    default_branch: str
    description: str | None
    status: str
    last_indexed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class RepositoryListResponse(BaseModel):
    """Paginated list of repositories."""

    repositories: list[RepositoryResponse]
    count: int
