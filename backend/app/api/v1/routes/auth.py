"""Authentication routes — register, login, logout, refresh, me.

All five endpoints use the standard error envelope defined in
``app.core.errors``.  Route handlers stay thin: validate input,
call the service, shape the response.

Cookie strategy:
  - Refresh token → HttpOnly; SameSite=Lax; Secure (in production)
  - Access token  → JSON response body (held in-memory by the client)

Rate limits are enforced via slowapi decorators:
  - /register, /login  →  5 requests / minute / IP
  - /refresh           → 10 requests / minute / IP
"""

from fastapi import APIRouter, Depends, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.dependencies.auth import CurrentUserDep
from app.api.v1.schemas.auth import (
    LoginRequest,
    MessageResponse,
    RefreshResponse,
    RegisterRequest,
    TokenResponse,
    UserResponse,
)
from app.core.config import settings
from app.core.rate_limits import AUTH_ENDPOINT_LIMIT, TOKEN_REFRESH_LIMIT, limiter
from app.db.engine import get_db
from app.services.user_service import AuthService

router = APIRouter()

# ── Cookie configuration ─────────────────────────────────────────

_REFRESH_COOKIE_NAME = "refresh_token"
_REFRESH_COOKIE_MAX_AGE = settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60  # seconds


def _set_refresh_cookie(response: Response, raw_refresh_token: str) -> None:
    """Write the refresh token into a secure HttpOnly cookie."""
    response.set_cookie(
        key=_REFRESH_COOKIE_NAME,
        value=raw_refresh_token,
        max_age=_REFRESH_COOKIE_MAX_AGE,
        httponly=True,
        samesite="lax",
        secure=settings.is_production,
        path="/api/v1/auth",  # Cookie only sent to auth endpoints
    )


def _clear_refresh_cookie(response: Response) -> None:
    """Clear the refresh token cookie on logout."""
    response.delete_cookie(
        key=_REFRESH_COOKIE_NAME,
        path="/api/v1/auth",
        httponly=True,
        samesite="lax",
    )


# ── POST /auth/register ──────────────────────────────────────────


@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=201,
    summary="Register a new account",
    description=(
        "Create a new user account with email and password. "
        "A default workspace is provisioned automatically. "
        "Returns an access token and sets a refresh-token cookie."
    ),
)
@limiter.limit(AUTH_ENDPOINT_LIMIT)
async def register(
    request: Request,
    response: Response,
    payload: RegisterRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    user, token_pair = await service.register_user(
        email=payload.email,
        display_name=payload.display_name,
        password=payload.password,
    )
    _set_refresh_cookie(response, token_pair.raw_refresh_token)
    return TokenResponse(
        access_token=token_pair.access_token,
        expires_in=token_pair.expires_in,
        user=UserResponse.model_validate(user),
    )


# ── POST /auth/login ─────────────────────────────────────────────


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Sign in with email and password",
    description=(
        "Authenticate with email and password. "
        "Returns a short-lived access token and sets a rotating refresh-token cookie."
    ),
)
@limiter.limit(AUTH_ENDPOINT_LIMIT)
async def login(
    request: Request,
    response: Response,
    payload: LoginRequest,
    db: AsyncSession = Depends(get_db),
) -> TokenResponse:
    service = AuthService(db)
    user, token_pair = await service.login_user(
        email=payload.email,
        password=payload.password,
    )
    _set_refresh_cookie(response, token_pair.raw_refresh_token)
    return TokenResponse(
        access_token=token_pair.access_token,
        expires_in=token_pair.expires_in,
        user=UserResponse.model_validate(user),
    )


# ── POST /auth/logout ────────────────────────────────────────────


@router.post(
    "/logout",
    response_model=MessageResponse,
    summary="Sign out of the current session",
    description=(
        "Revoke the current refresh token. The access token will expire "
        "naturally within its 15-minute window. "
        "Requires a valid access token in the Authorization header."
    ),
)
async def logout(
    request: Request,
    response: Response,
    current_user: CurrentUserDep,
    db: AsyncSession = Depends(get_db),
) -> MessageResponse:
    raw_refresh = request.cookies.get(_REFRESH_COOKIE_NAME, "")
    if raw_refresh:
        service = AuthService(db)
        await service.logout_user(
            user_id=current_user.id,
            raw_refresh_token=raw_refresh,
        )
    _clear_refresh_cookie(response)
    return MessageResponse(message="Signed out successfully.")


# ── POST /auth/refresh ───────────────────────────────────────────


@router.post(
    "/refresh",
    response_model=RefreshResponse,
    summary="Rotate the refresh token and issue a new access token",
    description=(
        "Exchange a valid refresh token (from cookie) for a new access token. "
        "The old refresh token is immediately revoked and a new one is issued."
    ),
)
@limiter.limit(TOKEN_REFRESH_LIMIT)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncSession = Depends(get_db),
) -> RefreshResponse:
    raw_refresh = request.cookies.get(_REFRESH_COOKIE_NAME)
    if not raw_refresh:
        from app.core.errors import UnauthorizedError
        raise UnauthorizedError(
            "No refresh token found. Please sign in again."
        )

    service = AuthService(db)
    token_pair = await service.refresh_access_token(raw_refresh_token=raw_refresh)
    _set_refresh_cookie(response, token_pair.raw_refresh_token)

    return RefreshResponse(
        access_token=token_pair.access_token,
        expires_in=token_pair.expires_in,
    )


# ── GET /auth/me ─────────────────────────────────────────────────


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user's profile",
    description="Return the authenticated user's public profile. Requires a valid access token.",
)
async def get_current_user_profile(
    current_user: CurrentUserDep,
) -> UserResponse:
    return UserResponse.model_validate(current_user)
