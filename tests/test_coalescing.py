"""
Name: test_coalescing.py

Description: Tests for request coalescing logic.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import asyncio

import pytest

from toolops.coalescer import RequestCoalescer


@pytest.mark.asyncio
async def test_request_coalescer_merges_concurrent_calls():
    """Test that multiple concurrent calls result in only one execution."""
    coalescer = RequestCoalescer()
    calls = 0

    async def task():
        nonlocal calls
        calls += 1
        await asyncio.sleep(0.1)
        return "result"

    # Run 3 concurrent tasks
    results = await asyncio.gather(
        coalescer.execute("key1", task),
        coalescer.execute("key1", task),
        coalescer.execute("key1", task),
    )

    assert all(r == "result" for r in results)
    assert calls == 1


@pytest.mark.asyncio
async def test_request_coalescer_propagates_exception():
    """Test that exceptions are multicasted to all waiters."""
    coalescer = RequestCoalescer()

    async def failing_task():
        await asyncio.sleep(0.1)
        raise ValueError("failed")

    with pytest.raises(ValueError, match="failed"):
        await asyncio.gather(
            coalescer.execute("err1", failing_task),
            coalescer.execute("err1", failing_task),
        )


@pytest.mark.asyncio
async def test_request_coalescer_cleans_up_after_finish():
    """Test that key is removed from pending after execution."""
    coalescer = RequestCoalescer()

    async def task():
        return "ok"

    await coalescer.execute("k1", task)
    assert "k1" not in coalescer._pending

    # Second execution should run again
    await coalescer.execute("k1", task)
    assert "k1" not in coalescer._pending
