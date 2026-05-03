"""
Name: __init__.py

Description: ToolOps SDK core package initialization.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from importlib.metadata import PackageNotFoundError, version

from toolops.cache import (
    CacheBackend,
    CacheEntry,
    CacheManager,
    FileCache,
    MemoryCache,
    OpenAIEmbedder,
    PostgresCache,
    SemanticCache,
    SentenceTransformerEmbedder,
    cache_manager,
    cosine_similarity,
)
from toolops.logger import ToolOpsLogger, logger
from toolops.observability import configure_opentelemetry, prometheus_metrics
from toolops.decorators import build_cache_key, readonly, sideeffect, stateful, tool


try:
    __version__ = version("toolops")
except PackageNotFoundError:
    __version__ = "0.0.0-dev"

__author__ = "ToolOps AI"
__license__ = "Apache-2.0"

__all__ = [
    "tool",
    "build_cache_key",
    "readonly",
    "sideeffect",
    "stateful",
    "CacheBackend",
    "CacheEntry",
    "MemoryCache",
    "PostgresCache",
    "FileCache",
    "SemanticCache",
    "SentenceTransformerEmbedder",
    "OpenAIEmbedder",
    "CacheManager",
    "cache_manager",
    "cosine_similarity",
    "configure_opentelemetry",
    "prometheus_metrics",
    "ToolOpsLogger",
    "logger",
    "__version__",
]
