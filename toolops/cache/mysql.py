"""
Name: mysql.py

Description: MySQL and MariaDB persistent cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import asyncio
import contextlib
import json
import urllib.parse
from typing import Any

from .base import CacheBackend, CacheEntry, TaggedCacheMixin, _normalise_tags, _now


def parse_mysql_dsn(dsn: str) -> dict[str, Any]:
    """
    Parse a MySQL DSN connection string (e.g. mysql://user:pass@host:port/dbname).

    Args:
        dsn: Connection string.

    Returns:
        Connection parameters dictionary.
    """
    parsed = urllib.parse.urlparse(dsn)
    kwargs: dict[str, Any] = {
        "host": parsed.hostname or "localhost",
        "port": parsed.port or 3306,
        "user": parsed.username or "root",
        "password": parsed.password or "",
    }
    if parsed.path:
        kwargs["db"] = parsed.path.lstrip("/")
    return kwargs


class MySQLCache(CacheBackend, TaggedCacheMixin):
    """MySQL and MariaDB persistent cache backend using aiomysql pool."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 3306,
        user: str = "root",
        password: str = "",
        db: str | None = None,
        dsn: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize MySQL/MariaDB backend.

        Args:
            host: Database host.
            port: Database port.
            user: Database user.
            password: User password.
            db: Database name.
            dsn: Optional URI connection string (mysql://...).
            kwargs: Connection pool configurations.
        """
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._db = db
        self._dsn = dsn
        self._kwargs = kwargs
        self._pool: Any = None
        self._DictCursor: Any = None  # set to aiomysql.DictCursor after connect()
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._lock = asyncio.Lock()
        self._closed = False

    async def connect(self) -> None:
        """Establish database connection pool and initialize schemas."""
        if self._pool is not None:
            return
        self._closed = False
        try:
            import aiomysql

            self._DictCursor = aiomysql.DictCursor
        except ImportError as exc:
            raise ImportError(
                "MySQLCache requires aiomysql. " "Install it with: pip install toolops"
            ) from exc

        params: dict[str, Any] = {}
        if self._dsn:
            params.update(parse_mysql_dsn(self._dsn))
        else:
            params.update(
                {
                    "host": self._host,
                    "port": self._port,
                    "user": self._user,
                    "password": self._password,
                    "db": self._db,
                }
            )
        params.update(self._kwargs)
        # Ensure autocommit is enabled to match transaction handling
        params.setdefault("autocommit", True)

        self._pool = await aiomysql.create_pool(**params)

        async with self._pool.acquire() as conn, await conn.cursor() as cur:
            await cur.execute("""
                    CREATE TABLE IF NOT EXISTS toolops_cache (
                        `key` VARCHAR(255) PRIMARY KEY,
                        `value` LONGTEXT NOT NULL,
                        `expires_at` TIMESTAMP NOT NULL,
                        `created_at` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    )
                    """)
            await cur.execute("""
                    CREATE TABLE IF NOT EXISTS toolops_cache_tags (
                        `cache_key` VARCHAR(255),
                        `tag` VARCHAR(255),
                        PRIMARY KEY (`cache_key`, `tag`),
                        FOREIGN KEY (`cache_key`) REFERENCES toolops_cache (`key`) ON DELETE CASCADE
                    )
                    """)
            # Fail-safe index creation
            with contextlib.suppress(Exception):
                await cur.execute(
                    "CREATE INDEX idx_toolops_expires ON toolops_cache (expires_at)"
                )
            with contextlib.suppress(Exception):
                await cur.execute(
                    "CREATE INDEX idx_toolops_tags_tag ON toolops_cache_tags (tag)"
                )

    async def _ensure_pool(self) -> Any:
        """Ensure pool is established and return pool."""
        if self._closed:
            raise RuntimeError("MySQLCache is closed.")
        if self._pool is None:
            async with self._lock:
                if self._pool is None:
                    await self.connect()
        return self._pool

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get full entry from MySQL.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        pool = await self._ensure_pool()
        now_ts = _now()
        query = "SELECT `value`, UNIX_TIMESTAMP(`expires_at`) as expires_at_ts FROM toolops_cache WHERE `key` = %s"

        async with pool.acquire() as conn, await conn.cursor(self._DictCursor) as cur:
            await cur.execute(query, (key,))
            row = await cur.fetchone()

        if not row:
            return None

        expires_at = float(row["expires_at_ts"])
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
        Get value from MySQL.

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
        Store value in MySQL.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        pool = await self._ensure_pool()
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)

        upsert_query = """
            INSERT INTO toolops_cache (`key`, `value`, `expires_at`, `created_at`)
            VALUES (%s, %s, FROM_UNIXTIME(%s), FROM_UNIXTIME(%s))
            ON DUPLICATE KEY UPDATE
                `value` = VALUES(`value`),
                `expires_at` = VALUES(`expires_at`),
                `created_at` = VALUES(`created_at`)
        """

        async with pool.acquire() as conn, await conn.cursor() as cur:
            await conn.begin()
            try:
                await cur.execute(
                    upsert_query,
                    (
                        key,
                        json.dumps(entry.payload(), default=str),
                        entry.stale_until,
                        entry.created_at,
                    ),
                )
                await cur.execute(
                    "DELETE FROM toolops_cache_tags WHERE `cache_key` = %s", (key,)
                )
                if entry.tags:
                    await cur.executemany(
                        "INSERT INTO toolops_cache_tags (`cache_key`, `tag`) VALUES (%s, %s)",
                        [(key, tag) for tag in entry.tags],
                    )
                await conn.commit()
            except Exception:
                await conn.rollback()
                raise
        self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key from MySQL.

        Args:
            key: Cache key.
        """
        pool = await self._ensure_pool()
        async with pool.acquire() as conn, await conn.cursor() as cur:
            await cur.execute("DELETE FROM toolops_cache WHERE `key` = %s", (key,))

    async def clear(self) -> None:
        """Clear MySQL cache tables."""
        pool = await self._ensure_pool()
        async with pool.acquire() as conn, await conn.cursor() as cur:
            await cur.execute("DELETE FROM toolops_cache")

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate MySQL entries by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        pool = await self._ensure_pool()
        wanted = _normalise_tags(tags)
        if not wanted:
            return 0

        placeholders = ",".join("%s" for _ in wanted)
        query = f"""
            DELETE FROM toolops_cache
            WHERE `key` IN (
                SELECT `cache_key` FROM toolops_cache_tags WHERE `tag` IN ({placeholders})
            )
        """
        async with pool.acquire() as conn, await conn.cursor() as cur:
            await cur.execute(query, tuple(wanted))
            count = int(cur.rowcount)
        return count

    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect MySQL entry.

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
        Get MySQL cache stats.

        Returns:
            Stats dictionary.
        """
        pool = await self._ensure_pool()
        query = "SELECT COUNT(*) as count FROM toolops_cache WHERE `expires_at` > NOW()"
        async with pool.acquire() as conn, await conn.cursor(self._DictCursor) as cur:
            await cur.execute(query)
            row = await cur.fetchone()
            active_entries = row["count"] if row else 0

        total = self._hits + self._misses
        return {
            "backend": "mysql",
            "active_entries": active_entries,
            "pool_size": pool.size,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }

    async def close(self) -> None:
        """Close database connection pool."""
        self._closed = True
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()
            self._pool = None
