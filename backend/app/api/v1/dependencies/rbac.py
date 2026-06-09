"""Role-based access control (RBAC) dependency."""

import uuid
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import CurrentUserDep
from app.core.errors import ForbiddenError, NotFoundError
from app.db.engine import get_db
from app.models.enums import WorkspaceRole
from app.repositories.workspace_repo import WorkspaceRepository

def require_role(*allowed_roles: WorkspaceRole):
    """FastAPI dependency factory that enforces role-based access.
    
    Must be used in routes that have a `workspace_id` path parameter.
    """
    async def _check(
        workspace_id: uuid.UUID,
        current_user: CurrentUserDep,
        db: AsyncSession = Depends(get_db),
    ) -> WorkspaceRole:
        ws_repo = WorkspaceRepository(db)
        role = await ws_repo.get_member_role(workspace_id, current_user.id)
        if role is None:
            raise NotFoundError("Workspace", str(workspace_id))
        if role not in allowed_roles:
            allowed_roles_str = ", ".join(r.value for r in allowed_roles)
            raise ForbiddenError(
                f"Role '{role.value}' cannot perform this action. "
                f"Required: {allowed_roles_str}."
            )
        return role
    return Depends(_check)
