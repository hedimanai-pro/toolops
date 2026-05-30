"""
Name: valkey.py

Description: Valkey and Redis persistent cache backends for ToolOps SDK.

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


class ValkeyCache(CacheBackend, TaggedCacheMixin):
    """Valkey persistent cache backend with connection pooling and pipeline support."""

    def __init__(
        self,
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str | None = None,
        url: str | None = None,
        **kwargs: Any,
    ) -> None:
        """
        Initialize Valkey backend.

        Args:
            host: Server hostname.
            port: Server port.
            db: Database index.
            password: Optional authentication password.
            url: Connection URL string (e.g. redis://...).
            kwargs: Extra arguments for the client connection pool.
        """
        self._host = host
        self._port = port
        self._db = db
        self._password = password
        self._url = url
        self._kwargs = kwargs
        self._client: Any = None
        self._hits = 0
        self._misses = 0
        self._sets = 0
        self._lock = asyncio.Lock()
        self._closed = False

    @classmethod
    def from_url(cls, url: str, **kwargs: Any) -> ValkeyCache:
        """
        Create a backend instance from a connection URL.

        Args:
            url: Connection URL.
            kwargs: Extra connection arguments.

        Returns:
            ValkeyCache instance.
        """
        return cls(url=url, **kwargs)

    async def connect(self) -> None:
        """Establish connection pool and ping server."""
        if self._client is not None:
            return
        self._closed = False
        try:
            import redis.asyncio as aioredis
        except ImportError as exc:
            backend_type = self.__class__.__name__
            raise ImportError(
                f"{backend_type} requires the redis client library. "
                "Install it with: pip install toolops"
            ) from exc

        async with self._lock:
            if self._client is not None:
                return
            if self._url:
                self._client = aioredis.from_url(
                    self._url, decode_responses=True, **self._kwargs
                )
            else:
                self._client = aioredis.Redis(
                    host=self._host,
                    port=self._port,
                    db=self._db,
                    password=self._password,
                    decode_responses=True,
                    **self._kwargs,
                )
            # Verify connectivity
            await self._client.ping()

    async def _ensure_client(self) -> Any:
        """Ensure connection is established and return client."""
        if self._closed:
            raise RuntimeError(f"{self.__class__.__name__} is closed.")
        if self._client is None:
            async with self._lock:
                if self._client is None:
                    await self.connect()
        return self._client

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Get full entry from Valkey/Redis.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Entry or None.
        """
        client = await self._ensure_client()
        now_ts = _now()
        raw = await client.get(f"toolops:cache:{key}")
        if not raw:
            return None

        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, TypeError):
            return None

        entry = CacheEntry.from_payload(key, payload)

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
        Get value from cache.

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
        Store value in Valkey/Redis.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        client = await self._ensure_client()
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)

        cache_key = f"toolops:cache:{key}"
        tags_key = f"toolops:key_tags:{key}"
        ex = int(max(1, entry.stale_until - _now()))

        async with self._lock:
            # 1. Clear existing key tags from sets
            old_tags = await client.smembers(tags_key)
            if old_tags:
                for tag in old_tags:
                    await client.srem(f"toolops:tag:{tag}", key)

            # 2. Write key payload
            await client.set(cache_key, json.dumps(entry.payload(), default=str), ex=ex)

            # 3. Add to new tag sets
            if entry.tags:
                await client.sadd(tags_key, *entry.tags)
                await client.expire(tags_key, ex)
                for tag in entry.tags:
                    await client.sadd(f"toolops:tag:{tag}", key)

        self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key from Valkey/Redis.

        Args:
            key: Cache key.
        """
        client = await self._ensure_client()
        cache_key = f"toolops:cache:{key}"
        tags_key = f"toolops:key_tags:{key}"

        async with self._lock:
            old_tags = await client.smembers(tags_key)
            if old_tags:
                for tag in old_tags:
                    await client.srem(f"toolops:tag:{tag}", key)
            await client.delete(cache_key, tags_key)

    async def clear(self) -> None:
        """Clear all toolops keys from database."""
        client = await self._ensure_client()
        cursor = 0
        async with self._lock:
            while True:
                cursor, keys = await client.scan(cursor, match="toolops:*", count=100)
                if keys:
                    await client.delete(*keys)
                if cursor == 0:
                    break

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate cache entries by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        client = await self._ensure_client()
        wanted = _normalise_tags(tags)
        if not wanted:
            return 0

        count = 0
        async with self._lock:
            for tag in wanted:
                tag_key = f"toolops:tag:{tag}"
                keys = await client.smembers(tag_key)
                if keys:
                    for key in keys:
                        cache_key = f"toolops:cache:{key}"
                        tags_key = f"toolops:key_tags:{key}"
                        other_tags = await client.smembers(tags_key)
                        if other_tags:
                            for ot in other_tags:
                                if ot != tag:
                                    await client.srem(f"toolops:tag:{ot}", key)
                        await client.delete(cache_key, tags_key)
                        count += 1
                await client.delete(tag_key)

        return count

    async def inspect(self, key: str) -> dict[str, Any] | None:
        """
        Inspect cache key metadata.

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
        Get Valkey/Redis cache statistics.

        Returns:
            Stats dictionary.
        """
        client = await self._ensure_client()
        cursor = 0
        active_entries = 0
        now_ts = _now()
        async with self._lock:
            while True:
                cursor, keys = await client.scan(
                    cursor, match="toolops:cache:*", count=100
                )
                if keys:
                    for key in keys:
                        raw = await client.get(key)
                        if raw:
                            try:
                                payload = json.loads(raw)
                                if float(payload.get("fresh_until", 0)) > now_ts:
                                    active_entries += 1
                            except (json.JSONDecodeError, ValueError, TypeError):
                                pass
                if cursor == 0:
                    break

        total = self._hits + self._misses
        backend_name = "redis" if isinstance(self, RedisCache) else "valkey"
        return {
            "backend": backend_name,
            "active_entries": active_entries,
            "hits": self._hits,
            "misses": self._misses,
            "sets": self._sets,
            "hit_rate": round(self._hits / total, 4) if total else 0.0,
        }

    async def close(self) -> None:
        """Close client connections."""
        self._closed = True
        if self._client:
            await self._client.aclose()
            self._client = None


class RedisCache(ValkeyCache):
    """Redis persistent cache backend, sharing ValkeyCache's implementation."""
