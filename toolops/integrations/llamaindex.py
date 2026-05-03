"""
Name: llamaindex.py

Description: LlamaIndex integration bridge for ToolOps.

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


def as_llamaindex_tool(func: Callable[..., Any], *, name: str | None = None, description: str | None = None) -> Any:
    """
    Wrap a function as a LlamaIndex FunctionTool.

    Args:
        func: Target function.
        name: Optional tool name.
        description: Optional tool description.

    Returns:
        LlamaIndex FunctionTool instance.
    """

    try:
        from llama_index.core.tools import FunctionTool  # type: ignore[import]
    except ImportError:
        try:
            from llama_index.tools import FunctionTool  # type: ignore[import]
        except ImportError as exc:
            raise ImportError("LlamaIndex integration requires llama-index.") from exc

    tool_name = name or func.__name__
    tool_description = description or inspect.getdoc(func) or tool_name

    def sync_callable(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return asyncio.run(result)
        return result

    try:
        return FunctionTool.from_defaults(
            fn=sync_callable,
            async_fn=func if inspect.iscoroutinefunction(func) else None,
            name=tool_name,
            description=tool_description,
        )

    except TypeError:
        return FunctionTool.from_defaults(
            fn=sync_callable,
            name=tool_name,
            description=tool_description,
        )
