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
from app.models.enums import IncidentSeverity, IncidentStatus


class Incident(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A production incident attached to a workspace."""

    __tablename__ = "incidents"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[IncidentSeverity] = mapped_column(
        nullable=False, default=IncidentSeverity.MEDIUM
    )
    status: Mapped[IncidentStatus] = mapped_column(
        nullable=False, default=IncidentStatus.DRAFT
    )
    environment: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="unknown"
    )
    expected_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_behavior: Mapped[str | None] = mapped_column(Text, nullable=True)
    stack_trace: Mapped[str | None] = mapped_column(Text, nullable=True)
    logs: Mapped[str | None] = mapped_column(Text, nullable=True)
    reproduction_steps: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='[]'
    )
    final_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    confidence_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default='{}'
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship(lazy="joined")
    repository: Mapped["Repository"] = relationship(lazy="joined")
    created_by: Mapped["User"] = relationship(lazy="joined")
    agent_runs: Mapped[list[AgentRun]] = relationship(
        back_populates="incident",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_incidents_workspace_status", "workspace_id", "status"),
        Index("ix_incidents_repo_created", "repository_id", "created_at"),
    )


class AgentRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """An AI-driven agent run on an incident."""

    __tablename__ = "agent_runs"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_type: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="queued"
    )
    model_name: Mapped[str] = mapped_column(Text, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    error_code: Mapped[str | None] = mapped_column(Text, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    input_snapshot: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='{}'
    )
    output: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='{}'
    )
    token_usage: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='{}'
    )

    # ── relationships ────────────────────────────────────────────
    incident: Mapped[Incident] = relationship(back_populates="agent_runs")
    steps: Mapped[list[AgentStep]] = relationship(
        back_populates="agent_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    retrieval_results: Mapped[list[RetrievalResult]] = relationship(
        back_populates="agent_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    patch_sets: Mapped[list[PatchSet]] = relationship(
        back_populates="agent_run",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_agent_runs_incident_id", "incident_id"),
    )


class AgentStep(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Individual reasoning step within an agent run."""

    __tablename__ = "agent_steps"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    step_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="queued"
    )
    sequence_number: Mapped[int] = mapped_column(Integer, nullable=False)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    input_data: Mapped[dict] = mapped_column(
        "input", JSONB, nullable=False, server_default='{}'
    )
    output_data: Mapped[dict] = mapped_column(
        "output", JSONB, nullable=False, server_default='{}'
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── relationships ────────────────────────────────────────────
    agent_run: Mapped[AgentRun] = relationship(back_populates="steps")

    __table_args__ = (
        Index("ix_agent_steps_run_sequence", "run_id", "sequence_number", unique=True),
    )


class RetrievalResult(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Chunks retrieved by the agent run."""

    __tablename__ = "retrieval_results"

    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        nullable=False,
    )
    rank: Mapped[int] = mapped_column(Integer, nullable=False)
    vector_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    keyword_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    rerank_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── relationships ────────────────────────────────────────────
    agent_run: Mapped[AgentRun] = relationship(back_populates="retrieval_results")
    
    __table_args__ = (
        Index("ix_retrieval_results_run_chunk", "run_id", "chunk_id", unique=True),
        Index("ix_retrieval_results_run_rank", "run_id", "rank"),
    )


class PatchSet(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A set of proposed code patches generated by analysis."""

    __tablename__ = "patch_sets"

    incident_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("incidents.id", ondelete="CASCADE"),
        nullable=False,
    )
    run_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_runs.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="draft"
    )
    title: Mapped[str] = mapped_column(Text, nullable=False)
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    unified_diff: Mapped[str] = mapped_column(Text, nullable=False)
    validation_errors: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='[]'
    )
    risk_level: Mapped[str] = mapped_column(
        Text, nullable=False, server_default='medium'
    )
    created_by: Mapped[str] = mapped_column(
        Text, nullable=False, server_default='ai'
    )

    # ── relationships ────────────────────────────────────────────
    agent_run: Mapped[AgentRun] = relationship(
        back_populates="patch_sets"
    )
    patch_files: Mapped[list[PatchFile]] = relationship(
        back_populates="patch_set",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    sandbox_runs: Mapped[list[SandboxRun]] = relationship(
        back_populates="patch_set",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_patch_sets_incident", "incident_id"),
    )


class PatchFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """File modifications within a patch set."""

    __tablename__ = "patch_files"

    patch_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patch_sets.id", ondelete="CASCADE"),
        nullable=False,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    change_type: Mapped[str] = mapped_column(Text, nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    old_content_hash: Mapped[str | None] = mapped_column(Text, nullable=True)
    new_content_hash: Mapped[str | None] = mapped_column(Text, nullable=True)

    patch_set: Mapped[PatchSet] = relationship(back_populates="patch_files")


class SandboxRun(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Sandbox execution validating a patch set."""

    __tablename__ = "sandbox_runs"

    patch_set_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("patch_sets.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String, nullable=False, default="queued"
    )
    command: Mapped[str] = mapped_column(Text, nullable=False)
    exit_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    stdout: Mapped[str | None] = mapped_column(Text, nullable=True)
    stderr: Mapped[str | None] = mapped_column(Text, nullable=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # ── relationships ────────────────────────────────────────────
    patch_set: Mapped[PatchSet] = relationship(back_populates="sandbox_runs")

    __table_args__ = (
        Index("ix_sandbox_runs_patch_set_id", "patch_set_id"),
    )
