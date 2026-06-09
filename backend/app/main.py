from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.core.config import settings
from app.core.errors import BaseAPIException, api_exception_handler, unhandled_exception_handler
from app.core.logging import logger
from app.core.middleware import RequestIDMiddleware
from app.core.rate_limits import limiter
from app.api.v1.api import api_router


def create_application() -> FastAPI:
    """Application factory.

    Assembles middleware, exception handlers, and routers into a
    ready-to-serve FastAPI instance.
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
    )

    # ── Rate limiter state ────────────────────────────────────────
    app.state.limiter = limiter

    # ── Middleware (order matters — outermost first) ──────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.FRONTEND_URL],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(SlowAPIMiddleware)
    app.add_middleware(RequestIDMiddleware)

    # ── Exception handlers ───────────────────────────────────────
    app.add_exception_handler(BaseAPIException, api_exception_handler)
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)

    # ── Routers ──────────────────────────────────────────────────
    app.include_router(api_router, prefix=settings.API_V1_STR)

    logger.info(
        "Application started  env=%s  api_prefix=%s",
        settings.ENVIRONMENT,
        settings.API_V1_STR,
    )

    return app


app = create_application()
