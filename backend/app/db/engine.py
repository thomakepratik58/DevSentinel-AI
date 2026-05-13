"""Async SQLAlchemy engine and session factory.

Provides a single ``async_engine`` and ``AsyncSessionLocal`` factory
that the rest of the application imports.  The ``get_db`` dependency
yields a session per-request and ensures it is closed afterwards.
"""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core.config import settings

# ── Engine ──────────────────────────────────────────────────────
# The connection string must use an async driver.
# For PostgreSQL: ``postgresql+asyncpg://…``
# The psycopg (sync) driver in requirements is used only by Alembic.

_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+psycopg://", "postgresql+asyncpg://"
)

async_engine = create_async_engine(
    _DATABASE_URL,
    echo=settings.is_development,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# ── Session factory ─────────────────────────────────────────────

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


# ── FastAPI dependency ──────────────────────────────────────────

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Yield a database session for the lifetime of a single request."""
    async with AsyncSessionLocal() as session:
        yield session
