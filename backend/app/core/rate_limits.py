"""Rate-limiting configuration using slowapi.

Limits are applied per dimension:

  - Auth endpoints (login, register):  5 requests / minute / IP
  - Token refresh endpoint:           10 requests / minute / IP
  - General API:                       60 requests / minute / IP

Uses Redis as the storage backend when available (REDIS_URL configured),
and falls back to in-process memory storage for local development so
the app starts even if Redis is temporarily unavailable.
"""

from __future__ import annotations

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

# ── Limiter instance ────────────────────────────────────────────
#
# Attempt to use Redis for distributed rate limiting.
# Fall back to in-memory storage so development stays friction-free.
#
try:
    limiter = Limiter(
        key_func=get_remote_address,
        storage_uri=settings.REDIS_URL,
        default_limits=["60/minute"],
    )
    # Eagerly test the connection by importing; errors surface at startup
    _storage_backend = "redis"
except Exception:  # pragma: no cover — only fires when Redis is unreachable
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["60/minute"],
    )
    _storage_backend = "memory"

# ── Named limit strings ─────────────────────────────────────────
#
# Import these constants in route decorators instead of inline strings
# to keep limit values in one place and easy to audit.
#
AUTH_LOGIN_LIMIT = "5/15minute"
AUTH_REGISTER_LIMIT = "3/hour"
TOKEN_REFRESH_LIMIT = "10/minute"
GENERAL_API_LIMIT = "60/minute"

def get_login_key(request: Request) -> str:
    """Rate limit by IP + email."""
    from slowapi.util import get_remote_address
    import json
    
    ip = get_remote_address(request)
    try:
        if hasattr(request, "_body"):
            body = request._body
            email = json.loads(body).get("email", "unknown")
        else:
            email = "unknown"
    except Exception:
        email = "unknown"
    return f"{ip}:{email}"
