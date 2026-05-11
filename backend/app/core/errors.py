from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import logger


# ── Typed error response schema ─────────────────────────────────


class APIErrorBody(BaseModel):
    """Standard error envelope returned by every failing endpoint.

    This shape is documented in the OpenAPI spec so frontend clients
    can rely on it for typed error handling.
    """

    error_code: str
    message: str
    details: Optional[Dict[str, Any]] = None
    trace_id: Optional[str] = None


# ── Base exception hierarchy ────────────────────────────────────


class BaseAPIException(Exception):
    """Root of the application exception hierarchy.

    Subclass this for domain-specific errors.  The global handler will
    serialize them into :class:`APIErrorBody`.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        self.details = details
        super().__init__(message)


class NotFoundError(BaseAPIException):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=f"{resource} '{identifier}' was not found.",
        )


class ConflictError(BaseAPIException):
    def __init__(self, message: str, error_code: str = "CONFLICT") -> None:
        super().__init__(status_code=409, error_code=error_code, message=message)


class ForbiddenError(BaseAPIException):
    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(status_code=403, error_code="FORBIDDEN", message=message)


class UnauthorizedError(BaseAPIException):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(status_code=401, error_code="UNAUTHORIZED", message=message)


class ValidationError(BaseAPIException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class RateLimitedError(BaseAPIException):
    def __init__(self, error_code: str = "RATE_LIMITED", message: str = "Too many requests.") -> None:
        super().__init__(status_code=429, error_code=error_code, message=message)


# ── Exception handlers ──────────────────────────────────────────


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle known application exceptions."""
    trace_id = getattr(request.state, "request_id", None)
    body = APIErrorBody(
        error_code=exc.error_code,
        message=exc.message,
        details=exc.details,
        trace_id=trace_id,
    )
    return JSONResponse(status_code=exc.status_code, content=body.model_dump(exclude_none=True))


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions.  Never leak stack traces."""
    trace_id = getattr(request.state, "request_id", None)
    logger.error("Unhandled exception  request_id=%s", trace_id, exc_info=exc)
    body = APIErrorBody(
        error_code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. If the problem persists, contact support.",
        trace_id=trace_id,
    )
    return JSONResponse(status_code=500, content=body.model_dump(exclude_none=True))
