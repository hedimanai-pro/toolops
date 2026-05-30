# ToolOps v1.0.0 — Release Notes

**Release Date:** 2026-05-30  
**Codename:** Stable Default Install  
**Full Changelog:** [CHANGELOG.md](CHANGELOG.md)

---

## Summary

ToolOps v1.0.0 formalizes the package as a stable, batteries-included SDK. The default installation path is now the only recommended user-facing path:

```bash
pip install toolops
```

No optional extras are required for standard cache backends, database drivers, semantic caching, OpenAI embeddings, or telemetry support.

**Key themes:** Stability, Developer Experience, Packaging Simplicity.

---

## What's Changed

### Single Install Command

ToolOps now treats `pip install toolops` as the complete installation contract. The default dependency set includes the supported production backends and integration libraries:

* **PostgreSQL** via `asyncpg`
* **SQLite** via `aiosqlite`
* **Valkey / Redis** via `redis`
* **MySQL / MariaDB** via `aiomysql`
* **Semantic caching** via `sentence-transformers` and `numpy`
* **OpenAI embeddings** via `openai`
* **Telemetry** via `opentelemetry-api` and `prometheus-client`

Legacy extras remain defined for compatibility with existing deployment scripts, but new installations should use the plain package name.

---

### Development Workflow Cleanup

Contributor and automation workflows no longer use extras-based editable installs.

* `make install` installs the local package with default dependencies.
* `make install-dev` installs from `requirements.txt`, including the local editable package and development tools.
* `Dockerfile` installs ToolOps through the same requirements-driven development path.
* Runtime ImportError guidance now points users to `pip install toolops`.

This keeps local development aligned with the public installation model while preserving the tools required for testing, linting, and type checking.

---

## Migration Notes

### For users

Replace any extras-based install command with:

```bash
pip install --upgrade toolops
```

Examples:

* Replace `toolops[postgres]` with `toolops`.
* Replace `toolops[sqlite]` with `toolops`.
* Replace `toolops[valkey]` or `toolops[redis]` with `toolops`.
* Replace `toolops[mysql]` with `toolops`.
* Replace `toolops[semantic]` or `toolops[openai]` with `toolops`.

### For contributors

Use:

```bash
pip install -r requirements.txt
make test
make lint
make typecheck
```

This installs ToolOps in editable mode and includes the development toolchain.

---

## Compatibility

This release does not require application code changes. Existing imports, decorators, cache backends, and CLI commands continue to work.

The old extras are retained as compatibility aliases so existing CI and deployment scripts do not fail immediately, but they are no longer necessary.
