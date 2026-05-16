"""
Name: langgraph.py

Description: LangGraph node integration for ToolOps functions.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import inspect
from typing import Any, Callable


def bind_langgraph_node(
    func: Callable[..., Any],
    *,
    arg_map: dict[str, str] | None = None,
    output_key: str | None = None,
) -> Callable[[dict[str, Any]], Any]:
    """
    Build a LangGraph-friendly node from a ToolOps function.

    Args:
        func: Target function.
        arg_map: Map of function params to state keys.
        output_key: Key to store result in state.

    Returns:
        LangGraph node function.
    """

    signature = inspect.signature(func)
    mapping = arg_map or {}

    async def node(state: dict[str, Any]) -> Any:
        kwargs: dict[str, Any] = {}
        for name, parameter in signature.parameters.items():
            state_key = mapping.get(name, name)
            if state_key in state:
                kwargs[name] = state[state_key]
            elif parameter.default is inspect._empty:
                raise KeyError(
                    f"Missing state key '{state_key}' for parameter '{name}'."
                )

        result = func(**kwargs)
        if inspect.isawaitable(result):
            result = await result

        if output_key is None:
            return result

        return {output_key: result}

    return node
