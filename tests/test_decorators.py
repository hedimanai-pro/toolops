import pytest

from toolops import cache_manager, readonly, sideeffect, stateful, tool
from toolops.cache import MemoryCache


@pytest.mark.asyncio
async def test_tool_decorator_initialization_variants():
    """Test all shortcut decorators and their default configs."""
    cache_manager.register("memory", MemoryCache(), is_default=True)

    @tool(cache_backend="memory")
    async def t1():
        return 1

    @readonly(cache_backend="memory")
    async def t2():
        return 2

    @sideeffect()
    async def t3():
        return 3

    @stateful(cache_backend="memory")
    async def t4():
        return 4

    assert await t1() == 1
    assert await t2() == 2
    assert await t3() == 3
    assert await t4() == 4


@pytest.mark.asyncio
async def test_decorator_with_sensitive_params():
    """Test sensitive_params exclusion from cache keys."""
    cache_manager.register("memory", MemoryCache(), is_default=True)

    @readonly(cache_backend="memory", sensitive_params=["api_key"])
    async def call_api(api_key: str, query: str):
        return f"result_{query}"

    # These two calls should share the same cache key because api_key is excluded
    await call_api(api_key="secret1", query="test")

    # Manually check cache
    stats = await cache_manager.stats()
    assert stats["memory"]["size"] == 1

    # Call with different api_key but same query
    res = await call_api(api_key="secret2", query="test")
    assert res == "result_test"

    stats = await cache_manager.stats()
    assert stats["memory"]["hits"] == 1
    assert stats["memory"]["size"] == 1


def test_build_cache_key_logic():
    """Test the low-level cache key construction logic."""
    from toolops.decorators import build_cache_key

    # Standard key
    k1 = build_cache_key("foo", {"a": 1, "b": 2}, None)
    k2 = build_cache_key("foo", {"b": 2, "a": 1}, None)
    assert k1 == k2

    # Selective key
    k3 = build_cache_key("foo", {"a": 1, "b": 2}, ["a"])
    k4 = build_cache_key("foo", {"a": 1, "c": 3}, ["a"])
    assert k3 == k4
    assert k3 != k1


def test_mask_params_logic():
    """Test the sensitive parameter masking for logs."""
    from toolops.decorators import _mask_sensitive_params

    params = {"query": "hello", "api_key": "secret123", "user_password": "p1"}
    masked = _mask_sensitive_params(params)

    assert masked["query"] == "hello"
    assert masked["api_key"] == "***MASKED***"
    assert masked["user_password"] == "***MASKED***"
