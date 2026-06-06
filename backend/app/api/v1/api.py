"""API v1 router — assembles all versioned route modules."""

from fastapi import APIRouter

from app.api.v1.routes import auth, health, incident, repository, workspace

api_router = APIRouter()

# ── Auth ─────────────────────────────────────────────────────────
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# ── Health ───────────────────────────────────────────────────────
api_router.include_router(health.router, tags=["health"])

# ── Workspaces ───────────────────────────────────────────────────
api_router.include_router(workspace.router, prefix="/workspaces", tags=["workspaces"])

# ── Repositories (nested under workspaces) ───────────────────────
api_router.include_router(
    repository.router,
    prefix="/workspaces/{workspace_id}/repositories",
    tags=["repositories"],
)

# ── Incidents (nested under workspaces) ──────────────────────────
api_router.include_router(
    incident.router,
    prefix="/workspaces/{workspace_id}/incidents",
    tags=["incidents"],
)
