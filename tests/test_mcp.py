"""
Name: test_mcp.py

Description: Tests for Model Context Protocol (MCP) integration.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import pytest

from toolops import readonly
from toolops.integrations.mcp import MCPIntegration


@readonly(cache_backend="memory")
async def sample_tool(city: str, temperature: float, is_raining: bool = False) -> str:
    """
    A sample tool for testing MCP conversion.

    Args:
        city: City name.
        temperature: Current temperature.
        is_raining: Rain status.

    Returns:
        Formatted weather string.
    """

    return f"Weather in {city}: {temperature}C"


def test_mcp_definition_conversion():
    """Test conversion of ToolOps tools to MCP JSON Schema."""

    definition = MCPIntegration.to_mcp_definition(sample_tool)

    assert definition["name"] == "sample_tool"
    assert "sample tool for testing mcp conversion" in definition["description"].lower()

    schema = definition["inputSchema"]
    assert schema["type"] == "object"
    assert "city" in schema["properties"]
    assert "temperature" in schema["properties"]
    assert "is_raining" in schema["properties"]

    assert schema["properties"]["city"]["type"] == "string"
    assert schema["properties"]["temperature"]["type"] == "number"
    assert schema["properties"]["is_raining"]["type"] == "boolean"

    assert "city" in schema["required"]
    assert "temperature" in schema["required"]
    assert "is_raining" not in schema["required"]


def test_mcp_wrap_handler():
    """Test MCP handler wrapping (no-op check)."""

    wrapped = MCPIntegration.wrap_mcp_handler(sample_tool)
    assert wrapped == sample_tool
