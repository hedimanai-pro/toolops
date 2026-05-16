"""
Name: test_observability.py

Description: Tests for metrics and observability providers.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import pytest

from toolops import cache_manager, prometheus_metrics, readonly
from toolops.cache import MemoryCache


@pytest.mark.asyncio
async def test_prometheus_metrics_include_cache_and_duration_series():
    """Test that Prometheus metrics are correctly rendered after tool calls."""

    cache_manager.register("memory", MemoryCache(), is_default=True)

    @readonly(cache_backend="memory", cache_ttl=60)
    async def get_weather(city: str) -> dict[str, str]:
        return {"city": city}

    await get_weather(city="Paris")
    await get_weather(city="Paris")

    rendered = prometheus_metrics()

    assert "toolops_tool_calls_total" in rendered
    assert 'tool="get_weather"' in rendered
    assert 'status="success"' in rendered
    assert 'status="cached"' in rendered
    assert "toolops_tool_duration_seconds_bucket" in rendered
    assert "toolops_cache_hits_total" in rendered
