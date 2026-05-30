"""
Name: test_backends.py

Description: Tests for cache backends (Memory, File, Postgres).

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import json
import os
import sys
import tempfile
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest

from toolops.cache import (
    CacheEntry,
    FileCache,
    MemoryCache,
    MySQLCache,
    OpenAIEmbedder,
    PostgresCache,
    RedisCache,
    SemanticCache,
    SentenceTransformerEmbedder,
    SQLiteCache,
    ValkeyCache,
)
from toolops.cache.base import _now


@pytest.mark.asyncio
async def test_sqlite_cache_operations():
    """Test SQLiteCache operations using a live in-memory database."""
    # SQLiteCache with :memory: acts as a real in-memory SQL database
    cache = SQLiteCache(database=":memory:")
    await cache.connect()

    key = "sqlite-key"
    value = {"msg": "hello sqlite"}

    # Set
    await cache.set(key, value, ttl=60, tags=["sqlite-tag"])

    # Get
    result = await cache.get(key)
    assert result == value

    # Invalidate tags
    invalidated = await cache.invalidate_tags(["sqlite-tag"])
    assert invalidated == 1
    assert await cache.get(key) is None

    # Stats
    stats = await cache.stats()
    assert stats["backend"] == "sqlite"
    assert stats["database"] == ":memory:"


@pytest.mark.asyncio
async def test_valkey_and_redis_cache_mocked():
    """Test ValkeyCache and RedisCache using async mocks."""
    mock_client = AsyncMock()
    mock_client.get.return_value = None
    mock_client.scan.return_value = (0, [])

    cache = ValkeyCache(host="localhost", port=6379)
    cache._client = mock_client

    key = "valkey-key"
    value = {"data": "valkey"}

    # Set
    await cache.set(key, value, ttl=60, tags=["tag1"])
    assert mock_client.set.called

    # Get (mock return)
    from toolops.cache import CacheEntry

    entry = CacheEntry.create(key, value, ttl=60, tags=["tag1"])
    import json

    mock_client.get.return_value = json.dumps(entry.payload())
    result = await cache.get(key)
    assert result == value

    # Invalidate tags
    mock_client.smembers.return_value = {key}
    deleted = await cache.invalidate_tags(["tag1"])
    assert deleted == 1

    # RedisCache test (verifies inheritance and stats name)
    redis_cache = RedisCache(host="localhost")
    redis_cache._client = mock_client
    redis_stats = await redis_cache.stats()
    assert redis_stats["backend"] == "redis"


@pytest.mark.asyncio
async def test_mysql_cache_mocked():
    """Test MySQLCache using async mocks."""
    mock_cur = AsyncMock()
    mock_conn = AsyncMock()

    # Mock await conn.cursor() returning an async context manager
    cur_mock = AsyncMock()
    cur_mock.__aenter__.return_value = mock_cur
    mock_conn.cursor.return_value = cur_mock

    # Mock pool acquire context manager
    mock_pool = MagicMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value = mock_context
    mock_pool.size = 5

    cache = MySQLCache(host="localhost", user="root", db="toolops")
    cache._pool = mock_pool

    key = "mysql-key"
    value = {"sql": "data"}

    # Set
    await cache.set(key, value, ttl=60, tags=["mysql-tag"])
    assert mock_cur.execute.called
    assert mock_conn.commit.called

    # Get
    import json

    from toolops.cache import CacheEntry

    entry = CacheEntry.create(key, value, ttl=60, tags=["mysql-tag"])
    mock_cur.fetchone.side_effect = [
        {"value": json.dumps(entry.payload()), "expires_at_ts": entry.stale_until},
        {"count": 1},
    ]
    result = await cache.get(key)
    assert result == value

    # Invalidate tags
    mock_cur.rowcount = 1
    deleted = await cache.invalidate_tags(["mysql-tag"])
    assert deleted == 1

    # Stats
    stats = await cache.stats()
    assert stats["backend"] == "mysql"


@pytest.mark.asyncio
async def test_file_cache_operations():
    """Test standard file-based cache operations."""

    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(directory=tmpdir)
        key = "test-key"
        value = {"data": 123}

        # Set
        await cache.set(key, value, ttl=60)
        assert len(list(os.listdir(tmpdir))) == 1

        # Get
        retrieved = await cache.get(key)
        assert retrieved == value

        # Stats
        stats = await cache.stats()
        assert stats["fresh_entries"] == 1
        assert stats["hits"] == 1

        # Delete
        await cache.delete(key)
        assert len(list(os.listdir(tmpdir))) == 0


@pytest.mark.asyncio
async def test_postgres_cache_mocked():
    """Test Postgres cache logic using async mocks."""

    mock_conn = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_conn

    mock_pool = MagicMock()
    mock_pool.acquire.return_value = mock_context

    cache = PostgresCache(dsn="postgresql://user:pass@localhost/db")
    cache._pool = mock_pool

    key = "pg-key"
    value = {"hello": "world"}

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=60)
    mock_conn.fetchrow.return_value = {"value": value, "expires_at": expires_at}

    # Get
    result = await cache.get(key)
    assert result == value

    # Set
    await cache.set(key, value, ttl=60)
    assert mock_conn.execute.called

    # Delete
    await cache.delete(key)
    assert mock_conn.execute.call_count >= 2

    # Clear
    await cache.clear()
    assert mock_conn.execute.call_count >= 3

    # Stats
    mock_conn.fetchval.return_value = 10
    stats = await cache.stats()
    assert stats["backend"] == "postgres"


@pytest.mark.asyncio
async def test_semantic_cache_logic():
    """Test semantic similarity matching with mocked embedder."""

    mock_embedder = AsyncMock()
    mock_embedder.embed.side_effect = lambda text: (
        [1.0, 0.0] if "password" in text else [0.0, 1.0]
    )

    cache = SemanticCache(embedder=mock_embedder, threshold=0.9)

    # Set entry
    key = 'tool:test:[["query", "how to reset password"]]'
    await cache.set(key, "Instructions", ttl=3600)

    # Semantic Hit
    hit_key = 'tool:test:[["query", "forgot password"]]'
    res = await cache.get(hit_key)

    assert res == "Instructions"
    assert mock_embedder.embed.call_count == 2

    # Clear
    await cache.clear()
    assert len(cache._entries) == 0

    # Stats
    stats = await cache.stats()
    assert stats["backend"] == "semantic"


def test_cache_entry_serialization():
    """Test that CacheEntry can be converted to/from payload correctly."""
    from toolops.cache import CacheEntry

    entry = CacheEntry.create("k1", {"data": 1}, ttl=60, tags=["t1"])
    payload = entry.payload()

    assert payload["key"] == "k1"
    assert payload["value"]["data"] == 1
    assert "t1" in payload["tags"]

    # Reconstruct
    new_entry = CacheEntry.from_payload("k1", payload)
    assert new_entry.value == entry.value
    assert new_entry.tags == entry.tags
    assert new_entry.fresh_until == entry.fresh_until


@pytest.mark.asyncio
async def test_memory_cache_stats_and_clear():
    """Test MemoryCache stats tracking and clear operation."""
    from toolops.cache import MemoryCache

    cache = MemoryCache()

    await cache.set("k1", "v1", ttl=60)
    await cache.get("k1")  # Hit
    await cache.get("k2")  # Miss

    stats = await cache.stats()
    assert stats["hits"] == 1
    assert stats["misses"] == 1
    assert stats["size"] == 1

    await cache.clear()
    assert len(cache._store) == 0


@pytest.mark.asyncio
async def test_sqlite_cache_edge_cases():
    """Test SQLiteCache edge cases and error paths."""
    cache = SQLiteCache(database=":memory:")
    await cache.connect()

    # Connection idempotent
    await cache.connect()

    key = "sqlite-edge"
    # Set with stale window
    await cache.set(key, "edge-val", ttl=1, stale_ttl=10, tags=["t1"])

    # Inspect key
    metadata = await cache.inspect(key)
    assert metadata is not None
    assert metadata["key"] == key
    assert metadata["value"] == "edge-val"

    # Invalidate tags with empty list
    assert await cache.invalidate_tags([]) == 0

    # Delete
    await cache.delete(key)
    assert await cache.get(key) is None

    # Clear
    await cache.set("k1", "v1", ttl=60)
    await cache.clear()
    assert await cache.get("k1") is None

    # Stale/Expired retrieval
    # Inject an expired entry directly into cache to test parser / expiration
    expired_entry = CacheEntry.create(
        "expired-key", "expired-val", ttl=-10, stale_ttl=-5
    )
    conn = await cache._ensure_conn()
    await conn.execute(
        "INSERT INTO toolops_cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
        ("expired-key", json.dumps(expired_entry.payload()), _now() - 5, _now() - 10),
    )
    await conn.commit()
    assert await cache.get("expired-key") is None

    # Inject a stale entry (fresh_until is in the past, but stale_until is in the future)
    stale_entry = CacheEntry.create("stale-key", "stale-val", ttl=-5, stale_ttl=100)
    await conn.execute(
        "INSERT INTO toolops_cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
        ("stale-key", json.dumps(stale_entry.payload()), _now() + 100, _now() - 10),
    )
    await conn.commit()
    # default get doesn't allow stale
    assert await cache.get("stale-key") is None
    # get_entry with allow_stale allows it
    res = await cache.get_entry("stale-key", allow_stale=True)
    assert res is not None
    assert res.value == "stale-val"

    # Inject corrupted JSON
    await conn.execute(
        "INSERT INTO toolops_cache (key, value, expires_at, created_at) VALUES (?, ?, ?, ?)",
        ("corrupt-key", "{invalid-json", _now() + 100, _now()),
    )
    await conn.commit()
    assert await cache.get("corrupt-key") is None

    # Close
    await cache.close()
    assert cache._conn is None


@pytest.mark.asyncio
async def test_file_cache_edge_cases():
    """Test FileCache edge cases."""
    with tempfile.TemporaryDirectory() as tmpdir:
        cache = FileCache(directory=tmpdir)
        # Empty tag invalidation
        assert await cache.invalidate_tags([]) == 0

        # Clear
        await cache.set("k1", "v1", ttl=60)
        await cache.clear()
        assert await cache.get("k1") is None


@pytest.mark.asyncio
async def test_valkey_cache_edge_cases():
    """Test ValkeyCache/RedisCache edge cases."""
    mock_client = AsyncMock()
    cache = ValkeyCache(host="localhost", port=6379)
    cache._client = mock_client

    # Connect idempotency: _client is already set, connect() should return early
    await cache.connect()

    # Empty tag invalidation
    assert await cache.invalidate_tags([]) == 0

    # Delete
    await cache.delete("k1")
    assert mock_client.delete.called

    # Clear
    mock_client.scan.side_effect = [(0, ["toolops:cache:k1", "toolops:tag:t1"])]
    await cache.clear()
    assert mock_client.delete.call_count >= 2

    # Close: close() calls _client.aclose(), not pool.disconnect
    await cache.close()
    assert mock_client.aclose.called
    assert cache._client is None


@pytest.mark.asyncio
async def test_mysql_cache_edge_cases():
    """Test MySQLCache edge cases."""
    mock_cur = AsyncMock()
    mock_conn = AsyncMock()
    cur_mock = AsyncMock()
    cur_mock.__aenter__.return_value = mock_cur
    mock_conn.cursor.return_value = cur_mock
    # Pool must be MagicMock so acquire() returns a value (not a coroutine),
    # but close()/wait_closed() need to match aiomysql's actual signatures:
    # close() is synchronous, wait_closed() is a coroutine.
    mock_pool = MagicMock()
    mock_pool.close = MagicMock()  # sync call
    mock_pool.wait_closed = AsyncMock()  # async call
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_conn
    mock_pool.acquire.return_value = mock_context
    mock_pool.size = 5

    cache = MySQLCache(host="localhost")
    cache._pool = mock_pool

    # Connect idempotency: _pool is already set, connect() should return early
    await cache.connect()

    # Invalidate tags empty list
    assert await cache.invalidate_tags([]) == 0

    # Clear
    await cache.clear()
    assert mock_cur.execute.called

    # Close: calls pool.close() (sync) then awaits pool.wait_closed()
    await cache.close()
    assert mock_pool.close.called
    assert mock_pool.wait_closed.called
    assert cache._pool is None


@pytest.mark.asyncio
async def test_postgres_cache_edge_cases():
    """Test PostgresCache edge cases."""
    mock_conn = AsyncMock()
    mock_context = AsyncMock()
    mock_context.__aenter__.return_value = mock_conn
    mock_pool = AsyncMock()
    mock_pool.acquire.return_value = mock_context

    cache = PostgresCache(dsn="postgresql://localhost")
    cache._pool = mock_pool

    # Connect idempotency: _pool is already set, connect() returns early
    await cache.connect()

    # Invalidate tags empty list
    assert await cache.invalidate_tags([]) == 0

    # Close: now also nulls out _pool
    mock_pool_close = AsyncMock()
    cache._pool = mock_pool_close
    await cache.close()
    assert mock_pool_close.close.called
    assert cache._pool is None


@pytest.mark.asyncio
async def test_semantic_cache_edge_cases():
    """Test SemanticCache edge cases."""
    mock_embedder = AsyncMock()
    cache = SemanticCache(embedder=mock_embedder)

    # Invalidate tags empty list
    assert await cache.invalidate_tags([]) == 0

    # ImportError check for SentenceTransformerEmbedder
    with pytest.raises(ImportError):
        # Trigger import error by mocking sentence_transformers import failure
        real_modules = sys.modules.copy()
        try:
            sys.modules["sentence_transformers"] = None  # type: ignore
            SentenceTransformerEmbedder()
        finally:
            sys.modules = real_modules

    # ImportError check for OpenAIEmbedder
    with pytest.raises(ImportError):
        real_modules = sys.modules.copy()
        try:
            sys.modules["openai"] = None  # type: ignore
            OpenAIEmbedder()
        finally:
            sys.modules = real_modules


@pytest.mark.asyncio
async def test_all_backends_lifecycle_and_closed_errors():
    """Test connect(), close(), idempotency, and check-closed behavior across all backends."""
    # 1. MemoryCache
    mem = MemoryCache()
    await mem.connect()
    await mem.set("k", "v", 60)
    assert await mem.get("k") == "v"
    await mem.close()
    with pytest.raises(RuntimeError, match="closed"):
        await mem.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await mem.set("k", "v", 60)
    with pytest.raises(RuntimeError, match="closed"):
        await mem.delete("k")
    with pytest.raises(RuntimeError, match="closed"):
        await mem.clear()
    with pytest.raises(RuntimeError, match="closed"):
        await mem.invalidate_tags(["t"])
    with pytest.raises(RuntimeError, match="closed"):
        await mem.inspect("k")
    with pytest.raises(RuntimeError, match="closed"):
        await mem.stats()

    # Re-connect should open it back up
    await mem.connect()
    await mem.set("k", "v2", 60)
    assert await mem.get("k") == "v2"

    # 2. FileCache
    with tempfile.TemporaryDirectory() as tmpdir:
        fc = FileCache(directory=tmpdir)
        await fc.connect()
        await fc.set("k", "v", 60)
        assert await fc.get("k") == "v"
        await fc.close()
        with pytest.raises(RuntimeError, match="closed"):
            await fc.get("k")
        with pytest.raises(RuntimeError, match="closed"):
            await fc.set("k", "v", 60)
        await fc.connect()
        await fc.set("k2", "v2", 60)

    # 3. SQLiteCache
    sc = SQLiteCache(database=":memory:")
    await sc.connect()
    await sc.set("k", "v", 60)
    await sc.close()
    with pytest.raises(RuntimeError, match="closed"):
        await sc.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await sc.set("k", "v", 60)
    await sc.connect()
    await sc.set("k2", "v2", 60)
    await sc.close()

    # 4. PostgresCache
    pc = PostgresCache(dsn="postgresql://localhost")
    pc._pool = AsyncMock()
    await pc.connect()
    await pc.close()
    with pytest.raises(RuntimeError, match="closed"):
        await pc.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await pc.set("k", "v", 60)

    # 5. ValkeyCache
    vc = ValkeyCache(host="localhost")
    vc._client = AsyncMock()
    await vc.connect()
    await vc.close()
    with pytest.raises(RuntimeError, match="closed"):
        await vc.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await vc.set("k", "v", 60)

    # 6. MySQLCache
    # aiomysql pool.close() is synchronous; wait_closed() is async.
    mc = MySQLCache(host="localhost")
    mock_mysql_pool = MagicMock()
    mock_mysql_pool.wait_closed = AsyncMock()
    mc._pool = mock_mysql_pool
    await mc.connect()
    await mc.close()
    with pytest.raises(RuntimeError, match="closed"):
        await mc.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await mc.set("k", "v", 60)

    # 7. SemanticCache
    mock_emb = AsyncMock()
    sem = SemanticCache(embedder=mock_emb)
    await sem.connect()
    await sem.close()
    with pytest.raises(RuntimeError, match="closed"):
        await sem.get("k")
    with pytest.raises(RuntimeError, match="closed"):
        await sem.set("k", "v", 60)
