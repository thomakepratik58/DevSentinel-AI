"""Database seed script — creates demo user and default workspace.

Idempotent: safe to run multiple times.  Skips creation if the demo
user already exists.

Usage (from project root):
    & "...\backend_venv\Scripts\python.exe" backend/seed.py

Demo credentials:
    email:    demo@devsentinel.ai
    password: DevSentinel2026!
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure the backend package is importable when run from project root
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings
from app.core.security import hash_password
from app.models.enums import WorkspaceRole
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember
from app.repositories.user_repo import UserRepository
from app.repositories.workspace_repo import WorkspaceRepository

_DEMO_EMAIL = "demo@devsentinel.ai"
_DEMO_PASSWORD = "DevSentinel2026!"
_DEMO_DISPLAY_NAME = "Demo User"
_DEMO_WORKSPACE_NAME = "Demo Workspace"

_DATABASE_URL = settings.DATABASE_URL.replace(
    "postgresql+psycopg://", "postgresql+asyncpg://"
)


async def seed() -> None:
    engine = create_async_engine(_DATABASE_URL, echo=False)
    SessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

    async with SessionLocal() as session:
        user_repo = UserRepository(session)
        ws_repo = WorkspaceRepository(session)

        async with session.begin():
            # ── Check for existing demo user ─────────────────────────
            existing = await user_repo.get_by_email(_DEMO_EMAIL)
            if existing is not None:
                print(f"[seed] Demo user already exists: {_DEMO_EMAIL}  (skipping)")
                await engine.dispose()
                return

            print("[seed] Creating demo user…")
            user = await user_repo.create_user(
                email=_DEMO_EMAIL,
                display_name=_DEMO_DISPLAY_NAME,
                password_hash=hash_password(_DEMO_PASSWORD),
            )

            workspace = await ws_repo.create_workspace(
                name=_DEMO_WORKSPACE_NAME,
                owner_id=user.id,
            )

        print(f"[seed] SUCCESS - User created:     {user.email}  (id={user.id})")
        print(f"[seed] SUCCESS - Workspace created: {workspace.name}  (id={workspace.id})")
        print(f"[seed]")
        print(f"[seed] Login credentials:")
        print(f"[seed]   Email:    {_DEMO_EMAIL}")
        print(f"[seed]   Password: {_DEMO_PASSWORD}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed())
