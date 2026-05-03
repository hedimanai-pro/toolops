"""
Name: logger.py

Description: Structured JSON logging for ToolOps SDK.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import sys
import json
import logging
from typing import Any
from datetime import datetime, timezone


class ToolOpsLogger:
    """Structured JSON logger for observability."""


    def __init__(self, name: str = "toolops", level: str = "INFO") -> None:
        """
        Initialize the structured logger.

        Args:
            name: Logger name.
            level: Logging level string.
        """

        self._logger = logging.getLogger(name)
        self._logger.setLevel(getattr(logging, level.upper(), logging.INFO))

        if not self._logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            handler.setFormatter(logging.Formatter("%(message)s"))
            self._logger.addHandler(handler)


    def info(self, event: str, **kw: Any) -> None:
        """
        Log an INFO level event.

        Args:
            event: Event identifier.
            kw: Additional context.
        """

        self._emit("INFO", event, **kw)


    def warning(self, event: str, **kw: Any) -> None:
        """
        Log a WARNING level event.

        Args:
            event: Event identifier.
            kw: Additional context.
        """

        self._emit("WARNING", event, **kw)


    def error(self, event: str, **kw: Any) -> None:
        """
        Log an ERROR level event.

        Args:
            event: Event identifier.
            kw: Additional context.
        """

        self._emit("ERROR", event, **kw)


    def debug(self, event: str, **kw: Any) -> None:
        """
        Log a DEBUG level event.

        Args:
            event: Event identifier.
            kw: Additional context.
        """

        self._emit("DEBUG", event, **kw)


    def _emit(self, level: str, event: str, **kw: Any) -> None:
        """
        Emit a formatted JSON log entry.

        Args:
            level: Log level.
            event: Event name.
            kw: Context fields.
        """

        entry: dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": level,
            "event": event,
            **kw,
        }
        self._logger.log(getattr(logging, level), json.dumps(entry, default=str))


logger = ToolOpsLogger()