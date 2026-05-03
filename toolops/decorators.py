"""
Name: decorators.py

Description: Resilience and efficiency decorators for tool execution.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import json
import time
import asyncio
import inspect
import functools
from typing import Any, Callable

from toolops.logger import logger
from toolops.observability import metrics
from toolops.coalescer import RequestCoalescer
from toolops.cache import CacheEntry, cache_manager
from toolops.resilience import CircuitBreaker, CircuitOpenError


_coalescer = RequestCoalescer()
_circuit_breakers: dict[str, CircuitBreaker] = {}


def _cache_key(name: str, kwargs: dict[str, Any], key_params: list[str] | None) -> str:
    """
    Generate a stable cache key for a tool call.

    Args:
        name: Tool name.
        kwargs: Bound tool arguments.
        key_params: Specific parameters to include.

    Returns:
        Hashed or serialized key string.
    """

    if key_params:
        pairs = [[p, kwargs[p]] for p in key_params if p in kwargs]
    else:
        pairs = [[k, v] for k, v in sorted(kwargs.items())]

    return f"{name}:{json.dumps(pairs, default=str)}"


build_cache_key = _cache_key


def _bind(func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Bind positional and keyword arguments to function parameters.

    Args:
        func: Target function.
        args: Positional arguments.
        kwargs: Keyword arguments.

    Returns:
        Dictionary of all bound parameters.
    """

    params = list(inspect.signature(func).parameters.keys())
    merged = dict(kwargs)

    for index, value in enumerate(args):
        if index < len(params):
            merged.setdefault(params[index], value)

    return merged


def _resolve_cache_tags(tool_name: str, kwargs: dict[str, Any], cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None) -> list[str]:
    """
    Resolve cache tags from static list or dynamic function.

    Args:
        tool_name: Tool name.
        kwargs: Tool arguments.
        cache_tags: Tag source.

    Returns:
        Sorted list of tags.
    """

    dynamic_tags = cache_tags(kwargs) if callable(cache_tags) else (cache_tags or [])
    return sorted({f"tool:{tool_name}", *[str(tag) for tag in dynamic_tags]})


def _breaker_for(tool_name: str, *, failure_threshold: int, recovery_timeout: float) -> CircuitBreaker:
    """
    Get or create a circuit breaker for a tool.

    Args:
        tool_name: Tool name.
        failure_threshold: Threshold to open.
        recovery_timeout: Recovery wait time.

    Returns:
        CircuitBreaker instance.
    """

    breaker = _circuit_breakers.get(tool_name)

    if breaker is None:
        breaker = CircuitBreaker(tool_name, failure_threshold=failure_threshold, recovery_timeout=recovery_timeout)
        _circuit_breakers[tool_name] = breaker

    return breaker


async def _call_fallback(fallback: Callable[..., Any] | Any, *, kwargs: dict[str, Any], error: Exception, stale_entry: CacheEntry | None) -> Any:
    """
    Execute fallback handler with appropriate context.

    Args:
        fallback: Fallback function or static value.
        kwargs: Original tool arguments.
        error: Caught exception.
        stale_entry: Stale cache entry if any.

    Returns:
        Fallback execution result.
    """

    if not callable(fallback):
        return fallback

    signature = inspect.signature(fallback)
    call_kwargs: dict[str, Any] = {}
    accepts_var_kw = any(param.kind == inspect.Parameter.VAR_KEYWORD for param in signature.parameters.values())

    if accepts_var_kw:
        call_kwargs.update(kwargs)
        call_kwargs["error"] = error
        call_kwargs["stale_value"] = stale_entry.value if stale_entry else None

    else:
        for name in signature.parameters:
            if name in kwargs:
                call_kwargs[name] = kwargs[name]

            elif name == "error":
                call_kwargs[name] = error

            elif name == "stale_value":
                call_kwargs[name] = stale_entry.value if stale_entry else None

    result = fallback(**call_kwargs)

    if inspect.isawaitable(result):
        return await result

    return result


