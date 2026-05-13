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
    MEMBER = "member"
    VIEWER = "viewer"


class OAuthProvider(str, enum.Enum):
    """Supported OAuth identity providers."""

    GITHUB = "github"
    GOOGLE = "google"


class RepositoryStatus(str, enum.Enum):
    """Lifecycle status of a connected repository."""

    PENDING = "pending"
    INDEXING = "indexing"
    READY = "ready"
    ERROR = "error"
    ARCHIVED = "archived"


class ImportJobStatus(str, enum.Enum):
    """Status of a repository import / re-index job."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IncidentSeverity(str, enum.Enum):
    """Severity classification for an incident."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class IncidentStatus(str, enum.Enum):
    """Workflow status of an incident."""

    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    CLOSED = "closed"


class AnalysisRunStatus(str, enum.Enum):
    """Status of an AI analysis run."""

    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class AnalysisStepType(str, enum.Enum):
    """Kind of reasoning step within an analysis run."""

    EVIDENCE_GATHERING = "evidence_gathering"
    ROOT_CAUSE_ANALYSIS = "root_cause_analysis"
    FIX_GENERATION = "fix_generation"
    VALIDATION = "validation"


class AnalysisStepStatus(str, enum.Enum):
    """Completion status of an individual analysis step."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class EvidenceType(str, enum.Enum):
    """Category of evidence collected during analysis."""

    LOG_SNIPPET = "log_snippet"
    STACK_TRACE = "stack_trace"
    CODE_REFERENCE = "code_reference"
    CONFIGURATION = "configuration"
    METRIC = "metric"
    EXTERNAL_LINK = "external_link"


class PatchSetStatus(str, enum.Enum):
    """Status of a generated patch set."""

    DRAFT = "draft"
    VALIDATED = "validated"
    APPLIED = "applied"
    REJECTED = "rejected"


class SandboxRunStatus(str, enum.Enum):
    """Status of a sandbox validation run."""

    QUEUED = "queued"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERROR = "error"


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
