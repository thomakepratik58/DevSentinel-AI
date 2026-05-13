"""Incident and analysis models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import (
    AnalysisRunStatus,
    AnalysisStepStatus,
    AnalysisStepType,
    EvidenceType,
    IncidentSeverity,
    IncidentStatus,
    PatchSetStatus,
    SandboxRunStatus,
)


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A production incident attached to a workspace.

    Users paste logs, stack traces, and descriptions.  AI analysis runs
    are launched from an incident to determine root cause.
    """

    __tablename__ = "incidents"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    severity: Mapped[IncidentSeverity] = mapped_column(
        nullable=False, default=IncidentSeverity.MEDIUM
    )
    status: Mapped[IncidentStatus] = mapped_column(
        nullable=False, default=IncidentStatus.OPEN
    )
    raw_logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship(lazy="joined")
    repository: Mapped["Repository | None"] = relationship(lazy="joined")
    created_by: Mapped["User"] = relationship(lazy="joined")
    analysis_runs: Mapped[list[AnalysisRun]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_incidents_workspace_id", "workspace_id"),
        Index("ix_incidents_status", "status"),
        Index("ix_incidents_severity", "severity"),
        Index("ix_incidents_created_by", "created_by_id"),
    )


class AnalysisRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An AI-driven analysis run on an incident.

    Each run progresses through multiple steps (evidence gathering →
    root cause → fix generation → validation).
    """

    __tablename__ = "analysis_runs"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )
    triggered_by_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[AnalysisRunStatus] = mapped_column(
        nullable=False, default=AnalysisRunStatus.QUEUED
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    model_used: Mapped[str | None] = mapped_column(String(128), nullable=True)
    token_usage: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── relationships ────────────────────────────────────────────
    incident: Mapped[Incident] = relationship(back_populates="analysis_runs")
    triggered_by: Mapped["User"] = relationship(lazy="joined")
    steps: Mapped[list[AnalysisStep]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    evidence_items: Mapped[list[EvidenceItem]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    patch_sets: Mapped[list[PatchSet]] = relationship(
        back_populates="analysis_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_analysis_runs_incident_id", "incident_id"),
        Index("ix_analysis_runs_status", "status"),
    )


class AnalysisStep(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Individual reasoning step within an analysis run."""

    __tablename__ = "analysis_steps"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_order: Mapped[int] = mapped_column(Integer, nullable=False)
    step_type: Mapped[AnalysisStepType] = mapped_column(nullable=False)
    status: Mapped[AnalysisStepStatus] = mapped_column(
        nullable=False, default=AnalysisStepStatus.PENDING
    )
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    output_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── relationships ────────────────────────────────────────────
    analysis_run: Mapped[AnalysisRun] = relationship(back_populates="steps")

    __table_args__ = (
        Index("ix_analysis_steps_run_id", "analysis_run_id"),
    )


class EvidenceItem(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A piece of evidence collected during an analysis run."""

    __tablename__ = "evidence_items"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    evidence_type: Mapped[EvidenceType] = mapped_column(nullable=False)
    title: Mapped[str] = mapped_column(String(512), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_file: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_lines: Mapped[str | None] = mapped_column(
        String(64), nullable=True
    )
    relevance_score: Mapped[float | None] = mapped_column(
        Float, nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="evidence_items"
    )

    __table_args__ = (
        Index("ix_evidence_items_run_id", "analysis_run_id"),
        Index("ix_evidence_items_type", "evidence_type"),
    )


class PatchSet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A set of proposed code patches generated by analysis."""

    __tablename__ = "patch_sets"

    analysis_run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("analysis_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[PatchSetStatus] = mapped_column(
        nullable=False, default=PatchSetStatus.DRAFT
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    diff_content: Mapped[str] = mapped_column(Text, nullable=False)
    files_changed: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    applied_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    applied_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── relationships ────────────────────────────────────────────
    analysis_run: Mapped[AnalysisRun] = relationship(
        back_populates="patch_sets"
    )
    applied_by: Mapped["User | None"] = relationship(lazy="joined")
    sandbox_runs: Mapped[list[SandboxRun]] = relationship(
        back_populates="patch_set",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_patch_sets_run_id", "analysis_run_id"),
        Index("ix_patch_sets_status", "status"),
    )


class SandboxRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Sandbox execution validating a patch set."""

    __tablename__ = "sandbox_runs"

    patch_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patch_sets.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[SandboxRunStatus] = mapped_column(
        nullable=False, default=SandboxRunStatus.QUEUED
    )
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    patch_set: Mapped[PatchSet] = relationship(back_populates="sandbox_runs")

    __table_args__ = (
        Index("ix_sandbox_runs_patch_set_id", "patch_set_id"),
        Index("ix_sandbox_runs_status", "status"),
    )
