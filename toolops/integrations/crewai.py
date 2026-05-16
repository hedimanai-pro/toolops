"""
Name: crewai.py

Description: CrewAI integration bridge for ToolOps.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
import inspect
from typing import Any, Callable


def as_crewai_tool(
    func: Callable[..., Any], *, name: str | None = None, description: str | None = None
) -> Any:
    """
    Wrap a function as a CrewAI-compatible tool.

    Args:
        func: Target function.
        name: Optional tool name.
        description: Optional tool description.

    Returns:
        CrewAI Tool instance.
    """

    try:
        from crewai import Tool as CrewTool
    except ImportError as exc:
        raise ImportError("CrewAI integration requires crewai.") from exc

    tool_name = name or func.__name__
    tool_description = description or inspect.getdoc(func) or tool_name

    def sync_callable(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return asyncio.run(result)  # type: ignore[arg-type]
        return result

    return CrewTool(name=tool_name, func=sync_callable, description=tool_description)
