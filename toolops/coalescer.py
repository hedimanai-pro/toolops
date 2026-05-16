"""
Name: coalescer.py

Description: Request coalescing for concurrent tool calls.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
from typing import Any, Callable


class RequestCoalescer:
    """Collapses concurrent calls with the same key into a single execution."""

    def __init__(self) -> None:
        """Initialize the pending requests store."""

        self._pending: dict[str, asyncio.Future[Any]] = {}

    async def execute(self, key: str, func: Callable[..., Any], **kwargs: Any) -> Any:
        """
        Execute function or wait for a pending execution of the same key.

        Args:
            key: Coalescing key.
            func: Function to execute.
            kwargs: Arguments for the function.

        Returns:
            Result of the execution.
        """

        if key in self._pending:
            return await asyncio.shield(self._pending[key])

        loop = asyncio.get_running_loop()
        future: asyncio.Future[Any] = loop.create_future()
        self._pending[key] = future

        try:
            result = await func(**kwargs)
            future.set_result(result)
            return result

        except Exception as exc:
            future.set_exception(exc)
            raise

        finally:
            self._pending.pop(key, None)