def tool(
    name: str | None = None,
    *,
    cache_backend: str | None = None,
    cache_ttl: int = 3600,
    cache_key_params: list[str] | None = None,
    cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None = None,
    stale_if_error: bool = False,
    stale_ttl: int | None = None,
    coalesce: bool = False,
    timeout: float | None = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    fallback: Callable[..., Any] | Any | None = None,
    circuit_breaker: bool = False,
    circuit_failure_threshold: int = 5,
    circuit_recovery_timeout: float = 30.0,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Universal decorator for AI agent tools.

    Args:
        name: Tool name.
        cache_backend: Cache backend name.
        cache_ttl: Cache TTL.
        cache_key_params: Params for key.
        cache_tags: Tags for invalidation.
        stale_if_error: Serve stale on error.
        stale_ttl: Stale window TTL.
        coalesce: Collapse concurrent calls.
        timeout: Execution timeout.
        retry_count: Retries on failure.
        retry_delay: Delay between retries.
        fallback: Fallback handler.
        circuit_breaker: Enable circuit breaker.
        circuit_failure_threshold: Breaker threshold.
        circuit_recovery_timeout: Breaker recovery.
        tags: Metric/log tags.

    Returns:
        Tool decorator.
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        tool_name = name or func.__name__
        tool_tags = tags or []
        breaker = _breaker_for(tool_name, failure_threshold=circuit_failure_threshold, recovery_timeout=circuit_recovery_timeout) if circuit_breaker else None

        async def _run(**kwargs: Any) -> Any:
            key = _cache_key(tool_name, kwargs, cache_key_params)
            entry_tags = _resolve_cache_tags(tool_name, kwargs, cache_tags)
            start = time.monotonic()
            stale_entry: CacheEntry | None = None

            logger.info("tool_start", tool=tool_name, tags=tool_tags, params=kwargs)
            metrics.record_tool_start(tool=tool_name, cache=cache_backend)

            with metrics.otel.start_span(f"toolops.{tool_name}", attributes={"toolops.tool": tool_name, "toolops.cache_backend": cache_backend or "none"}):
                if cache_backend:
                    try:
                        cached = await cache_manager.get(cache_backend, key)
                        if cached is not None:
                            ms = (time.monotonic() - start) * 1000
                            logger.info("cache_hit", tool=tool_name, cache=cache_backend, duration_ms=round(ms, 2), stale=False)
                            metrics.record_cache_hit(tool=tool_name, cache=cache_backend, hit_kind="fresh")
                            metrics.record_tool_result(tool=tool_name, status="cached", duration_s=time.monotonic() - start, cache=cache_backend, cached=True)
                            return cached

                        if stale_if_error:
                            stale_entry = await cache_manager.get_entry(cache_backend, key, allow_stale=True)

                    except Exception as exc:
                        logger.warning("cache_read_error", tool=tool_name, error=str(exc))

                if breaker is not None:
                    try:
                        breaker.before_call()

                    except CircuitOpenError as exc:
                        logger.warning("circuit_rejected", tool=tool_name, retry_after=round(exc.retry_after, 2))
                        metrics.record_circuit_state(tool=tool_name, state="open")
                        if stale_if_error and stale_entry is not None:
                            logger.warning("cache_stale_served", tool=tool_name, cache=cache_backend, reason="circuit_open")
                            metrics.record_cache_hit(tool=tool_name, cache=cache_backend or "none", hit_kind="stale")
                            metrics.record_tool_result(tool=tool_name, status="stale", duration_s=time.monotonic() - start, cache=cache_backend, cached=True)
                            return stale_entry.value

                        if fallback is not None:
                            result = await _call_fallback(fallback, kwargs=kwargs, error=exc, stale_entry=stale_entry)
                            logger.warning("tool_fallback", tool=tool_name, reason="circuit_open")
                            metrics.record_tool_result(tool=tool_name, status="fallback", duration_s=time.monotonic() - start, cache=cache_backend, cached=False)
                            return result
                        raise

                async def _execute() -> Any:
                    last: Exception | None = None
                    for attempt in range(retry_count + 1):
                        try:
                            result = func(**kwargs)
                            if inspect.isawaitable(result):
                                return await (asyncio.wait_for(result, timeout=timeout) if timeout else result)
                            return result

                        except Exception as exc:
                            last = exc
                            logger.warning("tool_retry", tool=tool_name, attempt=attempt + 1, of=retry_count + 1, reason=str(exc))
                            metrics.record_retry(tool=tool_name)
                            if attempt < retry_count:
                                await asyncio.sleep(retry_delay)

                    raise RuntimeError(f"[{tool_name}] failed after {retry_count + 1} attempt(s): {last}")

                try:
                    result = await _coalescer.execute(key, _execute) if coalesce else await _execute()
                    if breaker is not None:
                        breaker.record_success()
                        metrics.record_circuit_state(tool=tool_name, state="closed")

                except Exception as exc:
                    if breaker is not None:
                        breaker.record_failure()
                        metrics.record_circuit_state(tool=tool_name, state=breaker.state)
                        breaker.finish_attempt()

                    if stale_if_error and stale_entry is not None:
                        logger.warning("cache_stale_served", tool=tool_name, cache=cache_backend, reason=str(exc))
                        metrics.record_cache_hit(tool=tool_name, cache=cache_backend or "none", hit_kind="stale")
                        metrics.record_tool_result(tool=tool_name, status="stale", duration_s=time.monotonic() - start, cache=cache_backend, cached=True)
                        return stale_entry.value

                    if fallback is not None:
                        result = await _call_fallback(fallback, kwargs=kwargs, error=exc, stale_entry=stale_entry)
                        logger.warning("tool_fallback", tool=tool_name, reason=str(exc))
                        metrics.record_tool_result(tool=tool_name, status="fallback", duration_s=time.monotonic() - start, cache=cache_backend, cached=False)
                        return result

                    ms = (time.monotonic() - start) * 1000
                    logger.error("tool_failed", tool=tool_name, duration_ms=round(ms, 2))
                    metrics.record_tool_result(tool=tool_name, status="failed", duration_s=time.monotonic() - start, cache=cache_backend, cached=False)
                    raise

                finally:
                    if breaker is not None:
                        breaker.finish_attempt()

                if cache_backend and result is not None:
                    try:
                        await cache_manager.set(cache_backend, key, result, cache_ttl, tags=entry_tags, stale_ttl=stale_ttl)

                    except Exception as exc:
                        logger.warning("cache_write_error", tool=tool_name, error=str(exc))

                ms = (time.monotonic() - start) * 1000
                logger.info("tool_success", tool=tool_name, duration_ms=round(ms, 2), cached=False)
                metrics.record_tool_result(tool=tool_name, status="success", duration_s=time.monotonic() - start, cache=cache_backend, cached=False)
                return result

        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
                return await _run(**_bind(func, args, kwargs))
            return async_wrapper

        @functools.wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                loop = asyncio.get_running_loop()

            except RuntimeError:
                loop = None

            if loop and loop.is_running():
                return asyncio.run_coroutine_threadsafe(_run(**_bind(func, args, kwargs)), loop).result()

            return asyncio.run(_run(**_bind(func, args, kwargs)))

        return sync_wrapper

    return decorator


def readonly(
    cache_backend: str = "memory",
    cache_ttl: int = 3600,
    cache_key_params: list[str] | None = None,
    cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None = None,
    stale_if_error: bool = False,
    stale_ttl: int | None = None,
    coalesce: bool = False,
    timeout: float | None = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    fallback: Callable[..., Any] | Any | None = None,
    circuit_breaker: bool = False,
    circuit_failure_threshold: int = 5,
    circuit_recovery_timeout: float = 30.0,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for read-only tools with default memory caching.

    Args:
        cache_backend: Backend name.
        cache_ttl: TTL seconds.
        cache_key_params: Params for key.
        cache_tags: Tags for invalidation.
        stale_if_error: Serve stale on error.
        stale_ttl: Stale window.
        coalesce: Collapse concurrent.
        timeout: Execution timeout.
        retry_count: Retries.
        retry_delay: Delay.
        fallback: Fallback handler.
        circuit_breaker: Breaker enable.
        circuit_failure_threshold: Threshold.
        circuit_recovery_timeout: Recovery.
        tags: Metric/log tags.

    Returns:
        ReadOnly tool decorator.
    """

    return tool(
        cache_backend=cache_backend,
        cache_ttl=cache_ttl,
        cache_key_params=cache_key_params,
        cache_tags=cache_tags,
        stale_if_error=stale_if_error,
        stale_ttl=stale_ttl,
        coalesce=coalesce,
        timeout=timeout,
        retry_count=retry_count,
        retry_delay=retry_delay,
        fallback=fallback,
        circuit_breaker=circuit_breaker,
        circuit_failure_threshold=circuit_failure_threshold,
        circuit_recovery_timeout=circuit_recovery_timeout,
        tags=(tags or []) + ["readonly"],
    )


def sideeffect(
    timeout: float | None = None,
    retry_count: int = 0,
    retry_delay: float = 1.0,
    fallback: Callable[..., Any] | Any | None = None,
    circuit_breaker: bool = False,
    circuit_failure_threshold: int = 5,
    circuit_recovery_timeout: float = 30.0,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for tools with side effects (no caching).

    Args:
        timeout: Execution timeout.
        retry_count: Retries.
        retry_delay: Delay.
        fallback: Fallback handler.
        circuit_breaker: Breaker enable.
        circuit_failure_threshold: Threshold.
        circuit_recovery_timeout: Recovery.
        tags: Metric/log tags.

    Returns:
        SideEffect tool decorator.
    """

    return tool(
        cache_backend=None,
        timeout=timeout,
        retry_count=retry_count,
        retry_delay=retry_delay,
        fallback=fallback,
        circuit_breaker=circuit_breaker,
        circuit_failure_threshold=circuit_failure_threshold,
        circuit_recovery_timeout=circuit_recovery_timeout,
        tags=(tags or []) + ["sideeffect"],
    )


def stateful(
    cache_backend: str = "memory",
    cache_ttl: int = 1800,
    cache_key_params: list[str] | None = None,
    cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None = None,
    stale_if_error: bool = False,
    stale_ttl: int | None = None,
    timeout: float | None = None,
    retry_count: int = 1,
    retry_delay: float = 1.0,
    fallback: Callable[..., Any] | Any | None = None,
    circuit_breaker: bool = False,
    circuit_failure_threshold: int = 5,
    circuit_recovery_timeout: float = 30.0,
    tags: list[str] | None = None,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorator for stateful tools with short-term caching and retries.

    Args:
        cache_backend: Backend name.
        cache_ttl: TTL seconds.
        cache_key_params: Params for key.
        cache_tags: Tags for invalidation.
        stale_if_error: Serve stale on error.
        stale_ttl: Stale window.
        timeout: Execution timeout.
        retry_count: Retries.
        retry_delay: Delay.
        fallback: Fallback handler.
        circuit_breaker: Breaker enable.
        circuit_failure_threshold: Threshold.
        circuit_recovery_timeout: Recovery.
        tags: Metric/log tags.

    Returns:
        Stateful tool decorator.
    """

    return tool(
        cache_backend=cache_backend,
        cache_ttl=cache_ttl,
        cache_key_params=cache_key_params,
        cache_tags=cache_tags,
        stale_if_error=stale_if_error,
        stale_ttl=stale_ttl,
        timeout=timeout,
        retry_count=retry_count,
        retry_delay=retry_delay,
        fallback=fallback,
        circuit_breaker=circuit_breaker,
        circuit_failure_threshold=circuit_failure_threshold,
        circuit_recovery_timeout=circuit_recovery_timeout,
        tags=(tags or []) + ["stateful"],
    )
