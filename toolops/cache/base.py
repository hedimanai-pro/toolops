"""
Name: base.py

Description: Base abstractions, interfaces, and utilities for ToolOps cache backends.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import time
from abc import ABC, abstractmethod
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _now() -> float:
    """
    Get current UTC timestamp.

    Returns:
        Current time as float.
    """
    return time.time()


def _utc_iso(ts: float) -> str:
    """
    Convert timestamp to UTC ISO string.

    Args:
        ts: Unix timestamp.

    Returns:
        ISO formatted string.
    """
    return datetime.fromtimestamp(ts, tz=timezone.utc).isoformat()


def _normalise_tags(tags: Iterable[str] | None) -> list[str]:
    """
    Normalise and deduplicate cache tags.

    Args:
        tags: Iterable of tag strings.

    Returns:
        Sorted list of unique tags.
    """
    if not tags:
        return []
    return sorted({str(tag) for tag in tags if str(tag).strip()})


@dataclass
class CacheEntry:
    """Representation of a single cache entry."""

    key: str
    value: Any
    fresh_until: float
    stale_until: float
    created_at: float
    tags: list[str] = field(default_factory=list)

    def is_fresh(self, now: float | None = None) -> bool:
        """
        Check if entry is still fresh.

        Args:
            now: Optional current timestamp.

        Returns:
            True if fresh.
        """
        return (now or _now()) <= self.fresh_until

    def is_stale(self, now: float | None = None) -> bool:
        """
        Check if entry is in stale window.

        Args:
            now: Optional current timestamp.

        Returns:
            True if stale.
        """
        current = now or _now()
        return self.fresh_until < current <= self.stale_until

    def is_expired(self, now: float | None = None) -> bool:
        """
        Check if entry has fully expired.

        Args:
            now: Optional current timestamp.

        Returns:
            True if expired.
        """
        return (now or _now()) > self.stale_until

    def payload(self) -> dict[str, Any]:
        """
        Get serializable payload for the entry.

        Returns:
            Dictionary payload.
        """
        return {
            "key": self.key,
            "value": self.value,
            "fresh_until": self.fresh_until,
            "stale_until": self.stale_until,
            "created_at": self.created_at,
            "tags": list(self.tags),
        }

    def inspect(self, *, now: float | None = None) -> dict[str, Any]:
        """
        Get inspection data for the entry.

        Args:
            now: Optional current timestamp.

        Returns:
            Inspection metadata dictionary.
        """
        current = now or _now()
        state = "fresh"
        if self.is_stale(current):
            state = "stale"
        elif self.is_expired(current):
            state = "expired"

        return {
            "key": self.key,
            "value": self.value,
            "tags": list(self.tags),
            "state": state,
            "fresh_until": _utc_iso(self.fresh_until),
            "stale_until": _utc_iso(self.stale_until),
            "created_at": _utc_iso(self.created_at),
        }

    @classmethod
    def create(
        cls,
        key: str,
        value: Any,
        ttl: int,
        *,
        tags: Iterable[str] | None = None,
        stale_ttl: int | None = None,
    ) -> CacheEntry:
        """
        Create a new cache entry.

        Args:
            key: Cache key.
            value: Value to cache.
            ttl: Time to live in seconds.
            tags: Optional tags.
            stale_ttl: Optional stale window TTL.

        Returns:
            New CacheEntry instance.
        """
        created_at = _now()
        fresh_until = created_at + ttl
        stale_window = stale_ttl if stale_ttl is not None else ttl
        stale_until = created_at + max(ttl, stale_window)

        return cls(
            key=key,
            value=value,
            fresh_until=fresh_until,
            stale_until=stale_until,
            created_at=created_at,
            tags=_normalise_tags(tags),
        )

    @classmethod
    def from_payload(
        cls, key: str, payload: Any, *, fallback_expiry: float | None = None
    ) -> CacheEntry:
        """
        Reconstruct entry from a payload.

        Args:
            key: Default cache key.
            payload: Payload data.
            fallback_expiry: Fallback expiration timestamp.

        Returns:
            Reconstructed CacheEntry.
        """
        if isinstance(payload, dict):
            if {"value", "fresh_until", "stale_until", "created_at"} <= payload.keys():
                resolved_key = str(payload.get("key", key))
                return cls(
                    key=resolved_key,
                    value=payload["value"],
                    fresh_until=float(payload["fresh_until"]),
                    stale_until=float(payload["stale_until"]),
                    created_at=float(payload["created_at"]),
                    tags=_normalise_tags(payload.get("tags")),
                )

            if {"value", "expires_at"} <= payload.keys():
                expires_at = float(payload["expires_at"])
                resolved_key = str(payload.get("key", key))
                return cls(
                    key=resolved_key,
                    value=payload["value"],
                    fresh_until=expires_at,
                    stale_until=expires_at,
                    created_at=expires_at,
                    tags=[],
                )

        expires_at = fallback_expiry if fallback_expiry is not None else _now()
        return cls(
            key=key,
            value=payload,
            fresh_until=expires_at,
            stale_until=expires_at,
            created_at=expires_at,
            tags=[],
        )


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """
    Calculate cosine similarity between vectors.

    Args:
        a: First vector.
        b: Second vector.

    Returns:
        Similarity score in [0, 1].
    """
    try:
        import numpy as np

        va, vb = np.array(a, dtype=float), np.array(b, dtype=float)
        denom = float(np.linalg.norm(va) * np.linalg.norm(vb))
        return float(np.dot(va, vb) / denom) if denom else 0.0

    except ImportError:
        dot = sum(x * y for x, y in zip(a, b))
        na = sum(x**2 for x in a) ** 0.5
        nb = sum(x**2 for x in b) ** 0.5
        return dot / (na * nb) if (na and nb) else 0.0


class TaggedCacheMixin:
    """Mixin for tag-based cache invalidation."""

    def _matching_tags(self, entry_tags: Iterable[str], tags: Iterable[str]) -> bool:
        """
        Check if tags intersect.

        Args:
            entry_tags: Tags on the entry.
            tags: Tags to match against.

        Returns:
            True if any tag matches.
        """
        return bool(set(entry_tags) & set(tags))


class CacheBackend(ABC):
    """Abstract base class for cache backends."""

    async def connect(self) -> None:
        """Establish connections to the backend store."""
        return None

    async def close(self) -> None:
        """Close connections to the backend store."""
        return None

    @abstractmethod
    async def get(self, key: str) -> Any | None:
        """
        Get value from cache.

        Args:
            key: Cache key.

        Returns:
            Value or None.
        """

    @abstractmethod
    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get full entry from cache.

        Args:
            key: Cache key.
            allow_stale: Whether to return stale entries.

        Returns:
            CacheEntry or None.
        """

    @abstractmethod
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
        Store value in cache.

        Args:
            key: Cache key.
            value: Value to store.
            ttl: Time to live.
            tags: Optional tags.
            stale_ttl: Optional stale window.
        """

    @abstractmethod
    async def delete(self, key: str) -> None:
        """
        Delete key from cache.

        Args:
            key: Cache key.
        """

    @abstractmethod
    async def clear(self) -> None:
        """Clear entire cache content."""

    @abstractmethod
    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate entries by tags.

        Args:
            tags: Tags to invalidate.

        Returns:
            Number of entries removed.
        """

    @abstractmethod
    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect cache key metadata.

        Args:
            key: Cache key.

        Returns:
            Metadata dictionary.
        """

    @abstractmethod
    async def stats(self) -> dict[str, Any]:
        """
        Get backend statistics.

        Returns:
            Stats dictionary.
        """
