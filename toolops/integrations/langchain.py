"""
Name: langchain.py

Description: LangChain integration bridge for ToolOps.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
import functools
import inspect
from typing import Any, Callable


def _sync_wrapper(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Wrap an async function for synchronous execution.

    Args:
        func: Target function.

    Returns:
        Synchronous wrapper function.
    """

    @functools.wraps(func)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        result = func(*args, **kwargs)
        if inspect.isawaitable(result):
            return asyncio.run(result)
        return result

    return wrapped


def as_langchain_tool(
    func: Callable[..., Any], *, name: str | None = None, description: str | None = None
) -> Any:
    """
    Wrap a function as a LangChain StructuredTool.

    Args:
        func: Target function.
        name: Optional tool name.
        description: Optional tool description.

    Returns:
        LangChain StructuredTool instance.
    """

    try:
        from langchain_core.tools import StructuredTool
    except ImportError:
        try:
            from langchain.tools import StructuredTool
        except ImportError as exc:
            raise ImportError(
                "LangChain integration requires langchain or langchain-core."
            ) from exc

    tool_name = name or func.__name__
    tool_description = description or inspect.getdoc(func) or tool_name
    sync_func = _sync_wrapper(func)

    try:
        return StructuredTool.from_function(
            func=sync_func,
            coroutine=func if inspect.iscoroutinefunction(func) else None,
            name=tool_name,
            description=tool_description,
        )
    except TypeError:
        return StructuredTool.from_function(
            sync_func,
            coroutine=func if inspect.iscoroutinefunction(func) else None,
            name=tool_name,
            description=tool_description,
        )
