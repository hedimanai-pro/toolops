"""
Name: memory.py

Description: In-memory cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
from typing import Any

from .base import CacheBackend, CacheEntry, TaggedCacheMixin, _normalise_tags, _now


class MemoryCache(CacheBackend, TaggedCacheMixin):
    """In-memory cache implementation with async thread-safety."""

    def __init__(self) -> None:
        """Initialize memory store, indices, and async lock."""
        self._store: dict[str, CacheEntry] = {}
        self._tag_index: dict[str, set[str]] = {}
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._lock = asyncio.Lock()
        self._closed = False

    def _check_closed(self) -> None:
        """Check if backend is closed."""
        if self._closed:
            raise RuntimeError("MemoryCache is closed.")

    async def connect(self) -> None:
        """Connect to the memory store (noop)."""
        self._closed = False

    async def close(self) -> None:
        """Close the memory store."""
        self._closed = True

    def _purge_if_expired(self, key: str) -> CacheEntry | None:
        """
        Remove entry if expired.

        Args:
            key: Cache key.

        Returns:
            Entry if still valid.
        """
        entry = self._store.get(key)
        if entry and entry.is_expired():
            self._unindex(entry)
            del self._store[key]
            return None
        return entry

    def _index(self, entry: CacheEntry) -> None:
        """
        Add entry to tag index.

        Args:
            entry: Cache entry.
        """
        for tag in entry.tags:
            self._tag_index.setdefault(tag, set()).add(entry.key)

    def _unindex(self, entry: CacheEntry) -> None:
        """
        Remove entry from tag index.

        Args:
            entry: Cache entry.
        """
        for tag in entry.tags:
            keys = self._tag_index.get(tag)
            if not keys:
                continue
            keys.discard(entry.key)
            if not keys:
                del self._tag_index[tag]

    async def get(self, key: str) -> Any | None:
        """
        Get value from memory.

        Thread-safe: protected by asyncio.Lock.

        Args:
            key: Cache key.

        Returns:
            Value or None.
        """
        self._check_closed()
        async with self._lock:
            entry = self._purge_if_expired(key)
            if entry and entry.is_fresh():
                self._hits += 1
                return entry.value

            self._misses += 1
            return None

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get entry from memory.

        Thread-safe: protected by asyncio.Lock.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        self._check_closed()
        async with self._lock:
            entry = self._purge_if_expired(key)
            if not entry:
                return None

            if entry.is_fresh():
                return entry

            if allow_stale and entry.is_stale():
                return entry

            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int,
        *,
        tags: list[str] | None = None,
        stale_ttl: int | None = None,
    ) -> None:
        """
        Store value in memory.

        Thread-safe: protected by asyncio.Lock.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        self._check_closed()
        async with self._lock:
            existing = self._store.get(key)
            if existing:
                self._unindex(existing)

            entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
            self._store[key] = entry
            self._index(entry)
            self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key from memory.

        Thread-safe: protected by asyncio.Lock.

        Args:
            key: Cache key.
        """
        self._check_closed()
        async with self._lock:
            entry = self._store.pop(key, None)
            if entry:
                self._unindex(entry)

    async def clear(self) -> None:
        """Clear all memory entries."""
        self._check_closed()
        async with self._lock:
            self._store.clear()
            self._tag_index.clear()

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate memory by tags.

        Thread-safe: protected by asyncio.Lock.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        self._check_closed()
        async with self._lock:
            wanted = _normalise_tags(tags)
            keys: set[str] = set()
            for tag in wanted:
                keys.update(self._tag_index.get(tag, set()))

            count = 0
            for key in keys:
                if key in self._store:
                    entry = self._store.pop(key, None)
                    if entry:
                        self._unindex(entry)
                    count += 1

            return count

    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect memory entry.

        Args:
            key: Cache key.

        Returns:
            Metadata dict.
        """
        self._check_closed()
        entry = self._purge_if_expired(key)
        if not entry:
            return None
        return entry.inspect()

    async def stats(self) -> dict[str, Any]:
        """
        Get memory cache stats.

        Returns:
            Stats dictionary.
        """
        self._check_closed()
        now = _now()
        fresh_entries = sum(1 for entry in self._store.values() if entry.is_fresh(now))
        stale_entries = sum(1 for entry in self._store.values() if entry.is_stale(now))
        total = self._hits + self._misses
        return {
            "backend": "memory",
            "size": len(self._store),
            "fresh_entries": fresh_entries,
            "stale_entries": stale_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }
