"""Audit event model."""

from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.enums import AuditAction


class AuditEvent(UUIDPrimaryKeyMixin, TimestampMixin, Base):
    """Immutable audit log of significant actions.

    Every auditable action records who did it, in which workspace,
    what the action was, and any additional payload.
    """

    __tablename__ = "audit_events"

    workspace_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("workspaces.id", ondelete="SET NULL"),
        nullable=True,
    )
    actor_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[AuditAction] = mapped_column(nullable=False)
    resource_type: Mapped[str | None] = mapped_column(
        String(128), nullable=True
    )
    resource_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # ── relationships ────────────────────────────────────────────
    actor: Mapped["User | None"] = relationship(lazy="joined")
    workspace: Mapped["Workspace | None"] = relationship(lazy="joined")

    __table_args__ = (
        Index("ix_audit_events_workspace_id", "workspace_id"),
        Index("ix_audit_events_actor_id", "actor_id"),
        Index("ix_audit_events_action", "action"),
        Index("ix_audit_events_created_at", "created_at"),
    )
