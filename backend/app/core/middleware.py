from __future__ import annotations

import time
import uuid

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.types import ASGIApp

from app.core.logging import logger


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Attach a unique request ID to every inbound request.

    The ID is:
    * stored on ``request.state.request_id`` for use in error handlers
      and service-layer logging,
    * returned as ``X-Request-ID`` response header for client correlation,
    * logged alongside the method, path, status code, and duration.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        request_id = f"req_{uuid.uuid4().hex[:24]}"
        request.state.request_id = request_id

        start = time.perf_counter()

        response = await call_next(request)

        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Process-Time-Ms"] = f"{elapsed_ms:.1f}"

        logger.info(
            "%s %s  status=%d  %.1fms  id=%s",
            request.method,
            request.url.path,
            response.status_code,
            elapsed_ms,
            request_id,
        )

        return response
