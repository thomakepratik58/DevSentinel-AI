"""FastAPI dependencies for authentication and current-user resolution.

Import ``CurrentUserDep`` in route handlers to enforce authentication:

    async def my_route(current_user: CurrentUserDep) -> ...:
        ...

The dependency reads the ``Authorization: Bearer <token>`` header,
decodes the JWT, loads the user from the database, and raises a typed
``UnauthorizedError`` on any failure — never leaking internal details.
"""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import UnauthorizedError
from app.core.security import decode_access_token, extract_bearer_token
from app.db.engine import get_db
from app.models.user import User
from app.repositories.user_repo import UserRepository
import uuid


async def get_current_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User:
    """Resolve the authenticated user from the incoming JWT access token.

    Reads ``Authorization: Bearer <token>`` from the request headers.
    Decodes the token, fetches the user from the database, and confirms
    the account is still active.

    Raises:
        UnauthorizedError: On any auth failure — missing header, expired
                           token, revoked session, or deactivated account.
    """
    authorization = request.headers.get("Authorization")
    token = extract_bearer_token(authorization)
    payload = decode_access_token(token)

    subject = payload.get("sub")
    if not subject:
        raise UnauthorizedError("Token is missing the subject claim.")

    try:
        user_id = uuid.UUID(subject)
    except ValueError:
        raise UnauthorizedError("Token subject is not a valid identifier.")

    repo = UserRepository(db)
    user = await repo.get_active_user_by_id(user_id)

    if user is None:
        raise UnauthorizedError(
            "Account not found or has been deactivated. Please sign in again."
        )

    return user


async def get_optional_user(
    request: Request,
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """Like ``get_current_user`` but returns ``None`` instead of raising.

    Use this for endpoints that serve different content to authenticated
    vs. anonymous visitors.
    """
    authorization = request.headers.get("Authorization")
    if not authorization:
        return None
    try:
        return await get_current_user(request, db)
    except UnauthorizedError:
        return None


# ── Convenience type aliases ────────────────────────────────────
#
# Route handlers import these instead of the raw ``Depends(...)`` call.

CurrentUserDep = Annotated[User, Depends(get_current_user)]
OptionalUserDep = Annotated[User | None, Depends(get_optional_user)]
