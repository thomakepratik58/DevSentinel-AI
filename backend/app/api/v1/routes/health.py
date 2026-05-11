from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Request
from pydantic import BaseModel

from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str
    timestamp: str
    requestId: str


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check(request: Request) -> HealthResponse:
    request_id: str = getattr(request.state, "request_id", "unknown")
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
        requestId=request_id,
    )
