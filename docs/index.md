# ToolOps Documentation

<img src="assets/logo.png" width="150" alt="ToolOps Logo">

**The Resilience & Efficiency Layer for AI Agent Tools.**

ToolOps is a **framework-agnostic middleware SDK** by **Hedi MANAI** that sits between your AI agent and its tools — adding industrial-grade caching, resilience, and observability in a single decorator.

---

## Why ToolOps?

Every production AI agent eventually faces the same problems:

| Problem | Without ToolOps | With ToolOps |
|---|---|---|
| **Redundant Costs** | 100 calls = 100 credits | 1 call, 99 cache hits |
| **Similar Queries** | Treated as different | Semantic match → same result |
| **API Instability** | Agent crashes | Retry + Circuit Breaker |
| **Concurrency** | N real calls | 1 real call (Coalescing) |
| **Zero Visibility** | Blind operations | Structured JSON logs + OTEL |
| **Framework Lock-in** | Rewrite everything | Zero changes to core logic |
| **CLI Tools** | ❌ None | ✅ `toolops` CLI |

---

## v0.2.0 Highlights (Security & Architecture)

ToolOps v0.2.0 brings industrial-grade stability and security to the core:
- **Middleware Pipeline**: Replaced monolithic decorators with a modular, composable pipeline (`LoggingMiddleware`, `CacheMiddleware`, `CircuitBreakerMiddleware`, etc.).
- **Security Hardening**:
  - All cache keys are now **SHA-256 hashed** to prevent data leakage.
  - Automatic masking of sensitive keywords (e.g., `token`, `password`) in structured logs.
  - New `sensitive_params` parameter in all decorators to explicitly exclude fields from cache keys.
- **Docker Environment**: Quick local setup via `docker-compose up -d` with a pre-configured PostgreSQL instance.

---

## Installation

```bash
# Minimal install
pip install toolops

# With all features (Postgres, Semantic, OTEL)
pip install "toolops[all]"
```

---

## Core Concepts

### 1. Cache Backends

Register backends once at startup, then reference them by name in your decorators.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache

# Register memory as default
cache_manager.register("memory", MemoryCache(), is_default=True)
```

| Backend | Extra | Best for |
|---|---|---|
| `MemoryCache` | — | Dev / testing, single process |
| `PostgresCache` | `[postgres]` | Persistent cache, audit trail |
| `FileCache` | — | Lightweight local persistence |
| `SemanticCache` | `[semantic]` | NLP / RAG similarity matching |

---

### 2. Decorators

#### `@readonly(...)` — For reads with caching
```python
@readonly(cache_backend="memory", cache_ttl=3600, sensitive_params=["api_key"])
async def get_user_data(user_id: str, api_key: str) -> dict: ...
```

#### `@sideeffect(...)` — For writes (no caching, but has retries/timeout)
```python
@sideeffect(retry_count=3, circuit_breaker=True)
async def send_notification(msg: str) -> bool: ...
```

---

### 3. Resilience Features

ToolOps provides advanced resilience patterns to keep your agents running even when external services fail.

#### Circuit Breaker
Prevent cascading failures by stopping calls to failing services.
```python
@tool(circuit_breaker=True, circuit_failure_threshold=5, circuit_recovery_timeout=60)
async def external_api(): ...
```

#### Stale-if-Error
Serve expired cache data if the upstream tool call fails.
```python
@readonly(stale_if_error=True, stale_ttl=86400)
async def get_exchange_rates(): ...
```

---

### 4. Semantic Cache
Match queries by **meaning** using vector embeddings.
```python
from toolops.cache import SemanticCache, SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
semantic = SemanticCache(embedder=embedder, threshold=0.92)
cache_manager.register("semantic", semantic)

@readonly(cache_backend="semantic")
async def ask_agent(query: str): ...
```

---

## CLI & Operations

ToolOps includes a command-line tool to inspect and manage your tool infrastructure.

```bash
# See all available commands
toolops --help

# Check system health and backend readiness
toolops doctor

# View real-time cache statistics
toolops stats --app my_app:setup_toolops
```

---

## Framework Integration

ToolOps tools are plain Python functions and work natively with every major framework.

### Model Context Protocol (MCP)
Expose your tools to MCP-compatible hosts (like Claude Desktop) instantly.
```python
from toolops.integrations.mcp import MCPIntegration

# Get MCP-compatible tool definition
definition = MCPIntegration.to_mcp_definition(get_weather)
```

---

## Maintenance & Support

ToolOps is an open-source project by **Hedi MANAI**.

- **Website** [hedimanai.vercel.app](https://hedimanai.vercel.app/)
- **LinkedIn** [Hedi Manai Profile](https://www.linkedin.com/in/hedimanai/)
- **GitHub** [hedimanai-pro/toolops](https://github.com/hedimanai-pro/toolops)

---

## License

Apache License 2.0 — Copyright 2026 Hedi Manai.