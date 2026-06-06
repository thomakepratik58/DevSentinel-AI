"""Pydantic request/response schemas for the incident API.

Incidents represent production issues that trigger AI-assisted
root-cause analysis.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel, Field


# ── Request schemas ─────────────────────────────────────────────


class CreateIncidentRequest(BaseModel):
    """Payload for ``POST /workspaces/{id}/incidents``."""

    title: str = Field(
        ...,
        min_length=3,
        max_length=300,
        description="Short, descriptive incident title.",
    )
    description: str | None = Field(
        default=None,
        max_length=10_000,
        description="Detailed description — stack traces, logs, context.",
    )
    severity: str = Field(
        default="medium",
        description="Severity level: low, medium, high, critical.",
    )
    repository_id: uuid.UUID | None = Field(
        default=None,
        description="Optional linked repository.",
    )


class UpdateIncidentRequest(BaseModel):
    """Payload for ``PATCH /workspaces/{id}/incidents/{id}``."""

    title: str | None = Field(default=None, min_length=3, max_length=300)
    description: str | None = Field(default=None, max_length=10_000)
    severity: str | None = Field(default=None)
    status: str | None = Field(default=None)


# ── Response schemas ────────────────────────────────────────────


class IncidentResponse(BaseModel):
    """Single incident returned from the API."""

    id: uuid.UUID
    workspace_id: uuid.UUID
    repository_id: uuid.UUID | None
    title: str
    description: str | None
    severity: str
    status: str
    created_by_id: uuid.UUID
    resolved_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class IncidentListResponse(BaseModel):
    """Paginated list of incidents."""

    incidents: list[IncidentResponse]
    count: int
