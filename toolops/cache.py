"""
Name: cache.py

Description: Cache backends and manager for ToolOps SDK.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import json
import time
import asyncio
import hashlib
from pathlib import Path
from typing import Any, Iterable
from abc import ABC, abstractmethod
from collections import deque
from datetime import datetime, timezone
from dataclasses import dataclass, field

from toolops.logger import logger
from toolops.observability import metrics


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


@dataclass(slots=True)
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
    def create(cls, key: str, value: Any, ttl: int, *, tags: Iterable[str] | None = None, stale_ttl: int | None = None) -> "CacheEntry":
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
    def from_payload(cls, key: str, payload: Any, *, fallback_expiry: float | None = None) -> "CacheEntry":
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
        import numpy as np  # type: ignore[import]

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
    async def get_entry(self, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
        """
        Get full entry from cache.

        Args:
            key: Cache key.
            allow_stale: Whether to return stale entries.

        Returns:
            CacheEntry or None.
        """


    @abstractmethod
    async def set(self, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
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

        async with self._lock:
            entry = self._purge_if_expired(key)
            if entry and entry.is_fresh():
                self._hits += 1
                return entry.value

            self._misses += 1
            return None


    async def get_entry(self, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
        """
        Get entry from memory.

        Thread-safe: protected by asyncio.Lock.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """

        async with self._lock:
            entry = self._purge_if_expired(key)
            if not entry:
                return None

            if entry.is_fresh():
                return entry

            if allow_stale and entry.is_stale():
                return entry

            return None


    async def set(self, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
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

        async with self._lock:
            entry = self._store.pop(key, None)
            if entry:
                self._unindex(entry)


    async def clear(self) -> None:
        """Clear all memory entries."""

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


_PG_INIT = """
CREATE TABLE IF NOT EXISTS toolops_cache (
    key        TEXT PRIMARY KEY,
    value      JSONB       NOT NULL,
    expires_at TIMESTAMPTZ NOT NULL,
    tags       JSONB       NOT NULL DEFAULT '[]'::jsonb
);
CREATE INDEX IF NOT EXISTS idx_toolops_expires
    ON toolops_cache (expires_at);
CREATE INDEX IF NOT EXISTS idx_toolops_tags
    ON toolops_cache USING GIN (tags);
