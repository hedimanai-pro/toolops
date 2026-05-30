# ToolOps v0.3.0 — Release Notes

**Release Date:** 2026-05-30
**Codename:** Batteries Included
**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## Summary

ToolOps v0.3.0 is a **major feature and usability release** that introduces four new robust cache backends, refactors the caching subsystem into a modular package structure, and drastically simplifies the developer experience. 

With this release, **ToolOps transitions to a "batteries-included" dependency model**. Installing `toolops` now automatically bundles all database drivers, caching clients, and OpenTelemetry instrumentation, making it instantly functional for every production scenario out-of-the-box.

**Key themes:** Caching, Usability, Modularity, Developer Experience.

---

## What's New

### Simplified Caching Installation (Batteries Included)

Previously, developers had to manage multiple optional dependencies (extras) like `toolops[postgres]` or `toolops[otel]` to use specific database drivers or telemetry systems. 

In v0.3.0, all standard drivers and utility libraries have been moved to default dependencies:
* **SQLite**: `aiosqlite`
* **Valkey / Redis**: `redis[hiredis]`
* **MySQL / MariaDB**: `aiomysql`
* **PostgreSQL**: `asyncpg`
* **OpenAI Embeddings**: `openai`
* **Telemetry**: `opentelemetry-api` & `prometheus-client`
* **Semantic Caching**: `sentence-transformers` & `numpy`

A single command installs all capabilities:
```bash
pip install toolops
```
*Note: All old optional dependency extras (`postgres`, `sqlite`, `valkey`, `redis`, `mysql`, `openai`, `otel`, `semantic`, `all`) remain defined in `pyproject.toml` as empty groups or aliases to ensure complete backward compatibility with existing deployment scripts.*

---

### Four New Cache Backends

The cache storage layer has been expanded with three new first-class database drivers and a dedicated alias backend:

1. **`SQLiteCache`** (`sqlite.py`):
   * Perfect for local development, single-process apps, or serverless deployments.
   * Utilizes a highly optimized two-table relational schema with indexes.
   * Fully supports tag-based invalidation via `ON DELETE CASCADE` foreign keys.
2. **`ValkeyCache`** (`valkey.py`):
   * Designed for high-concurrency, distributed environments.
   * Targets [Valkey](https://valkey.io/) (the open-source Redis fork) using the asynchronous connection pool.
   * Employs Sets for efficient O(1) tag-based tracking and invalidation.
3. **`RedisCache`** (`valkey.py`):
   * An alias class inheriting from `ValkeyCache` to provide native Redis nomenclature for existing clouds and deployments.
4. **`MySQLCache`** (`mysql.py`):
   * Compatible with MySQL 8.0+ and MariaDB 10.5+.
   * Uses a normalized dual-table schema with transactional commits and cleanups.
   * Employs `ON DUPLICATE KEY UPDATE` upsert semantics.

---

### Modular Caching Package Structure

To prevent the caching codebase from bloating, the single `toolops/cache.py` module has been refactored into a clean python package directory (`toolops/cache/`):
* `base.py`: Interface contracts (`CacheBackend`, `TaggedCacheMixin`) and common math/time helper utilities.
* `memory.py`, `file.py`, `postgres.py`, `semantic.py`: Moved from the original monolithic file.
* `sqlite.py`, `valkey.py`, `mysql.py`: New backend modules.
* `__init__.py`: Package facade exposing all public classes and managers.

All imports like `from toolops.cache import MemoryCache` remain **100% backward-compatible**.

---

## Verification & Type Safety

* **mypy Strict Mode**: All 9 cache modules fully pass strict static analysis with zero errors (`mypy --strict`).
* **Test Matrix Coverage**: Added extensive unit and integration tests inside `tests/test_backends.py`.
* **Zero Regressions**: Verified that all existing resilience, request coalescing, sync-wrapper, and third-party integrations pass cleanly.

---

## Migration Notes

### For users upgrading from v0.2.x

No code changes are required. Simply upgrade via pip:
```bash
pip install --upgrade toolops
```

All references to install extras (e.g. `toolops[postgres]`) can be simplified to just `toolops` in your `requirements.txt` or `pyproject.toml`.
