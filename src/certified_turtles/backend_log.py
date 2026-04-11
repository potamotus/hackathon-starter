"""Один канал логов «работы бэкенда» без шума uvicorn/системных INFO."""

from __future__ import annotations

import logging
import sys


def get_backend_logger() -> logging.Logger:
    """Логгер с отдельным handler на stderr; не наследует уровень root/uvicorn."""
    log = logging.getLogger("certified_turtles.backend")
    if log.handlers:
        return log
    log.setLevel(logging.INFO)
    h = logging.StreamHandler(sys.stderr)
    h.setLevel(logging.INFO)
    h.setFormatter(logging.Formatter("[backend] %(message)s"))
    log.addHandler(h)
    log.propagate = False
    return log