"""


class PostgresCache(CacheBackend, TaggedCacheMixin):
    """PostgreSQL persistent cache backend."""


    def __init__(self, dsn: str) -> None:
        """
        Initialize Postgres backend.

        Args:
            dsn: Database connection string.
        """

        self._dsn = dsn
        self._pool: Any = None
        self._hits = 0
        self._misses = 0
        self._sets = 0


    async def connect(self) -> None:
        """Establish database connection pool."""

        try:
            import asyncpg  # type: ignore[import]

            async def _init_conn(conn: Any) -> None:
                await conn.set_type_codec(
                    "jsonb",
                    encoder=json.dumps,
                    decoder=json.loads,
                    schema="pg_catalog",
                )

            self._pool = await asyncpg.create_pool(self._dsn, init=_init_conn)
            async with self._pool.acquire() as conn:
                await conn.execute(_PG_INIT)

        except ImportError as exc:
            raise ImportError(
                'PostgresCache requires asyncpg. '
                'Install it with: pip install "toolops[postgres]"'
            ) from exc


    async def _fetch_entry(self, key: str, *, include_expired: bool = False) -> CacheEntry | None:
        """
        Fetch entry from database.

        Args:
            key: Cache key.
            include_expired: Allow expired results.

        Returns:
            Entry or None.
        """

        query = "SELECT value, expires_at FROM toolops_cache WHERE key = $1"
        if not include_expired:
            query += " AND expires_at > NOW()"

        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(query, key)

        if not row:
            return None

        expires_at = row["expires_at"].timestamp()
        entry = CacheEntry.from_payload(key, row["value"], fallback_expiry=expires_at)

        if entry.is_expired():
            await self.delete(key)
            return None

        return entry


    async def get(self, key: str) -> Any | None:
        """
        Get value from Postgres.

        Args:
            key: Cache key.

        Returns:
            Value or None.
        """

        entry = await self._fetch_entry(key)
        if entry and entry.is_fresh():
            self._hits += 1
            return entry.value
        self._misses += 1
        return None


    async def get_entry(self, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
        """
        Get entry from Postgres.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """

        entry = await self._fetch_entry(key)
        if not entry:
            return None

        if entry.is_fresh():
            return entry

        if allow_stale and entry.is_stale():
            return entry

        return None


    async def set(self, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
        """
        Store value in Postgres.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """

        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
        async with self._pool.acquire() as conn:
            await conn.execute(
                """
                INSERT INTO toolops_cache (key, value, expires_at, tags)
                VALUES ($1, $2, TO_TIMESTAMP($3), $4::jsonb)
                ON CONFLICT (key) DO UPDATE
                    SET value      = EXCLUDED.value,
                        expires_at = EXCLUDED.expires_at,
                        tags       = EXCLUDED.tags
                """,
                key,
                entry.payload(),
                entry.stale_until,
                entry.tags,
            )
        self._sets += 1


    async def delete(self, key: str) -> None:
        """
        Delete key from Postgres.

        Args:
            key: Cache key.
        """

        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM toolops_cache WHERE key = $1", key)


    async def clear(self) -> None:
        """Clear Postgres cache table."""

        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM toolops_cache")


    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate Postgres entries by tags using GIN index.

        Uses the JSONB @> (contains) operator with the GIN index
        on the tags column for efficient server-side filtering.
        Avoids loading all entries into memory (pre-v0.2.0 bug).

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """

        wanted = _normalise_tags(tags)
        if not wanted:
            return 0

        async with self._pool.acquire() as conn:
            # The GIN index on tags column makes this efficient:
            # @> operator checks if JSONB array contains any of the wanted tags.
            # We build a JSONB array of wanted tags and use @> for each tag.
            total = 0
            for tag in wanted:
                result = await conn.execute(
                    "DELETE FROM toolops_cache WHERE tags @> $1::jsonb AND expires_at > NOW()",
                    [tag],
                )
                # asyncpg returns a status string like "DELETE 3"
                try:
                    total += int(result.split()[1]) if len(result.split()) > 1 else 0
                except (IndexError, ValueError):
                    pass

        return total


    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect Postgres entry.

        Args:
            key: Cache key.

        Returns:
            Metadata dict.
        """

        entry = await self._fetch_entry(key, include_expired=True)
        if not entry:
            return None
        return entry.inspect()


    async def stats(self) -> dict[str, Any]:
        """
        Get Postgres cache stats.

        Returns:
            Stats dictionary.
        """

        total = self._hits + self._misses
        async with self._pool.acquire() as conn:
            active_entries = await conn.fetchval("SELECT COUNT(*) FROM toolops_cache WHERE expires_at > NOW()")
        return {
            "backend": "postgres",
            "active_entries": active_entries,
            "pool_size": self._pool.get_size(),
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }


    async def close(self) -> None:
        """Close database connection pool."""

        if self._pool:
            await self._pool.close()


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

        path = self._path(key)
        if not path.exists():
            return None

        with path.open(encoding="utf-8") as f:
            payload = json.load(f)

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


    async def get_entry(self, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
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


    async def set(self, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
        """
        Store value in file.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """

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

        self._path(key).unlink(missing_ok=True)


    async def clear(self) -> None:
        """Delete all cache files."""

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

        wanted = _normalise_tags(tags)
        count = 0
        for file in self._dir.glob("*.json"):
            with file.open(encoding="utf-8") as f:
                payload = json.load(f)
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

        total = self._hits + self._misses
        fresh_entries = 0
        stale_entries = 0
        now = _now()

        for file in self._dir.glob("*.json"):
            with file.open(encoding="utf-8") as f:
                payload = json.load(f)

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


class SentenceTransformerEmbedder:
    """Local embedder using sentence-transformers."""


    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedder.

        Args:
            model: Model name.
        """

        try:
            from sentence_transformers import SentenceTransformer  # type: ignore[import]

            self._model = SentenceTransformer(model)
        except ImportError as exc:
            raise ImportError(
                'SentenceTransformerEmbedder requires sentence-transformers. '
                'Install it with: pip install "toolops[semantic]"'
            ) from exc


    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text.

        Returns:
            Vector embedding.
        """

        return self._model.encode(text, convert_to_numpy=True).tolist()


class OpenAIEmbedder:
    """Cloud embedder using OpenAI API."""


    def __init__(self, api_key: str | None = None, model: str = "text-embedding-3-small") -> None:
        """
        Initialize OpenAI embedder.

        Args:
            api_key: Optional API key.
            model: OpenAI model name.
        """

        try:
            from openai import AsyncOpenAI  # type: ignore[import]

            self._client = AsyncOpenAI(api_key=api_key)
            self._model = model

        except ImportError as exc:
            raise ImportError(
                'OpenAIEmbedder requires openai. '
                'Install it with: pip install "toolops[openai]"'
            ) from exc


    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding via OpenAI.

        Args:
            text: Input text.

        Returns:
            Vector embedding.
        """

        response = await self._client.embeddings.create(input=text, model=self._model)
        return response.data[0].embedding


