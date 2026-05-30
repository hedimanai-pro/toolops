"""
Name: file.py

Description: File-system based cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from .base import CacheBackend, CacheEntry, TaggedCacheMixin, _normalise_tags, _now


class FileCache(CacheBackend, TaggedCacheMixin):
    """File-system based cache backend."""

    def __init__(self, directory: str = ".toolops_cache") -> None:
        """
        Initialize file cache.

        Args:
            directory: Path to store cache files.
        """
        self._dir = Path(directory)
        self._dir.mkdir(parents=True, exist_ok=True)
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._closed = False

    def _check_closed(self) -> None:
        """Check if backend is closed."""
        if self._closed:
            raise RuntimeError("FileCache is closed.")

    async def connect(self) -> None:
        """Connect to file cache (noop)."""
        self._closed = False

    async def close(self) -> None:
        """Close file cache."""
        self._closed = True

    def _path(self, key: str) -> Path:
        """
        Get file path for key.

        Args:
            key: Cache key.

        Returns:
            Path object.
        """
        safe = hashlib.md5(key.encode("utf-8")).hexdigest()
        return self._dir / f"{safe}.json"

    def _load_entry(self, key: str) -> CacheEntry | None:
        """
        Load entry from file.

        Args:
            key: Cache key.

        Returns:
            Entry or None.
        """
        self._check_closed()
        path = self._path(key)
        if not path.exists():
            return None

        try:
            with path.open(encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            return None

        entry = CacheEntry.from_payload(key, payload)
        if entry.is_expired():
            path.unlink(missing_ok=True)
            return None
        return entry

    async def get(self, key: str) -> Any | None:
        """
        Get value from file.

        Args:
            key: Cache key.

        Returns:
            Value or None.
        """
        entry = self._load_entry(key)
        if entry and entry.is_fresh():
            self._hits += 1
            return entry.value

        self._misses += 1
        return None

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get entry from file.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        entry = self._load_entry(key)
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
        Store value in file.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        self._check_closed()
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
        with self._path(key).open("w", encoding="utf-8") as f:
            json.dump(entry.payload(), f, default=str)
        self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key file.

        Args:
            key: Cache key.
        """
        self._check_closed()
        self._path(key).unlink(missing_ok=True)

    async def clear(self) -> None:
        """Delete all cache files."""
        self._check_closed()
        for f in self._dir.glob("*.json"):
            f.unlink(missing_ok=True)

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate files by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        self._check_closed()
        wanted = _normalise_tags(tags)
        count = 0
        for file in self._dir.glob("*.json"):
            try:
                with file.open(encoding="utf-8") as f:
                    payload = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue
            entry = CacheEntry.from_payload(str(payload.get("key", file.stem)), payload)
            if entry.is_expired():
                file.unlink(missing_ok=True)
                continue

            if self._matching_tags(entry.tags, wanted):
                file.unlink(missing_ok=True)
                count += 1

        return count

    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect file entry.

        Args:
            key: Cache key.

        Returns:
            Metadata dict.
        """
        entry = self._load_entry(key)
        if not entry:
            return None
        return entry.inspect()

    async def stats(self) -> dict[str, Any]:
        """
        Get file cache stats.

        Returns:
            Stats dictionary.
        """
        self._check_closed()
        total = self._hits + self._misses
        fresh_entries = 0
        stale_entries = 0
        now = _now()

        for file in self._dir.glob("*.json"):
            try:
                with file.open(encoding="utf-8") as f:
                    payload = json.load(f)
            except (json.JSONDecodeError, OSError):
                continue

            entry = CacheEntry.from_payload(str(payload.get("key", file.stem)), payload)
            if entry.is_expired(now):
                file.unlink(missing_ok=True)
                continue

            if entry.is_fresh(now):
                fresh_entries += 1
            elif entry.is_stale(now):
                stale_entries += 1

        return {
            "backend": "file",
            "directory": str(self._dir),
            "files": fresh_entries + stale_entries,
            "fresh_entries": fresh_entries,
            "stale_entries": stale_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }
