"""
Name: __init__.py

Description: ToolOps public API exports.

Last_updated: 2026-05-30

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

from toolops.cache import cache_manager
from toolops.decorators import (
    build_cache_key,
    readonly,
    sideeffect,
    stateful,
    tool,
)

# v1.0.0 — middleware pipeline
from toolops.middlewares import (
    DEFAULT_PIPELINE,
    CacheMiddleware,
    CircuitBreakerMiddleware,
    CoalescingMiddleware,
    FallbackMiddleware,
    LoggingMiddleware,
    Middleware,
    RetryMiddleware,
    ToolContext,
    ToolExecutor,
    build_executor,
)
from toolops.observability import configure_opentelemetry, prometheus_metrics

__version__ = "1.0.0"

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
    "configure_opentelemetry",
    "__version__",
    # Middleware pipeline (v1.0.0)
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
