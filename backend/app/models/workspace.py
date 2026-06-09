"""Workspace and workspace membership models."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    String,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import WorkspaceRole


class Workspace(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """A workspace groups repositories, incidents, and members."""

    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(Text, nullable=False)
    slug: Mapped[str] = mapped_column(
        Text, unique=True, nullable=False
    )
    created_by_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id"),
        nullable=False,
    )
    settings: Mapped[dict] = mapped_column(
        JSONB, nullable=False, server_default='{}'
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # ── relationships ────────────────────────────────────────────
    members: Mapped[list[WorkspaceMember]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    repositories: Mapped[list["Repository"]] = relationship(
        back_populates="workspace",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        Index("ix_workspaces_slug", "slug"),
    )


class WorkspaceMember(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Many-to-many join between users and workspaces with a role."""

    __tablename__ = "workspace_members"

    workspace_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[WorkspaceRole] = mapped_column(
        nullable=False, default=WorkspaceRole.DEVELOPER
    )

    # ── relationships ────────────────────────────────────────────
    workspace: Mapped[Workspace] = relationship(back_populates="members")
    user: Mapped["User"] = relationship(back_populates="workspace_memberships")

    __table_args__ = (
        Index(
            "ix_workspace_members_ws_user",
            "workspace_id",
            "user_id",
            unique=True,
        ),
        Index("ix_workspace_members_user", "user_id"),
    )
