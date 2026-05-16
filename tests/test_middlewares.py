"""
Name: test_middlewares.py

Description: Tests for the middleware pipeline architecture.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import pytest

from toolops.middlewares import (
    FallbackMiddleware,
    RetryMiddleware,
    ToolContext,
    ToolExecutor,
)


@pytest.mark.asyncio
async def test_tool_executor_pipeline_execution():
    """Test the orchestration of multiple middlewares."""
    ctx = ToolContext(
        tool_name="test_tool",
        cache_backend=None,
        cache_ttl=60,
        stale_if_error=False,
        stale_ttl=None,
        coalesce=False,
        timeout=None,
        retry_count=0,
        retry_delay=0.1,
        fallback=None,
        circuit_breaker=False,
        tags=["unit-test"],
        kwargs={"x": 1},
    )

    # Simple middleware that adds to context
    class TraceMiddleware:
        async def process(self, ctx, call_next):
            ctx.kwargs["traced"] = True
            return await call_next()

    executor = ToolExecutor([TraceMiddleware()])

    async def tool_func(x, traced=False):
        return x + 1 if traced else x

    result = await executor.execute(ctx, tool_func)
    assert result == 2


@pytest.mark.asyncio
async def test_retry_middleware_logic():
    """Test that retry middleware actually retries on failure."""
    ctx = ToolContext(
        tool_name="retry_tool",
        cache_backend=None,
        cache_ttl=0,
        stale_if_error=False,
        stale_ttl=None,
        coalesce=False,
        timeout=None,
        retry_count=2,
        retry_delay=0.01,
        fallback=None,
        circuit_breaker=False,
        tags=[],
        kwargs={},
    )

    calls = 0

    async def flaky():
        nonlocal calls
        calls += 1
        if calls < 3:
            raise ValueError("try again")
        return "success"

    executor = ToolExecutor([RetryMiddleware()])
    result = await executor.execute(ctx, flaky)

    assert result == "success"
    assert calls == 3


@pytest.mark.asyncio
async def test_fallback_middleware_executes_callable():
    """Test that fallback middleware calls the fallback function."""

    async def my_fallback(error):
        return f"caught {type(error).__name__}"

    ctx = ToolContext(
        tool_name="fail_tool",
        cache_backend=None,
        cache_ttl=0,
        stale_if_error=False,
        stale_ttl=None,
        coalesce=False,
        timeout=None,
        retry_count=0,
        retry_delay=0,
        fallback=my_fallback,
        circuit_breaker=False,
        tags=[],
        kwargs={},
    )

    async def fail():
        raise RuntimeError("boom")

    executor = ToolExecutor([FallbackMiddleware()])
    result = await executor.execute(ctx, fail)

    assert result == "caught RuntimeError"


@pytest.mark.asyncio
async def test_cache_middleware_stale_if_error():
    """Test stale-if-error logic in CacheMiddleware."""
    from toolops.cache import MemoryCache, cache_manager
    from toolops.middlewares import CacheMiddleware

    cache = MemoryCache()
    cache_manager.register("m2", cache)

    # Pre-seed stale entry
    await cache.set("k1", "stale_val", ttl=-10, stale_ttl=60)

    ctx = ToolContext(
        tool_name="stale_tool",
        cache_backend="m2",
        key="k1",
        cache_ttl=60,
        stale_if_error=True,
        stale_ttl=60,
        coalesce=False,
        timeout=None,
        retry_count=0,
        retry_delay=0,
        fallback=None,
        circuit_breaker=False,
        tags=[],
        kwargs={},
    )

    async def failing_tool():
        raise ValueError("dead")

    executor = ToolExecutor([CacheMiddleware()])
    # Should return stale value instead of raising
    result = await executor.execute(ctx, failing_tool)
    assert result == "stale_val"
