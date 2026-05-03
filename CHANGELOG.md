# Changelog

All notable changes to ToolOps are documented here.

Format: [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)
Versioning: [Semantic Versioning](https://semver.org/)

---

## [Unreleased]

### Added
- **MCP Integration**: Helper to convert ToolOps-decorated tools to Model Context Protocol definitions.
- **Enhanced Sync Support**: `sync_wrapper` now handles existing event loops via `asyncio.run_coroutine_threadsafe`.
- **Personal Branding**: Integrated [Hedi MANAI](https://hedimanai.vercel.app/) professional profiles and branding.
- **CLI & Operations**: Added a full-featured CLI (`toolops`) for system health checks (`doctor`), cache statistics (`stats`), metrics (`metrics`), and management (`clear`, `inspect-key`).

### Removed
- **Redis Backend**: Removed RedisCache and RedisRequestCoalescer to simplify the core SDK and focus on modern backends (Postgres, Semantic).

### Planned
- **Web Dashboard**: Real-time metrics, cost attribution, and hit rates UI.
- **Budget Control**: Hard limits on tool-induced API costs per hour/day.
- **Native MCP Server**: One-click deployment of ToolOps tools as a standalone host.
- **Streaming Middleware**: Support for streaming tool outputs in real-time.
- **New Backends**: MariaDB, ChromaDB, and Pinecone support.

---

## [0.1.0] — 2026-04-26

First public release of ToolOps. 🎉

### Added

**Core decorators**
- `@tool(...)` — universal decorator with full configuration
- `@readonly(...)` — shortcut for cached read-only tools
- `@sideeffect(...)` — shortcut for uncached side-effect tools
- `@stateful(...)` — shortcut for short-TTL stateful tools

**Cache backends**
- `MemoryCache` — in-process TTL cache, zero dependencies
- `PostgresCache` — PostgreSQL backend via `asyncpg` (`pip install "toolops[postgres]"`)
- `FileCache` — file-system JSON cache, zero dependencies
- `SemanticCache` — similarity-based cache using cosine distance

**Semantic cache**
- `SentenceTransformerEmbedder` — local embedder via `sentence-transformers`
- `OpenAIEmbedder` — cloud embedder via OpenAI Embeddings API
- Pure-Python cosine similarity fallback (no numpy required)
- Configurable similarity threshold (default: 0.92)
- Automatic TTL expiry and capacity eviction

**Infrastructure**
- `CacheManager` — central registry, supports multiple named backends
- `RequestCoalescer` — collapses concurrent identical calls into one execution
- `ToolOpsLogger` — structured JSON logging (timestamp, event, tool, duration)
- Retry with configurable count, delay and exponential backoff
- Per-tool timeout via `asyncio.wait_for`
- Full async and sync function support

**Developer experience**
- Zero required dependencies for core usage
- Optional extras: `[postgres]`, `[semantic]`, `[openai]`, `[all]`
- Type hints throughout, mypy strict compatible
- pytest suite with asyncio support
- CI/CD via GitLab CI
- Apache 2.0 license

### Notes
- Python 3.9+ required
- All cache backends implement the abstract `CacheBackend` interface
- Custom backends can be added by subclassing `CacheBackend`