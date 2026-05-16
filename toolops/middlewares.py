"""
Name: middlewares.py

Description: Middleware pipeline architecture for ToolOps decorators.
              Extracts cross-cutting concerns (cache, retry, circuit breaker,
              coalescing, logging) from the monolithic @tool decorator into
              independent, testable, composable middlewares.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import time
import asyncio
import inspect
from typing import Any, Callable
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from toolops.logger import logger
from toolops.observability import metrics
from toolops.coalescer import RequestCoalescer
from toolops.cache import CacheEntry, cache_manager
from toolops.resilience import CircuitBreaker, CircuitOpenError


@dataclass
class ToolContext:
    """Mutable context shared across all middlewares in a single tool call."""

    # Static configuration (set once at decoration time)
    tool_name: str
    cache_backend: str | None
    cache_ttl: int
    stale_if_error: bool
    stale_ttl: int | None
    coalesce: bool
    timeout: float | None
    retry_count: int
    retry_delay: float
    fallback: Callable[..., Any] | Any | None
    circuit_breaker: bool
    tags: list[str]

    # Mutable state (evolves during pipeline execution)
    key: str = ""
    entry_tags: list[str] = field(default_factory=list)
    start: float = 0.0
    stale_entry: CacheEntry | None = None
    breaker: CircuitBreaker | None = None
    kwargs: dict[str, Any] = field(default_factory=dict)
    result_recorded: bool = False


class Middleware(ABC):
    """Abstract base for all ToolOps middlewares."""

    @abstractmethod
    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        """
        Process the middleware logic and delegate to the next layer.

        Args:
            ctx: Shared tool execution context.
            call_next: Function to call the next middleware (or the tool itself).

        Returns:
            The tool execution result (possibly modified by the middleware).
        """


class FallbackMiddleware(Middleware):
    """Fallback execution when all retries are exhausted.

    Positioned FIRST in the pipeline so it catches errors from
    all upstream middlewares (circuit breaker, retry exhausted, etc.).
    """

    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        try:
            return await call_next()

        except Exception as exc:
            if ctx.fallback is None:
                raise

            result = await self._execute_fallback(ctx, exc)
            logger.warning("tool_fallback", tool=ctx.tool_name, reason=str(exc))
            metrics.record_tool_result(
                tool=ctx.tool_name, status="fallback",
                duration_s=time.monotonic() - ctx.start,
                cache=ctx.cache_backend, cached=False,
            )
            return result

    async def _execute_fallback(self, ctx: ToolContext, error: Exception) -> Any:
        fallback = ctx.fallback
        if not callable(fallback):
            return fallback

        signature = inspect.signature(fallback)
        call_kwargs: dict[str, Any] = {}
        accepts_var_kw = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values())

        if accepts_var_kw:
            call_kwargs.update(ctx.kwargs)
            call_kwargs["error"] = error
            call_kwargs["stale_value"] = ctx.stale_entry.value if ctx.stale_entry else None

        else:
            for name in signature.parameters:
                if name in ctx.kwargs:
                    call_kwargs[name] = ctx.kwargs[name]

                elif name == "error":
                    call_kwargs[name] = error

                elif name == "stale_value":
                    call_kwargs[name] = ctx.stale_entry.value if ctx.stale_entry else None

        result = fallback(**call_kwargs)
        if inspect.isawaitable(result):
            return await result
        return result


class LoggingMiddleware(Middleware):
    """Structured JSON logging for every tool call."""

    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        ctx.start = time.monotonic()
        logger.info("tool_start", tool=ctx.tool_name, tags=ctx.tags, params=ctx.kwargs)
        metrics.record_tool_start(tool=ctx.tool_name, cache=ctx.cache_backend)

        try:
            result = await call_next()
            ms = (time.monotonic() - ctx.start) * 1000
            logger.info("tool_success", tool=ctx.tool_name, duration_ms=round(ms, 2), cached=False)
            # Record success metrics only if not already recorded by CacheMiddleware
            if not ctx.result_recorded:
                metrics.record_tool_result(
                    tool=ctx.tool_name, status="success",
                    duration_s=time.monotonic() - ctx.start,
                    cache=ctx.cache_backend, cached=False,
                )
            return result

        except Exception:
            ms = (time.monotonic() - ctx.start) * 1000
            logger.error("tool_failed", tool=ctx.tool_name, duration_ms=round(ms, 2))
            raise


class CacheMiddleware(Middleware):
    """Cache lookup, stale-if-error fallback, and cache write."""

    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        if not ctx.cache_backend:
            return await call_next()

        cache = ctx.cache_backend

        # --- Cache lookup ---
        try:
            cached = await cache_manager.get(cache, ctx.key)
            if cached is not None:
                self._record_hit(ctx, "fresh")
                ctx.result_recorded = True
                return cached

            if ctx.stale_if_error:
                ctx.stale_entry = await cache_manager.get_entry(cache, ctx.key, allow_stale=True)

        except Exception as exc:
            logger.warning("cache_read_error", tool=ctx.tool_name, error=str(exc))

        # --- Execute tool ---
        try:
            result = await call_next()

        except Exception as exc:
            # Serve stale cache on error
            if ctx.stale_if_error and ctx.stale_entry is not None:
                self._record_stale(ctx, reason=str(exc))
                ctx.result_recorded = True
                return ctx.stale_entry.value
            raise

        # --- Cache write ---
        if result is not None:
            try:
                await cache_manager.set(cache, ctx.key, result, ctx.cache_ttl, tags=ctx.entry_tags, stale_ttl=ctx.stale_ttl)

            except Exception as exc:
                logger.warning("cache_write_error", tool=ctx.tool_name, error=str(exc))

        return result

    def _record_hit(self, ctx: ToolContext, hit_kind: str) -> None:
        ms = (time.monotonic() - ctx.start) * 1000
        logger.info("cache_hit", tool=ctx.tool_name, cache=ctx.cache_backend, duration_ms=round(ms, 2), stale=False)
        metrics.record_cache_hit(tool=ctx.tool_name, cache=ctx.cache_backend, hit_kind=hit_kind)
        metrics.record_tool_result(
            tool=ctx.tool_name, status="cached",
            duration_s=time.monotonic() - ctx.start,
            cache=ctx.cache_backend, cached=True,
        )

    def _record_stale(self, ctx: ToolContext, reason: str) -> None:
        logger.warning("cache_stale_served", tool=ctx.tool_name, cache=ctx.cache_backend, reason=reason)
        metrics.record_cache_hit(tool=ctx.tool_name, cache=ctx.cache_backend or "none", hit_kind="stale")
        metrics.record_tool_result(
            tool=ctx.tool_name, status="stale",
            duration_s=time.monotonic() - ctx.start,
            cache=ctx.cache_backend, cached=True,
        )


class RetryMiddleware(Middleware):
    """Retry loop with configurable count and exponential backoff.

    Propagates the original exception type when all retries are exhausted
    (does not wrap it in RuntimeError).
    """

    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        last_error: Exception | None = None

        for attempt in range(ctx.retry_count + 1):
            try:
                return await call_next()
            except Exception as exc:
                last_error = exc
                logger.warning("tool_retry", tool=ctx.tool_name, attempt=attempt + 1, of=ctx.retry_count + 1, reason=str(exc))
                metrics.record_retry(tool=ctx.tool_name)
                if attempt < ctx.retry_count:
                    await asyncio.sleep(ctx.retry_delay * (2 ** attempt))

        # All retries exhausted -- propagate the original exception
        assert last_error is not None
        raise last_error


class CircuitBreakerMiddleware(Middleware):
    """Circuit breaker protection around tool execution.

    Positioned AFTER RetryMiddleware so that only failures that survive
    all retries count toward the circuit breaker threshold.
    """

    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        if not ctx.circuit_breaker or ctx.breaker is None:
            return await call_next()

        try:
            ctx.breaker.before_call()

        except CircuitOpenError as exc:
            logger.warning("circuit_rejected", tool=ctx.tool_name, retry_after=round(exc.retry_after, 2))
            metrics.record_circuit_state(tool=ctx.tool_name, state="open")

            # Serve stale cache if circuit is open
            if ctx.stale_if_error and ctx.stale_entry is not None:
                logger.warning("cache_stale_served", tool=ctx.tool_name, cache=ctx.cache_backend, reason="circuit_open")
                metrics.record_cache_hit(tool=ctx.tool_name, cache=ctx.cache_backend or "none", hit_kind="stale")
                metrics.record_tool_result(tool=ctx.tool_name, status="stale", duration_s=time.monotonic() - ctx.start, cache=ctx.cache_backend, cached=True)
                return ctx.stale_entry.value

            raise

        try:
            result = await call_next()
            ctx.breaker.record_success()
            metrics.record_circuit_state(tool=ctx.tool_name, state="closed")
            return result

        except CircuitOpenError:
            # Do not count circuit-open rejections as failures; they are a control signal, not an execution failure.
            raise

        except Exception:
            ctx.breaker.record_failure()
            metrics.record_circuit_state(tool=ctx.tool_name, state=ctx.breaker.state)
            raise

        finally:
            ctx.breaker.finish_attempt()


class CoalescingMiddleware(Middleware):
    """Request coalescing -- collapse concurrent identical calls into one."""

    _coalescer = RequestCoalescer()
    async def process(self, ctx: ToolContext, call_next: Callable[[], Any]) -> Any:
        if not ctx.coalesce:
            return await call_next()

        return await self._coalescer.execute(ctx.key, lambda: call_next())


class ToolExecutor:
    """Orchestrates middleware execution in a pipeline."""

    def __init__(self, middlewares: list[Middleware]) -> None:
        self._middlewares = middlewares


    async def execute(self, ctx: ToolContext, func: Callable[..., Any]) -> Any:
        """
        Execute the middleware pipeline, ending with the user function.

        Args:
            ctx: Tool execution context.
            func: The user\'s tool function.

        Returns:
            Tool execution result.
        """

        index = 0
        async def call_next() -> Any:
            nonlocal index
            if index < len(self._middlewares):
                mw = self._middlewares[index]
                index += 1
                return await mw.process(ctx, call_next)

            # Final layer: call the user\'s function
            result = func(**ctx.kwargs)
            if inspect.isawaitable(result):
                if ctx.timeout:
                    return await asyncio.wait_for(result, timeout=ctx.timeout)

                return await result

            return result

        return await call_next()


DEFAULT_PIPELINE: list[type[Middleware]] = [
    FallbackMiddleware,       # 1st: catch all errors from upstream
    LoggingMiddleware,        # 2nd: log every call
    CacheMiddleware,          # 3rd: cache lookup / write
    RetryMiddleware,          # 4th: retry with backoff
    CircuitBreakerMiddleware, # 5th: count failures after retries
    CoalescingMiddleware,     # 6th: dedup right before execution
]


def build_executor(middleware_classes: list[type[Middleware]] | None = None) -> ToolExecutor:
    """
    Build a ToolExecutor with the given middleware classes.

    Args:
        middleware_classes: Ordered list of middleware classes.
                           Defaults to DEFAULT_PIPELINE.

    Returns:
        Configured ToolExecutor instance.
    """

    classes = middleware_classes or DEFAULT_PIPELINE
    return ToolExecutor([cls() for cls in classes])
