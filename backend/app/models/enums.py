"""Domain enumerations used across the schema.

Each Python enum maps to a PostgreSQL ``CREATE TYPE … AS ENUM``
created by Alembic during the initial migration.
"""

from __future__ import annotations

import enum


class WorkspaceRole(str, enum.Enum):
    """Role a user holds within a workspace."""

    OWNER = "owner"
    ADMIN = "admin"
    DEVELOPER = "developer"
    VIEWER = "viewer"


class RepositoryStatus(str, enum.Enum):
    """Lifecycle status of a connected repository."""

    QUEUED = "queued"
    CLONING = "cloning"
    SCANNING = "scanning"
    EMBEDDING = "embedding"
    PARTIAL_READY = "partial_ready"
    READY = "ready"
    FAILED = "failed"


class IncidentSeverity(str, enum.Enum):
    """Severity classification for an incident."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class IncidentStatus(str, enum.Enum):
    """Workflow status of an incident."""

    DRAFT = "draft"
    QUEUED = "queued"
    ANALYZING = "analyzing"
    ANALYZED = "analyzed"
    PATCHING = "patching"
    TESTING = "testing"
    RESOLVED = "resolved"
    FAILED = "failed"


class RunStatus(str, enum.Enum):
    """Status of an AI agent or sandbox run."""

    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PatchStatus(str, enum.Enum):
    """Status of a generated patch set."""

    DRAFT = "draft"
    VALIDATING = "validating"
    VALID = "valid"
    INVALID = "invalid"
    ACCEPTED = "accepted"
    REJECTED = "rejected"


class AuditAction(str, enum.Enum):
    """Categories of auditable actions."""

    USER_LOGIN = "user_login"
    USER_LOGOUT = "user_logout"
    WORKSPACE_CREATED = "workspace_created"
    WORKSPACE_UPDATED = "workspace_updated"
    MEMBER_INVITED = "member_invited"
    MEMBER_REMOVED = "member_removed"
    REPOSITORY_CONNECTED = "repository_connected"
    REPOSITORY_REMOVED = "repository_removed"
    INCIDENT_CREATED = "incident_created"
    INCIDENT_UPDATED = "incident_updated"
    ANALYSIS_STARTED = "analysis_started"
    PATCH_APPLIED = "patch_applied"
    SANDBOX_EXECUTED = "sandbox_executed"
