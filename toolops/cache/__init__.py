"""
Name: __init__.py

Description: Initialization for ToolOps cache package. Exposes all cache backends and manager.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

from typing import Any

from toolops.logger import logger
from toolops.observability import metrics

from .base import CacheBackend, CacheEntry
from .file import FileCache
from .memory import MemoryCache
from .mysql import MySQLCache
from .postgres import PostgresCache
from .semantic import OpenAIEmbedder, SemanticCache, SentenceTransformerEmbedder
from .sqlite import SQLiteCache
from .valkey import RedisCache, ValkeyCache


class CacheManager:
    """Central coordinator for multiple cache backends."""

    def __init__(self) -> None:
        """Initialize backend registry."""
        self._backends: dict[str, CacheBackend] = {}
        self._default: str | None = None

    def register(
        self, name: str, backend: CacheBackend, is_default: bool = False
    ) -> None:
        """
        Register a cache backend.

        Args:
            name: Backend identifier.
            backend: Backend instance.
            is_default: Set as default.
        """
        self._backends[name] = backend
        if is_default or self._default is None:
            self._default = name

        logger.info(
            "cache_registered",
            cache=name,
            backend=backend.__class__.__name__,
            default=self._default == name,
        )

    def _resolve(self, name: str) -> CacheBackend:
        """
        Resolve backend name to instance.

        Args:
            name: Backend name.

        Returns:
            Backend instance.
        """
        if name not in self._backends:
            raise KeyError(
                f"Cache '{name}' is not registered. "
                f"Call cache_manager.register('{name}', <backend>) first."
            )
        return self._backends[name]

    def backend(self, name: str) -> CacheBackend:
        """
        Get backend by name.

        Args:
            name: Backend name.

        Returns:
            Backend instance.
        """
        return self._resolve(name)

    async def get(self, name: str, key: str) -> Any | None:
        """
        Get value from specific cache.

        Args:
            name: Cache name.
            key: Cache key.

        Returns:
            Value or None.
        """
        return await self._resolve(name).get(key)

    async def get_entry(
        self, name: str, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get full entry from specific cache.

        Args:
            name: Cache name.
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        return await self._resolve(name).get_entry(key, allow_stale=allow_stale)

    async def set(
        self,
        name: str,
        key: str,
        value: Any,
        ttl: int,
        *,
        tags: list[str] | None = None,
        stale_ttl: int | None = None,
    ) -> None:
        """
        Store value in specific cache.

        Args:
            name: Cache name.
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        await self._resolve(name).set(key, value, ttl, tags=tags, stale_ttl=stale_ttl)

    async def delete(self, name: str, key: str) -> None:
        """
        Delete key from specific cache.

        Args:
            name: Cache name.
            key: Cache key.
        """
        await self._resolve(name).delete(key)

    async def clear(self, name: str) -> None:
        """
        Clear specific cache.

        Args:
            name: Cache name.
        """
        await self._resolve(name).clear()

    async def invalidate(
        self, name: str, *, tags: list[str] | None = None, keys: list[str] | None = None
    ) -> int:
        """
        Invalidate cache by tags or keys.

        Args:
            name: Cache name.
            tags: Optional tags.
            keys: Optional keys.

        Returns:
            Invalidated count.
        """
        deleted = 0
        if keys:
            for key in keys:
                await self.delete(name, key)
                deleted += 1

        if tags:
            deleted += await self._resolve(name).invalidate_tags(tags)

        if tags or keys:
            logger.info(
                "cache_invalidated",
                cache=name,
                deleted=deleted,
                tags=tags or [],
                keys=keys or [],
            )
            metrics.record_invalidation(cache=name, count=deleted)

        return deleted

    async def inspect(self, name: str, key: str) -> dict[str, Any] | None:
        """
        Inspect key in specific cache.

        Args:
            name: Cache name.
            key: Cache key.

        Returns:
            Metadata dict.
        """
        return await self._resolve(name).inspect(key)

    async def connect_all(self) -> None:
        """Initialize all registered backends."""
        for backend in self._backends.values():
            if hasattr(backend, "connect"):
                await backend.connect()

    async def stats(self) -> dict[str, Any]:
        """
        Get stats for all caches.

        Returns:
            Dictionary of stats.
        """
        return {name: await backend.stats() for name, backend in self._backends.items()}

    @property
    def registered(self) -> list[str]:
        """
        List registered cache names.

        Returns:
            List of names.
        """
        return list(self._backends.keys())


cache_manager = CacheManager()

__all__ = [
    "CacheBackend",
    "CacheEntry",
    "CacheManager",
    "cache_manager",
    "MemoryCache",
    "FileCache",
    "PostgresCache",
    "SemanticCache",
    "SentenceTransformerEmbedder",
    "OpenAIEmbedder",
    "SQLiteCache",
    "ValkeyCache",
    "RedisCache",
    "MySQLCache",
]
