"""
Name: test_langgraph_integration.py

Description: Tests for LangGraph integration.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import pytest

from toolops.integrations.langgraph import bind_langgraph_node


@pytest.mark.asyncio
async def test_bind_langgraph_node_maps_state_and_wraps_output():
    """Test LangGraph node binding with arg mapping and output key."""

    async def get_weather(city: str) -> dict[str, str]:
        return {"city": city, "status": "sunny"}

    node = bind_langgraph_node(
        get_weather,
        arg_map={"city": "target_city"},
        output_key="weather",
    )

    result = await node({"target_city": "Paris"})

    assert result == {"weather": {"city": "Paris", "status": "sunny"}}
