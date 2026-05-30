"""
Name: semantic.py

Description: Similarity-based semantic cache backend for ToolOps SDK.

Last_updated: 2026-05-30

Updated_by: Antigravity
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import json
from collections import deque
from typing import Any, cast

from .base import (
    CacheBackend,
    CacheEntry,
    TaggedCacheMixin,
    _normalise_tags,
    _now,
    cosine_similarity,
)


class SentenceTransformerEmbedder:
    """Local embedder using sentence-transformers."""

    def __init__(self, model: str = "all-MiniLM-L6-v2") -> None:
        """
        Initialize the embedder.

        Args:
            model: Model name.
        """
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(model)
        except ImportError as exc:
            raise ImportError(
                "SentenceTransformerEmbedder requires sentence-transformers. "
                "Install it with: pip install toolops"
            ) from exc

    async def embed(self, text: str) -> list[float]:
        """
        Generate embedding for text.

        Args:
            text: Input text.

        Returns:
            Vector embedding.
        """
        return cast(
            list[float], self._model.encode(text, convert_to_numpy=True).tolist()
        )


class OpenAIEmbedder:
    """Cloud embedder using OpenAI API."""

    def __init__(
        self, api_key: str | None = None, model: str = "text-embedding-3-small"
    ) -> None:
        """
        Initialize OpenAI embedder.

        Args:
            api_key: Optional API key.
            model: OpenAI model name.
        """
        try:
            from openai import AsyncOpenAI

            self._client = AsyncOpenAI(api_key=api_key)
            self._model = model
        except ImportError as exc:
            raise ImportError(
                "OpenAIEmbedder requires openai. "
                "Install it with: pip install toolops"
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
        return cast(list[float], response.data[0].embedding)


class SemanticCache(CacheBackend, TaggedCacheMixin):
    """Similarity-based semantic cache with O(1) LRU eviction."""

    def __init__(
        self, embedder: Any, threshold: float = 0.92, max_entries: int = 1_000
    ) -> None:
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
        self._entries: deque[dict[str, Any]] = deque(maxlen=max_entries)
        self._hits = 0
        self._misses = 0
        self._semantic_hits = 0
        self._sets = 0
        self._closed = False

    def _check_closed(self) -> None:
        """Check if backend is closed."""
        if self._closed:
            raise RuntimeError("SemanticCache is closed.")

    async def connect(self) -> None:
        """Connect to semantic cache (noop)."""
        self._closed = False

    async def close(self) -> None:
        """Close semantic cache."""
        self._closed = True

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
        self._check_closed()
        entry = await self.get_entry(key)
        if entry:
            self._hits += 1
            return entry.value
        self._misses += 1
        return None

    async def get_entry(
        self, key: str, *, allow_stale: bool = False
    ) -> CacheEntry | None:
        """
        Find best matching entry.

        Args:
            key: Cache key.
            allow_stale: Allow stale result.

        Returns:
            Best entry or None.
        """
        self._check_closed()
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
        Store value with embedding.

        Args:
            key: Cache key.
            value: Store value.
            ttl: TTL seconds.
            tags: Optional tags.
            stale_ttl: Optional stale TTL.
        """
        self._check_closed()
        query = self._extract_query(key)
        embedding = await self._embedder.embed(query) if query else []
        entry = CacheEntry.create(key, value, ttl, tags=tags, stale_ttl=stale_ttl)
        self._cleanup()

        # Remove existing entry for this key to avoid duplicates
        self._entries = deque(
            [wrapped for wrapped in self._entries if wrapped["entry"].key != key],
            maxlen=self._max_entries,
        )

        self._entries.append({"entry": entry, "query": query, "embedding": embedding})
        self._sets += 1

    async def delete(self, key: str) -> None:
        """
        Delete key from semantic store.

        Args:
            key: Cache key.
        """
        self._check_closed()
        self._entries = deque(
            [wrapped for wrapped in self._entries if wrapped["entry"].key != key],
            maxlen=self._max_entries,
        )

    async def clear(self) -> None:
        """Clear all semantic entries."""
        self._check_closed()
        self._entries.clear()

    async def invalidate_tags(self, tags: list[str]) -> int:
        """
        Invalidate semantic entries by tags.

        Args:
            tags: Tags to drop.

        Returns:
            Removed count.
        """
        self._check_closed()
        wanted = _normalise_tags(tags)
        before = len(self._entries)
        self._entries = deque(
            [
                wrapped
                for wrapped in self._entries
                if not self._matching_tags(wrapped["entry"].tags, wanted)
            ],
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
        self._check_closed()
        self._cleanup()
        total = self._hits + self._misses
        fresh_entries = sum(
            1 for wrapped in self._entries if wrapped["entry"].is_fresh()
        )
        stale_entries = sum(
            1 for wrapped in self._entries if wrapped["entry"].is_stale()
        )

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
