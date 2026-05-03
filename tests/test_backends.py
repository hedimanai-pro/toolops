"""
Name: test_backends.py

Description: Unit tests for cache backend implementations.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import os
import tempfile
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime, timedelta, timezone

import pytest

from toolops.cache import FileCache, PostgresCache, SemanticCache


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
    mock_conn.fetchrow.return_value = {
        "value": value,
        "expires_at": expires_at
    }

    # Get
    result = await cache.get(key)
    assert result == value

    # Set
    await cache.set(key, value, ttl=60)
    assert mock_conn.execute.called


@pytest.mark.asyncio
async def test_semantic_cache_logic():
    """Test semantic similarity matching with mocked embedder."""

    mock_embedder = AsyncMock()
    mock_embedder.embed.side_effect = lambda text: [1.0, 0.0] if "password" in text else [0.0, 1.0]

    cache = SemanticCache(embedder=mock_embedder, threshold=0.9)

    # Set entry
    key = 'tool:test:[["query", "how to reset password"]]'
    await cache.set(key, "Instructions", ttl=3600)

    # Semantic Hit
    hit_key = 'tool:test:[["query", "forgot password"]]'
    res = await cache.get(hit_key)

    assert res == "Instructions"
    assert mock_embedder.embed.call_count == 2
