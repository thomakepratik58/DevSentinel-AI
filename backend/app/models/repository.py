"""Repository, file, import-job, and code-chunk models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
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
from app.models.enums import ImportJobStatus, RepositoryStatus


class Repository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A connected source-code repository.

    Repositories belong to a workspace and are the context for code
    indexing, incident analysis, and patch generation.
    """

    __tablename__ = "repositories"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(512), nullable=False)
    clone_url: Mapped[str] = mapped_column(Text, nullable=False)
    default_branch: Mapped[str] = mapped_column(
        String(255), server_default="main", nullable=False
    )
    status: Mapped[RepositoryStatus] = mapped_column(
        nullable=False, default=RepositoryStatus.PENDING
    )
    last_indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    metadata_: Mapped[dict | None] = mapped_column(
        "metadata", JSONB, nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship(back_populates="repositories")
    files: Mapped[list[RepositoryFile]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    import_jobs: Mapped[list[RepositoryImportJob]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_repositories_workspace_id", "workspace_id"),
        Index(
            "ix_repositories_ws_fullname",
            "workspace_id",
            "full_name",
            unique=True,
        ),
    )


class RepositoryFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single file tracked within a repository.

    Stores path, language, and size metadata.  Content is not stored
    in this table — parsed chunks live in ``code_chunks``.
    """

    __tablename__ = "repository_files"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_path: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    # ── relationships ────────────────────────────────────────────
    repository: Mapped[Repository] = relationship(back_populates="files")
    chunks: Mapped[list[CodeChunk]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_repository_files_repo_id", "repository_id"),
        Index(
            "ix_repository_files_repo_path",
            "repository_id",
            "file_path",
            unique=True,
        ),
    )


class RepositoryImportJob(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Tracks a repository import / re-index operation."""

    __tablename__ = "repository_import_jobs"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    status: Mapped[ImportJobStatus] = mapped_column(
        nullable=False, default=ImportJobStatus.QUEUED
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    files_processed: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # ── relationships ────────────────────────────────────────────
    repository: Mapped[Repository] = relationship(back_populates="import_jobs")

    __table_args__ = (
        Index("ix_import_jobs_repo_id", "repository_id"),
        Index("ix_import_jobs_status", "status"),
    )


class CodeChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A semantic chunk of source code, ready for embedding.

    The ``embedding`` column is structured for pgvector but real
    embedding generation is deferred to a future milestone.
    The column stores a plain ``JSONB`` array of floats for now;
    the migration to a true ``vector(N)`` column will happen when
    pgvector embedding pipelines are implemented.
    """

    __tablename__ = "code_chunks"

    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    symbol_name: Mapped[str | None] = mapped_column(String(512), nullable=True)
    symbol_type: Mapped[str | None] = mapped_column(String(64), nullable=True)
    language: Mapped[str | None] = mapped_column(String(64), nullable=True)
    token_count: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # pgvector-ready: stored as JSONB float array until real embeddings
    embedding: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # ── relationships ────────────────────────────────────────────
    file: Mapped[RepositoryFile] = relationship(back_populates="chunks")

    __table_args__ = (
        Index("ix_code_chunks_file_id", "file_id"),
        Index("ix_code_chunks_symbol", "symbol_name"),
    )
