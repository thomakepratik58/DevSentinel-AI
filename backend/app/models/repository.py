"""Repository, file, import-job, and code-chunk models."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    BigInteger,
    Boolean,
    Computed,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import RepositoryStatus


class Repository(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A connected source-code repository."""

    __tablename__ = "repositories"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(Text, nullable=False)
    provider: Mapped[str] = mapped_column(Text, nullable=False)
    remote_url: Mapped[str | None] = mapped_column(Text, nullable=True)
    default_branch: Mapped[str] = mapped_column(
        Text, server_default="main", nullable=False
    )
    latest_commit_sha: Mapped[str | None] = mapped_column(Text, nullable=True)
    index_status: Mapped[RepositoryStatus] = mapped_column(
        nullable=False, default=RepositoryStatus.QUEUED
    )
    index_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    indexed_file_count: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    indexed_chunk_count: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    partial_index: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default='{}'
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    workspace: Mapped["Workspace"] = relationship(back_populates="repositories")
    files: Mapped[list[RepositoryFile]] = relationship(
        back_populates="repository",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_repositories_workspace_id", "workspace_id"),
    )


class RepositoryFile(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A single file tracked within a repository."""

    __tablename__ = "repository_files"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    path: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(
        Text, nullable=False, server_default="unknown"
    )
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    line_count: Mapped[int] = mapped_column(Integer, nullable=False)
    is_test: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    is_binary: Mapped[bool] = mapped_column(
        Boolean, server_default="false", nullable=False
    )
    content: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default='{}'
    )

    # ── relationships ────────────────────────────────────────────
    repository: Mapped[Repository] = relationship(back_populates="files")
    chunks: Mapped[list[CodeChunk]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index(
            "ix_repository_files_repo_path",
            "repository_id",
            "path",
            unique=True,
        ),
    )


class CodeSymbol(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A semantic symbol (function, class, etc.) extracted from code."""

    __tablename__ = "code_symbols"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol_name: Mapped[str] = mapped_column(Text, nullable=False)
    symbol_type: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    parent_symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_symbols.id", ondelete="SET NULL"),
        nullable=True,
    )
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    docstring: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default='{}'
    )

    __table_args__ = (
        Index("ix_code_symbols_repo_name", "repository_id", "symbol_name"),
    )


class CodeChunk(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A semantic chunk of source code, ready for embedding."""

    __tablename__ = "code_chunks"

    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    file_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repository_files.id", ondelete="CASCADE"),
        nullable=False,
    )
    symbol_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_symbols.id", ondelete="SET NULL"),
        nullable=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_type: Mapped[str] = mapped_column(Text, nullable=False)
    language: Mapped[str] = mapped_column(Text, nullable=False)
    path: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_hash: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    search_vector: Mapped[Any] = mapped_column(
        TSVECTOR,
        Computed("to_tsvector('english', content)"),
        nullable=True,
    )
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, nullable=False, server_default='{}'
    )

    # ── relationships ────────────────────────────────────────────
    file: Mapped[RepositoryFile] = relationship(back_populates="chunks")
    chunk_embedding: Mapped["ChunkEmbedding"] = relationship(
        back_populates="chunk",
        cascade="all, delete-orphan",
        lazy="selectin",
        uselist=False,
    )

    __table_args__ = (
        Index("ix_code_chunks_repo_file", "repository_id", "file_id"),
        Index("ix_code_chunks_search", "search_vector", postgresql_using="gin"),
        Index("ix_code_chunks_path_trgm", "path", postgresql_ops={"path": "gin_trgm_ops"}, postgresql_using="gin"),
        Index("ix_code_chunks_file_chunk", "file_id", "chunk_index", unique=True),
    )


class ChunkEmbedding(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Stores the pgvector embedding for a specific CodeChunk."""

    __tablename__ = "chunk_embeddings"

    chunk_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("code_chunks.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("repositories.id", ondelete="CASCADE"),
        nullable=False,
    )
    embedding_model: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(3072), nullable=False)

    chunk: Mapped[CodeChunk] = relationship(back_populates="chunk_embedding")
