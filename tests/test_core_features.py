"""
Name: test_core_features.py

Description: Tests for core ToolOps features like stale-if-error, circuit breaker, and tags.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio

import pytest

from toolops import build_cache_key, cache_manager, readonly, sideeffect
from toolops.cache import MemoryCache


@pytest.mark.asyncio
async def test_stale_if_error_returns_last_good_value():
    """Test stale-if-error serving during upstream failure."""

    cache_manager.register("memory", MemoryCache(), is_default=True)
    calls = 0

    @readonly(cache_backend="memory", cache_ttl=1, stale_ttl=5, stale_if_error=True)
    async def flaky_profile(user_id: str) -> dict[str, int | str]:
        nonlocal calls
        calls += 1
        if calls == 1:
            return {"user_id": user_id, "version": 1}
        raise ValueError("upstream down")

    first = await flaky_profile(user_id="alice")
    await asyncio.sleep(1.1)
    second = await flaky_profile(user_id="alice")

    assert second == first
    assert calls == 2

    entry = await cache_manager.inspect(
        "memory", build_cache_key("flaky_profile", {"user_id": "alice"}, None)
    )
    assert entry is not None
    assert entry["state"] == "stale"


@pytest.mark.asyncio
async def test_fallback_receives_error_and_returns_value():
    """Test fallback handler execution on tool failure."""

    cache_manager.register("memory", MemoryCache(), is_default=True)
    seen_error = None

    async def fallback(item: str, error: Exception) -> dict[str, str]:
        nonlocal seen_error
        seen_error = str(error)
        return {"item": item, "status": "fallback"}

    @readonly(cache_backend="memory", fallback=fallback)
    async def explode(item: str) -> dict[str, str]:
        raise ValueError("boom")

    result = await explode(item="report")

    assert result == {"item": "report", "status": "fallback"}
    assert seen_error is not None
    assert "boom" in seen_error


@pytest.mark.asyncio
async def test_circuit_breaker_short_circuits_after_threshold():
    """Test circuit breaker transition to OPEN after failures."""

    calls = 0

    @sideeffect(
        circuit_breaker=True,
        circuit_failure_threshold=2,
        circuit_recovery_timeout=60,
        fallback=lambda error: f"fallback:{type(error).__name__}",
    )
    async def unstable() -> str:
        nonlocal calls
        calls += 1
        raise RuntimeError("nope")

    first = await unstable()
    second = await unstable()
    third = await unstable()

    assert first == "fallback:RuntimeError"
    assert second == "fallback:RuntimeError"
    assert third == "fallback:CircuitOpenError"
    assert calls == 2


@pytest.mark.asyncio
async def test_invalidate_by_tags_only_evicts_matching_entries():
    """Test selective cache invalidation using tags."""

    cache_manager.register("memory", MemoryCache(), is_default=True)
    calls = 0

    @readonly(
        cache_backend="memory",
        cache_ttl=60,
        cache_tags=lambda kwargs: [f"user:{kwargs['user_id']}", "profile"],
    )
    async def load_profile(user_id: str) -> dict[str, int | str]:
        nonlocal calls
        calls += 1
        return {"user_id": user_id, "call": calls}

    alice_first = await load_profile(user_id="alice")
    bob_first = await load_profile(user_id="bob")
    alice_cached = await load_profile(user_id="alice")

    assert alice_cached == alice_first

    deleted = await cache_manager.invalidate("memory", tags=["user:alice"])
    assert deleted == 1

    alice_after = await load_profile(user_id="alice")
    bob_after = await load_profile(user_id="bob")

    assert alice_after["call"] == 3
    assert bob_after == bob_first


@pytest.mark.asyncio
async def test_coalescing_middleware_integration():
    """Test that coalesce=True correctly merges concurrent decorated calls."""
    cache_manager.register("memory", MemoryCache(), is_default=True)
    calls = 0

    @readonly(cache_backend="memory", cache_ttl=60, coalesce=True)
    async def expensive_op(val: int) -> int:
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.1)
        return val * 2

    # Fire 5 concurrent requests for the same value
    results = await asyncio.gather(*[expensive_op(val=10) for _ in range(5)])

    assert all(r == 20 for r in results)
    assert calls == 1
