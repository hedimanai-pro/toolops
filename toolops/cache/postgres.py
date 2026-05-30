"""
Name: postgres.py

Description: PostgreSQL persistent cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import contextlib
import json
from typing import Any

from .base import CacheBackend, CacheEntry, TaggedCacheMixin, _normalise_tags

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
        self._closed = False

    def _check_closed(self) -> None:
        """Check if backend is closed and raise error."""
        if self._closed:
            raise RuntimeError("PostgresCache is closed.")
        if self._pool is None:
            raise RuntimeError("PostgresCache is not connected. Call connect() first.")

    async def connect(self) -> None:
        """Establish database connection pool."""
        if self._pool is not None:
            return
        self._closed = False
        try:
            import asyncpg

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
                "PostgresCache requires asyncpg. "
                "Install it with: pip install toolops"
            ) from exc

    async def _fetch_entry(
        self, key: str, *, include_expired: bool = False
    ) -> CacheEntry | None:
        """
        Fetch entry from database.

        Args:
            key: Cache key.
            include_expired: Allow expired results.

        Returns:
            Entry or None.
        """
        self._check_closed()
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

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
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
        Store value in Postgres.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        self._check_closed()
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
        self._check_closed()
        async with self._pool.acquire() as conn:
            await conn.execute("DELETE FROM toolops_cache WHERE key = $1", key)

    async def clear(self) -> None:
        """Clear Postgres cache table."""
        self._check_closed()
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
        self._check_closed()
        wanted = _normalise_tags(tags)
        if not wanted:
            return 0

        async with self._pool.acquire() as conn:
            total = 0
            for tag in wanted:
                result = await conn.execute(
                    "DELETE FROM toolops_cache WHERE tags @> $1::jsonb AND expires_at > NOW()",
                    [tag],
                )
                with contextlib.suppress(IndexError, ValueError):
                    total += int(result.split()[1]) if len(result.split()) > 1 else 0

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
        self._check_closed()
        total = self._hits + self._misses
        async with self._pool.acquire() as conn:
            active_entries = await conn.fetchval(
                "SELECT COUNT(*) FROM toolops_cache WHERE expires_at > NOW()"
            )
        return {
            "backend": "postgres",
            "active_entries": active_entries,
            "pool_size": self._pool.get_size() if self._pool else 0,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }

    async def close(self) -> None:
        """Close database connection pool."""
        self._closed = True
        if self._pool:
            await self._pool.close()
            self._pool = None
