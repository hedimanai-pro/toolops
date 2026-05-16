# ToolOps v0.2.0 — Release Notes

**Release Date:** 2026-05-16
**Codename:** Stabilisation
**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## Summary

ToolOps v0.2.0 is a **stability and security release** that transforms the codebase from a functional prototype into a production-ready foundation. This release introduces a middleware pipeline architecture, fixes critical production bugs, adds comprehensive CI/CD, and hardens security across the entire SDK.

**Key themes:** Security, Testability, Architecture, Developer Experience.

---

## What's New

### Middleware Pipeline Architecture

The monolithic `@tool` decorator (~200 lines of intertwined logic) has been refactored into a **composable pipeline of independent middlewares**:

| Middleware | Responsibility |
| :--- | :--- |
| `LoggingMiddleware` | Structured JSON logging for every tool call |
| `CacheMiddleware` | Cache lookup, stale-if-error, cache write |
| `CircuitBreakerMiddleware` | Circuit breaker protection |
| `RetryMiddleware` | Retry loop with exponential backoff |
| `CoalescingMiddleware` | Request coalescing (deduplication) |
| `FallbackMiddleware` | Fallback execution on failure |

- **New file:** `toolops/middlewares.py` — full middleware framework
- **New class:** `ToolExecutor` — orchestrates middleware execution
- **New class:** `ToolContext` — shared mutable context across middlewares
- **New public API:** `build_executor()`, `DEFAULT_PIPELINE`
- The decorator behavior is **100% preserved** — no breaking changes for existing users

### Security Hardening

#### SHA-256 Cache Key Hashing
- All cache keys are now **SHA-256 hashed** instead of plaintext JSON serialization
- Prevents sensitive data (API tokens, PII) from appearing in cache keys and logs
- **New parameter:** `sensitive_params` on all decorators — explicitly exclude parameter names from cache keys

#### Automatic Parameter Masking in Logs
- Parameter values containing known sensitive keywords are automatically masked as `***MASKED***` in structured logs
- Covered keywords: `token`, `api_key`, `password`, `secret`, `auth`, `authorization`, `credential`, `access_token`, `refresh_token`, `private_key`, `bearer`

#### PostgreSQL Cache Security
- Tag-based invalidation now uses **server-side filtering** with GIN index — no more loading all cache entries into memory

### CI/CD Pipelines

- **`.github/workflows/ci.yml`** — Full CI pipeline:
  - Lint with Ruff
  - Format check with Black
  - Type check with mypy (strict mode)
  - Test matrix across Python 3.9, 3.10, 3.11, 3.12
  - Coverage reporting with Codecov (80% minimum)
- **`.github/workflows/release.yml`** — Automated release pipeline:
  - Runs full test suite on tag push
  - Builds wheel + sdist
  - Publishes to PyPI automatically (trusted publishing)

### Docker Development Environment

- **`Dockerfile`** — Containerized development environment
- **`docker-compose.yml`** — One-command setup with PostgreSQL:
  ```bash
  docker-compose up -d
  docker-compose exec toolops make test
  ```

### Makefile

Standardized development commands:
```bash
make test      # Run full test suite with coverage
make lint      # Ruff + Black checks
make format    # Auto-format with Black
make typecheck # mypy strict mode
make coverage  # HTML coverage report
make clean     # Remove all build artifacts
```

### Community Files

- `CODE_OF_CONDUCT.md` — Community standards
- `SECURITY.md` — Security policy and vulnerability reporting
- `.github/ISSUE_TEMPLATE/bug_report.md` — Structured bug reports
- `.github/ISSUE_TEMPLATE/feature_request.md` — Feature request template
- `.github/PULL_REQUEST_TEMPLATE.md` — PR checklist
- `CONTRIBUTING.md` — Complete contribution guide (setup, workflow, conventions)

---

## Bug Fixes

### Critical

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **PostgresCache OOM** | `invalidate_tags()` loaded all cache entries into memory for Python-side tag matching, causing OOM on large tables | Server-side filtering with GIN index + `jsonb @>` operator |
| **SemanticCache O(n)** | Used `list.pop(0)` for LRU eviction, causing linear time complexity | Replaced with `collections.deque(maxlen=...)` for O(1) operations |

### Security

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **Cache key leakage** | Cache keys contained plaintext serialized arguments, potentially exposing sensitive data | SHA-256 hashing of all cache keys |
| **Log parameter exposure** | Tool arguments were logged in plaintext, including potentially sensitive values | Automatic masking of known sensitive parameter names |

### Performance

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **MemoryCache race conditions** | No concurrency protection for cache operations under multi-threaded load | Added `asyncio.Lock` for all critical sections |

### Build

| Issue | Description | Fix |
| :--- | :--- | :--- |
| **Dual packaging** | `setup.py` (v0.1.0) and `pyproject.toml` (v0.1.1) coexisted with different versions | Removed `setup.py`, unified on `pyproject.toml` (PEP 621) |

---

## Breaking Changes

**None.** This release is fully backward-compatible. All existing `@tool`, `@readonly`, `@sideeffect`, and `@stateful` usage continues to work without modification.

The only visible change is that cache keys are now SHA-256 hashes (hex strings) instead of human-readable JSON. If your code relies on inspecting cache key contents, you will need to update those sections.

---

## Migration Notes

### For users upgrading from v0.1.x

No action required. Upgrade with:

```bash
pip install --upgrade toolops
```

### For contributors

The development workflow now uses `make` targets. Update your local setup:

```bash
pip install -e ".[all,dev]"
make test   # Instead of: pytest tests/
make lint   # Instead of: ruff check .
```

---

## Metrics

| Metric | v0.1.1 | v0.2.0 |
| :--- | :--- | :--- |
| Test files | 8 | 8 |
| Source modules | 7 | 8 (+middlewares) |
| CI/CD pipelines | 0 | 2 |
| Cache key security | Plaintext | SHA-256 |
| Log security | Plaintext | Auto-masking |
| PostgreSQL invalidation | O(n) memory | O(1) index |
| SemanticCache eviction | O(n) | O(1) |
| MemoryCache thread-safety | None | `asyncio.Lock` |

---

## Acknowledgments

This release was made possible by the community feedback and contributions since v0.1.0. Thank you for reporting issues, suggesting features, and helping make ToolOps better.

**Full commit log:** `git log v0.1.1..v0.2.0`