class SemanticCache(CacheBackend, TaggedCacheMixin):
    """Similarity-based semantic cache with O(1) LRU eviction."""


    def __init__(self, embedder: Any, threshold: float = 0.92, max_entries: int = 1_000) -> None:
        """
        Initialize semantic cache.

        Args:
            embedder: Embedder instance.
            threshold: Similarity threshold.
            max_entries: Max in-memory entries.
        """

        self._embedder = embedder
        self._threshold = threshold
        self._max_entries = max_entries
        # deque with maxlen provides O(1) append and automatic eviction
        # of the oldest entry when capacity is reached (fixes v0.1.x O(n) pop(0))
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)
        self._hits = 0
        self._misses = 0
        self._semantic_hits = 0
        self._sets = 0


    def _extract_query(self, key: str) -> str:
        """
        Extract query text from key.

        Args:
            key: Cache key.

        Returns:
            Extracted text.
        """

        try:
            payload = key.split(":", 1)[1]
            pairs = json.loads(payload)
            if pairs and isinstance(pairs, list) and pairs[0]:
                return str(pairs[0][1])

        except Exception:
            pass
        return key


    def _cleanup(self) -> None:
        """Remove expired entries from memory."""

        now = _now()
        # Rebuild deque with only non-expired entries (preserves maxlen)
        self._entries = deque(
            [entry for entry in self._entries if not entry["entry"].is_expired(now)],
            maxlen=self._max_entries,
        )


    async def get(self, key: str) -> Any | None:
        """
        Get value by similarity.

        Args:
            key: Cache key.

        Returns:
            Value or None.
        """

        entry = await self.get_entry(key)
        if entry:
            self._hits += 1
            return entry.value
        self._misses += 1
        return None


    async def get_entry(self, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
        """
        Find best matching entry.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Best entry or None.
        """

        self._cleanup()
        now = _now()

        for wrapped in self._entries:
            entry: CacheEntry = wrapped["entry"]
            if entry.key != key:
                continue

            if entry.is_fresh(now):
                return entry

            if allow_stale and entry.is_stale(now):
                return entry

        query = self._extract_query(key)
        embedding = await self._embedder.embed(query)
        best_score = 0.0
        best_entry: CacheEntry | None = None

        for wrapped in self._entries:
            entry = wrapped["entry"]
            if entry.is_expired(now):
                continue

            if not allow_stale and not entry.is_fresh(now):
                continue

            score = cosine_similarity(embedding, wrapped["embedding"])
            if score > best_score:
                best_score = score
                best_entry = entry

        if best_entry and best_score >= self._threshold:
            self._semantic_hits += 1
            return best_entry

        return None


    async def set(self, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
        """
        Store value with embedding.

        Uses deque with maxlen for O(1) append and automatic LRU eviction.
        Replaces the O(n) list.pop(0) from v0.1.x.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """

        query = self._extract_query(key)
        embedding = await self._embedder.embed(query) if query else []
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
        self._cleanup()

        # Remove existing entry for this key to avoid duplicates
        self._entries = deque(
            [wrapped for wrapped in self._entries if wrapped["entry"].key != key],
            maxlen=self._max_entries,
        )

        # deque.append with maxlen: O(1) — oldest entry auto-evicted at capacity
        self._entries.append({"entry": entry, "query": query, "embedding": embedding})
        self._sets += 1


    async def delete(self, key: str) -> None:
        """
        Delete key from semantic store.

        Args:
            key: Cache key.
        """

        self._entries = deque(
            [wrapped for wrapped in self._entries if wrapped["entry"].key != key],
            maxlen=self._max_entries,
        )


    async def clear(self) -> None:
        """Clear all semantic entries."""

        self._entries.clear()


    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate semantic entries by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """

        wanted = _normalise_tags(tags)
        before = len(self._entries)
        self._entries = deque(
            [wrapped for wrapped in self._entries if not self._matching_tags(wrapped["entry"].tags, wanted)],
            maxlen=self._max_entries,
        )
        return before - len(self._entries)


    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect semantic entry.

        Args:
            key: Cache key.

        Returns:
            Metadata dict.
        """

        entry = await self.get_entry(key, allow_stale=True)
        if not entry:
            return None
        return entry.inspect()


    async def stats(self) -> dict[str, Any]:
        """
        Get semantic cache stats.

        Returns:
            Stats dictionary.
        """

        self._cleanup()
        total = self._hits + self._misses
        fresh_entries = sum(1 for wrapped in self._entries if wrapped["entry"].is_fresh())
        stale_entries = sum(1 for wrapped in self._entries if wrapped["entry"].is_stale())

        return {
            "backend": "semantic",
            "threshold": self._threshold,
            "entries": len(self._entries),
            "fresh_entries": fresh_entries,
            "stale_entries": stale_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "semantic_hits": self._semantic_hits,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }


class CacheManager:
    """Central coordinator for multiple cache backends."""


    def __init__(self) -> None:
        """Initialize backend registry."""

        self._backends: dict[str, CacheBackend] = {}
        self._default: str | None = None


    def register(self, name: str, backend: CacheBackend, is_default: bool = False) -> None:
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


    async def get_entry(self, name: str, key: str, *, allow_stale: bool = False) -> CacheEntry | None:
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


    async def set(self, name: str, key: str, value: Any, ttl: int, *, tags: list[str] | None = None, stale_ttl: int | None = None) -> None:
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


    async def invalidate(self, name: str, *, tags: list[str] | None = None, keys: list[str] | None = None) -> int:
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
            logger.info("cache_invalidated", cache=name, deleted=deleted, tags=tags or [], keys=keys or [])
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
                await backend.connect()  # type: ignore[attr-defined]


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
