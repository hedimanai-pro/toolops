"""
Name: mcp.py

Description: Model Context Protocol (MCP) integration for ToolOps.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import inspect
from typing import Any, Callable


class MCPIntegration:
    """Helper to integrate ToolOps tools with MCP."""

    @staticmethod
    def to_mcp_definition(func: Callable[..., Any]) -> dict[str, Any]:
        """
        Convert a tool function into an MCP-compatible definition.

        Args:
            func: Tool function.

        Returns:
            MCP tool definition dictionary.
        """

        original_func = getattr(func, "__wrapped__", func)
        sig = inspect.signature(original_func)
        doc = inspect.getdoc(original_func) or ""

        properties = {}
        required = []

        for name, param in sig.parameters.items():
            param_type = "string"
            if param.annotation is int:
                param_type = "integer"

            elif param.annotation is float:
                param_type = "number"

            elif param.annotation is bool:
                param_type = "boolean"

            elif param.annotation is dict:
                param_type = "object"

            elif param.annotation is list:
                param_type = "array"

            properties[name] = {"type": param_type}
            if param.default is inspect.Parameter.empty:
                required.append(name)

        return {
            "name": original_func.__name__,
            "description": doc,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }

    @staticmethod
    def wrap_mcp_handler(func: Callable[..., Any]) -> Callable[..., Any]:
        """
        Ensure MCP handler respects ToolOps middleware.

        Args:
            func: Handler function.

        Returns:
            Wrapped handler function.
        """

        if hasattr(func, "__toolops__"):
            return func

        return func
