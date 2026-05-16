"""
Name: __init__.py

Description: ToolOps public API exports.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

from toolops.decorators import (
    tool,
    readonly,
    sideeffect,
    stateful,
    build_cache_key,
)
from toolops.cache import cache_manager
from toolops.observability import prometheus_metrics

# v0.2.0 — middleware pipeline (new public API)
from toolops.middlewares import (
    ToolContext,
    ToolExecutor,
    Middleware,
    LoggingMiddleware,
    CacheMiddleware,
    CircuitBreakerMiddleware,
    RetryMiddleware,
    CoalescingMiddleware,
    FallbackMiddleware,
    build_executor,
    DEFAULT_PIPELINE,
)

__all__ = [
    # Decorators
    "tool",
    "readonly",
    "sideeffect",
    "stateful",
    "build_cache_key",
    # Core components
    "cache_manager",
    "prometheus_metrics",
    # Middleware pipeline (v0.2.0)
    "ToolContext",
    "ToolExecutor",
    "Middleware",
    "LoggingMiddleware",
    "CacheMiddleware",
    "CircuitBreakerMiddleware",
    "RetryMiddleware",
    "CoalescingMiddleware",
    "FallbackMiddleware",
    "build_executor",
    "DEFAULT_PIPELINE",
]
