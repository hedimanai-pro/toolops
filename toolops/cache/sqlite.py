"""
Name: sqlite.py

Description: SQLite persistent cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

from .base import CacheBackend, CacheEntry, TaggedCacheMixin, _normalise_tags, _now


class SQLiteCache(CacheBackend, TaggedCacheMixin):
    """SQLite persistent cache backend with async thread safety."""

    def __init__(self, database: str = "toolops_cache.db") -> None:
        """
        Initialize SQLite backend.

        Args:
            database: Path to SQLite database file.
        """
        self._database = database
        self._conn: Any = None
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._lock = asyncio.Lock()
        self._closed = False

    async def connect(self) -> None:
        """Establish database connection and initialize schemas."""
        if self._conn is not None:
            return
        self._closed = False
        try:
            import aiosqlite
        except ImportError as exc:
            raise ImportError(
                "SQLiteCache requires aiosqlite. "
                "Install it with: pip install toolops"
            ) from exc

        self._conn = await aiosqlite.connect(self._database)
        self._conn.row_factory = aiosqlite.Row

        async with self._lock:
            await self._conn.execute("PRAGMA journal_mode=WAL;")
            await self._conn.execute("PRAGMA foreign_keys=ON;")
            await self._conn.execute("""
                CREATE TABLE IF NOT EXISTS toolops_cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expires_at REAL NOT NULL,
                    created_at REAL NOT NULL
                )
                """)
            await self._conn.execute("""
                CREATE TABLE IF NOT EXISTS toolops_cache_tags (
                    cache_key TEXT,
                    tag TEXT,
                    PRIMARY KEY (cache_key, tag),
                    FOREIGN KEY (cache_key) REFERENCES toolops_cache (key) ON DELETE CASCADE
                )
                """)
            await self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_toolops_expires ON toolops_cache (expires_at);"
            )
            await self._conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_toolops_tags_tag ON toolops_cache_tags (tag);"
            )
            await self._conn.commit()

    def _check_closed(self) -> None:
        """Check if backend is closed."""
        if self._closed:
            raise RuntimeError("SQLiteCache is closed.")

    async def _ensure_conn(self) -> Any:
        """Ensure connection is established."""
        self._check_closed()
        if self._conn is None:
            async with self._lock:
                if self._conn is None:
                    await self.connect()
        return self._conn

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get full entry from SQLite.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        conn = await self._ensure_conn()
        now_ts = _now()
        query = "SELECT value, expires_at FROM toolops_cache WHERE key = ?"
        async with conn.execute(query, (key,)) as cursor:
            row = await cursor.fetchone()

        if not row:
            return None

        expires_at = float(row["expires_at"])
        try:
            payload = json.loads(row["value"])
        except (json.JSONDecodeError, TypeError):
            return None

        entry = CacheEntry.from_payload(key, payload, fallback_expiry=expires_at)

        if entry.is_expired(now_ts):
            await self.delete(key)
            return None

        if entry.is_fresh(now_ts):
            return entry

        if allow_stale and entry.is_stale(now_ts):
            return entry

        return None

    async def get(self, key: str) -> Any | None:
        """
        Get value from SQLite.

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
        Store value in SQLite.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        conn = await self._ensure_conn()
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
        async with self._lock:
            await conn.execute(
                """
                INSERT INTO toolops_cache (key, value, expires_at, created_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT (key) DO UPDATE SET
                    value = EXCLUDED.value,
                    expires_at = EXCLUDED.expires_at,
                    created_at = EXCLUDED.created_at
                """,
                (
                    key,
                    json.dumps(entry.payload(), default=str),
                    entry.stale_until,
                    entry.created_at,
                ),
            )
            await conn.execute(
                "DELETE FROM toolops_cache_tags WHERE cache_key = ?", (key,)
            )
            if entry.tags:
                await conn.executemany(
                    "INSERT INTO toolops_cache_tags (cache_key, tag) VALUES (?, ?)",
                    [(key, tag) for tag in entry.tags],
                )
            await conn.commit()
        self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key from SQLite.

        Args:
            key: Cache key.
        """
        conn = await self._ensure_conn()
        async with self._lock:
            await conn.execute("DELETE FROM toolops_cache WHERE key = ?", (key,))
            await conn.commit()

    async def clear(self) -> None:
        """Clear SQLite cache tables."""
        conn = await self._ensure_conn()
        async with self._lock:
            await conn.execute("DELETE FROM toolops_cache")
            await conn.commit()

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate SQLite entries by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        conn = await self._ensure_conn()
        wanted = _normalise_tags(tags)
        if not wanted:
            return 0

        async with self._lock:
            placeholders = ",".join("?" for _ in wanted)
            query = f"""
                DELETE FROM toolops_cache
                WHERE key IN (
                    SELECT cache_key FROM toolops_cache_tags WHERE tag IN ({placeholders})
                )
            """
            cursor = await conn.execute(query, tuple(wanted))
            count = cursor.rowcount
            await conn.commit()
        return int(count) if count is not None else 0

    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect SQLite entry.

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
        Get SQLite cache stats.

        Returns:
            Stats dictionary.
        """
        conn = await self._ensure_conn()
        now_ts = _now()
        async with conn.execute(
            "SELECT COUNT(*) as count FROM toolops_cache WHERE expires_at > ?",
            (now_ts,),
        ) as cursor:
            row = await cursor.fetchone()
            active_entries = row["count"] if row else 0

        total = self._hits + self._misses
        return {
            "backend": "sqlite",
            "database": self._database,
            "active_entries": active_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }

    async def close(self) -> None:
        """Close database connection."""
        self._closed = True
        if self._conn:
            await self._conn.close()
            self._conn = None
