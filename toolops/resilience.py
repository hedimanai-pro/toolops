"""
Name: resilience.py

Description: Circuit breaker resilience logic for ToolOps SDK.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import time
from threading import Lock
from dataclasses import dataclass


class CircuitOpenError(RuntimeError):
    """Exception raised when the circuit is open."""


    def __init__(self, tool: str, retry_after: float) -> None:
        """
        Initialize circuit open error.

        Args:
            tool: Tool name.
            retry_after: Retry delay in seconds.
        """

        self.tool = tool
        self.retry_after = retry_after
        super().__init__(f"Circuit for '{tool}' is open. Retry after {retry_after:.2f}s.")


@dataclass(slots=True)
class CircuitSnapshot:
    """Snapshot of current circuit state."""

    state: str
    failures: int
    opened_at: float | None


class CircuitBreaker:
    """Thread-safe circuit breaker implementation."""


    def __init__(self, tool: str, *, failure_threshold: int = 5, recovery_timeout: float = 30.0) -> None:
        """
        Initialize the circuit breaker.

        Args:
            tool: Tool name.
            failure_threshold: Failures before opening.
            recovery_timeout: Seconds to wait before retry.
        """

        self._tool = tool
        self._failure_threshold = failure_threshold
        self._recovery_timeout = recovery_timeout
        self._state = "closed"
        self._failures = 0
        self._opened_at: float | None = None
        self._half_open_in_flight = False
        self._lock = Lock()


    @property
    def state(self) -> str:
        """
        Get current circuit state.

        Returns:
            State string (closed, open, half_open).
        """

        return self.snapshot().state


    def snapshot(self) -> CircuitSnapshot:
        """
        Get a snapshot of the breaker state.

        Returns:
            CircuitSnapshot instance.
        """

        with self._lock:
            return CircuitSnapshot(
                state=self._state,
                failures=self._failures,
                opened_at=self._opened_at,
            )


    def before_call(self) -> None:
        """
        Check circuit state before tool execution.

        Raises:
            CircuitOpenError: If circuit is open or half-open busy.
        """

        with self._lock:
            if self._state == "closed":
                return

            now = time.monotonic()

            if self._state == "open":
                assert self._opened_at is not None
                retry_after = self._recovery_timeout - (now - self._opened_at)

                if retry_after > 0:
                    raise CircuitOpenError(self._tool, retry_after)

                self._state = "half_open"
                self._half_open_in_flight = True
                return

            if self._state == "half_open":
                if self._half_open_in_flight:
                    raise CircuitOpenError(self._tool, self._recovery_timeout)
                self._half_open_in_flight = True


    def record_success(self) -> None:
        """Record a successful tool execution."""

        with self._lock:
            self._state = "closed"
            self._failures = 0
            self._opened_at = None
            self._half_open_in_flight = False


    def record_failure(self) -> None:
        """Record a failed tool execution."""

        with self._lock:
            now = time.monotonic()

            if self._state == "half_open":
                self._state = "open"
                self._opened_at = now
                self._half_open_in_flight = False
                return

            self._failures += 1

            if self._failures >= self._failure_threshold:
                self._state = "open"
                self._opened_at = now
                self._half_open_in_flight = False


    def finish_attempt(self) -> None:
        """Cleanup after a tool execution attempt."""

        with self._lock:
            if self._state == "half_open":
                self._half_open_in_flight = False