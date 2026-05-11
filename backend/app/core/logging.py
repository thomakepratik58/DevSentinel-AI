from __future__ import annotations

import logging
import sys
from typing import Any

from app.core.config import settings


def _build_formatter() -> logging.Formatter:
    """Structured log format: timestamp, level, logger name, message."""
    return logging.Formatter(
        fmt="%(asctime)s  %(levelname)-8s  [%(name)s]  %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )


def setup_logging() -> logging.Logger:
    """Configure the root application logger.

    Returns the ``devsentinel`` logger instance.  All application code
    should use ``from app.core.logging import logger`` rather than
    creating its own logger.
    """
    level = logging.DEBUG if settings.is_development else logging.INFO

    root = logging.getLogger("devsentinel")
    root.setLevel(level)

    if not root.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        handler.setFormatter(_build_formatter())
        root.addHandler(handler)

    # Silence noisy third-party loggers
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)

    return root


logger: logging.Logger = setup_logging()
