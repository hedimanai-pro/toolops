"""
Name: test_sync_wrapper.py

Description: Tests for synchronous execution wrappers.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import pytest

from toolops import readonly


@readonly(cache_backend=None)
def sync_tool_wrapped(x: int) -> int:
    """
    A sample synchronous tool for testing wrappers.

    Args:
        x: Input integer.

    Returns:
        Double the input.
    """

    return x * 2


def test_sync_wrapper_no_loop():
    """Test sync-wrapped tool execution without an active event loop."""

    result = sync_tool_wrapped(10)
    assert result == 20


@pytest.mark.asyncio
async def test_sync_wrapper_standard_usage():
    """Verify sync-wrapped tool logic (placeholder for async context check)."""

    pass


def test_sync_call_works():
    """Test inline sync tool definition and execution."""

    @readonly(cache_backend=None)
    def add_sync(a: int, b: int) -> int:
        return a + b

    assert add_sync(5, 5) == 10
