"""
Name: decorators.py

Description: Resilience and efficiency decorators for tool execution.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
import functools
import hashlib
import inspect
import json
from typing import Any, Callable

from toolops.cache import CacheEntry
from toolops.coalescer import RequestCoalescer
from toolops.middlewares import ToolContext, build_executor
from toolops.observability import metrics
from toolops.resilience import CircuitBreaker

_coalescer = RequestCoalescer()
_circuit_breakers: dict[str, CircuitBreaker] = {}


def _cache_key(
    name: str,
    kwargs: dict[str, Any],
    key_params: list[str] | None,
    sensitive_params: list[str] | None = None,
) -> str:
    """
    Generate a stable, SHA-256 hashed cache key for a tool call.

    Prevents sensitive data (tokens, PII) from appearing in plaintext
    in cache keys and logs. Added in v0.2.0.

    Args:
        name: Tool name.
        kwargs: Bound tool arguments.
        key_params: Specific parameters to include.
        sensitive_params: Parameter names to exclude from the key.

    Returns:
        SHA-256 hashed key string (hex digest).
    """

    sensitive = set(sensitive_params or [])

    if key_params:
        pairs = [
            [p, kwargs[p]] for p in key_params if p in kwargs and p not in sensitive
        ]
    else:
        pairs = [[k, v] for k, v in sorted(kwargs.items()) if k not in sensitive]

    raw = f"{name}:{json.dumps(pairs, default=str)}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


build_cache_key = _cache_key


# Parameter names commonly containing sensitive data — auto-masked in logs.
_SENSITIVE_PARAM_NAMES = frozenset(
    {
        "token",
        "api_key",
        "apikey",
        "password",
        "secret",
        "auth",
        "authorization",
        "key",
        "credential",
        "credentials",
        "access_token",
        "refresh_token",
        "private_key",
        "bearer",
    }
)


def _mask_sensitive_params(kwargs: dict[str, Any]) -> dict[str, Any]:
    """
    Return a copy of kwargs with sensitive values masked for logging.

    Any parameter whose name contains a known sensitive keyword
    has its value replaced with '***MASKED***'.

    Args:
        kwargs: Original tool arguments.

    Returns:
        Sanitized arguments safe for logging.
    """

    masked: dict[str, Any] = {}
    for key, value in kwargs.items():
        lower_key = key.lower()
        if any(s in lower_key for s in _SENSITIVE_PARAM_NAMES):
            masked[key] = "***MASKED***"
        else:
            masked[key] = value
    return masked


def _bind(
    func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> dict[str, Any]:
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


def _resolve_cache_tags(
    tool_name: str,
    kwargs: dict[str, Any],
    cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None,
) -> list[str]:
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


def _breaker_for(
    tool_name: str, *, failure_threshold: int, recovery_timeout: float
) -> CircuitBreaker:
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
        breaker = CircuitBreaker(
            tool_name,
            failure_threshold=failure_threshold,
            recovery_timeout=recovery_timeout,
        )
        _circuit_breakers[tool_name] = breaker

    return breaker


async def _call_fallback(
    fallback: Callable[..., Any] | Any,
    *,
    kwargs: dict[str, Any],
    error: Exception,
    stale_entry: CacheEntry | None,
) -> Any:
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
    accepts_var_kw = any(
        param.kind == inspect.Parameter.VAR_KEYWORD
        for param in signature.parameters.values()
    )

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
    sensitive_params: list[str] | None = None,
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
        sensitive_params: Param names to exclude from cache key and logs.
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
        breaker = (
            _breaker_for(
                tool_name,
                failure_threshold=circuit_failure_threshold,
                recovery_timeout=circuit_recovery_timeout,
            )
            if circuit_breaker
            else None
        )

        # Build the middleware pipeline for this tool (v0.2.0 — refactored from monolithic)
        _executor = build_executor()

        async def _run(**kwargs: Any) -> Any:
            key = _cache_key(tool_name, kwargs, cache_key_params, sensitive_params)
            entry_tags = _resolve_cache_tags(tool_name, kwargs, cache_tags)

            ctx = ToolContext(
                tool_name=tool_name,
                cache_backend=cache_backend,
                cache_ttl=cache_ttl,
                stale_if_error=stale_if_error,
                stale_ttl=stale_ttl,
                coalesce=coalesce,
                timeout=timeout,
                retry_count=retry_count,
                retry_delay=retry_delay,
                fallback=fallback,
                circuit_breaker=circuit_breaker,
                tags=tool_tags,
                key=key,
                entry_tags=entry_tags,
                breaker=breaker,
                kwargs=kwargs,
            )

            with metrics.otel.start_span(
                f"toolops.{tool_name}",
                attributes={
                    "toolops.tool": tool_name,
                    "toolops.cache_backend": cache_backend or "none",
                },
            ):
                return await _executor.execute(ctx, func)

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
                return asyncio.run_coroutine_threadsafe(
                    _run(**_bind(func, args, kwargs)), loop
                ).result()

            return asyncio.run(_run(**_bind(func, args, kwargs)))

        return sync_wrapper

    return decorator


def readonly(
    cache_backend: str = "memory",
    cache_ttl: int = 3600,
    cache_key_params: list[str] | None = None,
    cache_tags: list[str] | Callable[[dict[str, Any]], list[str]] | None = None,
    sensitive_params: list[str] | None = None,
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
        sensitive_params=sensitive_params,
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
    sensitive_params: list[str] | None = None,
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
        sensitive_params: Param names to exclude from cache key and logs.
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
        sensitive_params=sensitive_params,
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
    sensitive_params: list[str] | None = None,
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
        sensitive_params: Param names to exclude from cache key and logs.
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
        sensitive_params=sensitive_params,
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
