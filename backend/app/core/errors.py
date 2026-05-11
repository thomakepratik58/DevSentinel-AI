from __future__ import annotations

from typing import Any, Dict, Optional

from fastapi import Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.core.logging import logger


# ── Typed error response schema ─────────────────────────────────
#
# Every failing endpoint returns this exact envelope:
#
#   {
#     "error": {
#       "code": "NOT_FOUND",
#       "message": "Repository 'repo_abc' was not found.",
#       "requestId": "req_a1b2c3d4e5f6g7h8i9j0",
#       "retryable": false,
#       "details": {}
#     }
#   }


class APIErrorDetail(BaseModel):
    """Inner error payload."""

    code: str
    message: str
    requestId: str
    retryable: bool
    details: Dict[str, Any] = {}


class APIErrorEnvelope(BaseModel):
    """Top-level error envelope wrapping the error detail.

    Frontend clients rely on this exact shape for typed error
    handling across every endpoint.
    """

    error: APIErrorDetail


# ── Retryable status codes ──────────────────────────────────────

_RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})


# ── Base exception hierarchy ────────────────────────────────────


class BaseAPIException(Exception):
    """Root of the application exception hierarchy.

    Subclass this for domain-specific errors.  The global exception
    handlers serialize them into :class:`APIErrorEnvelope`.
    """

    def __init__(
        self,
        status_code: int,
        error_code: str,
        message: str,
        retryable: Optional[bool] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.status_code = status_code
        self.error_code = error_code
        self.message = message
        # Default: retryable if status code is in the retryable set
        self.retryable = retryable if retryable is not None else (status_code in _RETRYABLE_STATUS_CODES)
        self.details = details or {}
        super().__init__(message)


class NotFoundError(BaseAPIException):
    def __init__(self, resource: str, identifier: str) -> None:
        super().__init__(
            status_code=404,
            error_code="NOT_FOUND",
            message=f"{resource} '{identifier}' was not found.",
            retryable=False,
        )


class ConflictError(BaseAPIException):
    def __init__(self, message: str, error_code: str = "CONFLICT") -> None:
        super().__init__(
            status_code=409,
            error_code=error_code,
            message=message,
            retryable=False,
        )


class ForbiddenError(BaseAPIException):
    def __init__(self, message: str = "You do not have permission to perform this action.") -> None:
        super().__init__(
            status_code=403,
            error_code="FORBIDDEN",
            message=message,
            retryable=False,
        )


class UnauthorizedError(BaseAPIException):
    def __init__(self, message: str = "Authentication required.") -> None:
        super().__init__(
            status_code=401,
            error_code="UNAUTHORIZED",
            message=message,
            retryable=False,
        )


class ValidationError(BaseAPIException):
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None) -> None:
        super().__init__(
            status_code=422,
            error_code="VALIDATION_ERROR",
            message=message,
            retryable=False,
            details=details,
        )


class RateLimitedError(BaseAPIException):
    def __init__(self, error_code: str = "RATE_LIMITED", message: str = "Too many requests.") -> None:
        super().__init__(
            status_code=429,
            error_code=error_code,
            message=message,
            retryable=True,
        )


# ── Helpers ─────────────────────────────────────────────────────


def _build_error_envelope(
    code: str,
    message: str,
    request_id: str,
    retryable: bool,
    details: Dict[str, Any],
) -> Dict[str, Any]:
    """Build the canonical error response dict."""
    envelope = APIErrorEnvelope(
        error=APIErrorDetail(
            code=code,
            message=message,
            requestId=request_id,
            retryable=retryable,
            details=details,
        )
    )
    return envelope.model_dump()


# ── Exception handlers ──────────────────────────────────────────


async def api_exception_handler(request: Request, exc: BaseAPIException) -> JSONResponse:
    """Handle known application exceptions."""
    request_id: str = getattr(request.state, "request_id", "unknown")
    body = _build_error_envelope(
        code=exc.error_code,
        message=exc.message,
        request_id=request_id,
        retryable=exc.retryable,
        details=exc.details,
    )
    return JSONResponse(status_code=exc.status_code, content=body)


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unhandled exceptions.  Never leak stack traces."""
    request_id: str = getattr(request.state, "request_id", "unknown")
    logger.error("Unhandled exception  request_id=%s", request_id, exc_info=exc)
    body = _build_error_envelope(
        code="INTERNAL_SERVER_ERROR",
        message="An unexpected error occurred. If the problem persists, contact support.",
        request_id=request_id,
        retryable=True,
        details={},
    )
    return JSONResponse(status_code=500, content=body)
