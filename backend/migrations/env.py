"""Alembic environment configuration.

Supports both online (live database) and offline (SQL script) modes.
Uses the sync ``psycopg`` driver because Alembic runs migrations
synchronously.  The connection URL is pulled from app settings so that
``alembic.ini`` does not need to be kept in sync.
"""

from __future__ import annotations

import sys
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Ensure the backend package is on sys.path so that ``app.*`` imports work
# when alembic is invoked from the ``backend/`` directory.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings  # noqa: E402
from app.models import Base  # noqa: E402  — registers all models

# ── Alembic Config object ──────────────────────────────────────
config = context.config

# Override the sqlalchemy.url from settings (sync driver for Alembic)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Target metadata for autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Emit SQL statements without a live database connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
