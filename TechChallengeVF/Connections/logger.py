# -*- coding: utf-8 -*-
"""
Structured JSON logging.

Emits one JSON object per line to both stdout and a rotating log file, so the
"JSON-structured logs / resilient exception management" requirement is met and
the [NEW] / [CHANGED] / [DELETED] change-detection alerts are machine-readable.
"""
import json
import logging
import sys
from datetime import datetime, timezone
from logging.handlers import RotatingFileHandler

from .config import LOG_FILE


class JsonFormatter(logging.Formatter):
    """Render each log record as a single-line JSON object."""

    def format(self, record):
        payload = {
            "level": record.levelname,
            # Event time from the record itself (UTC, ISO-8601) — not "now",
            # so timestamps reflect when the event happened, not when it printed.
            "timestamp": datetime.fromtimestamp(
                record.created, tz=timezone.utc
            ).isoformat(),
            "logger": record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False)


def _build_logger():
    log = logging.getLogger("monge_logger")
    log.setLevel(logging.INFO)
    # Guard against duplicate handlers when this module is imported repeatedly.
    if log.handlers:
        return log
    log.propagate = False

    formatter = JsonFormatter()

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setFormatter(formatter)
    log.addHandler(stream_handler)

    # encoding=utf-8 avoids UnicodeEncodeError on Windows (cp1252) when product
    # titles / prices contain ₡, ñ, etc. Rotation keeps the file bounded.
    file_handler = RotatingFileHandler(
        LOG_FILE, maxBytes=2_000_000, backupCount=3, encoding="utf-8"
    )
    file_handler.setFormatter(formatter)
    log.addHandler(file_handler)

    return log


logger = _build_logger()
