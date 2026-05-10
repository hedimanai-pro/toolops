<div align="center">

<img src="docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### The Industrial-Grade Resilience & Efficiency Layer for AI Agent Tools

[![PyPI version](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![License](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Build production-ready AI agents. Stop writing infrastructure boilerplate.**

[Website](https://hedimanai.vercel.app/) · [Documentation](https://hedimanai.vercel.app/projects/toolops.html) · [Quickstart](#quickstart) · [Changelog](CHANGELOG.md)

</div>

---

## What is ToolOps?

> **"ToolOps is to AI Tools what a Service Mesh is to Microservices."**

When you build AI agents, every external call — to an LLM, an API, a database — is a tool call. In production, those calls are **expensive**, **unreliable**, and **slow**. Yet most developers handle this by re-writing the same boilerplate across every project: a cache class here, a retry decorator there, a circuit-breaker wrapper somewhere else.

**ToolOps eliminates that entirely.** It is a framework-agnostic middleware SDK that wraps any Python function in a single decorator and upgrades it with caching, resilience, observability, and concurrency control — with zero changes to your business logic.

```python
# Before ToolOps: 80+ lines of cache managers, retry logic, circuit breakers...
# After ToolOps:

@readonly(cache_backend="fast", cache_ttl=3600, retry_count=3)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)  # Automatically cached, retried, and traced
```

That's it. One line. Production-ready.

---

## The Production Wall

Every agent developer hits the same wall when moving from demo to production:

| Problem | Business Impact | Without ToolOps | With ToolOps |
| :--- | :--- | :--- | :--- |
| **Redundant API calls** | 💸 10× cost spikes | 100 calls = 100 credits | 100 calls → 1 real + 99 cache hits |
| **Similar queries** | 💸 LLM tokens wasted | Treated as unique | Semantic match → same result |
| **API instability** | 💥 Agent crashes & loops | No protection | Circuit Breaker + auto-retry |
| **Concurrency bursts** | 🐢 Thundering herd | N identical live calls | Request coalescing → 1 real call |
| **Zero observability** | 🌑 Blind operations | No insight | Structured JSON + OTEL traces |
| **Framework lock-in** | 🧩 Rewrites on migration | Coupled to one framework | Universal Python decorator |

---

## Feature Overview

| Feature | Standard `@lru_cache` | ToolOps |
| :--- | :---: | :---: |
| Async / `await` support | ❌ | ✅ Native |
| Semantic (meaning-aware) cache | ❌ | ✅ Embeddings |
| Exact-match cache | ✅ (in-memory only) | ✅ Memory, Postgres, File |
| Distributed / persistent cache | ❌ | ✅ Postgres (Redis coming) |
| Circuit Breaker | ❌ | ✅ |
| Automatic retries | ❌ | ✅ With backoff |
| Request coalescing | ❌ | ✅ |
| Stale-if-error fallback | ❌ | ✅ |
| OpenTelemetry tracing | ❌ | ✅ |
| Prometheus metrics | ❌ | ✅ |
| CLI management tools | ❌ | ✅ |
| AI-native (MCP / LangChain / CrewAI) | ❌ | ✅ |

---

## Prerequisites

Before installing ToolOps, make sure you have:

- **Python 3.9 or higher** — check with `python --version`
- **pip 21.0 or higher** — check with `pip --version`
- A working Python environment (virtual environment strongly recommended — see below)

> **New to virtual environments?** See the [Virtual Environment Setup](#virtual-environment-setup) section below — it takes 30 seconds and avoids a lot of pain.

---

## Installation

ToolOps uses a modular install system. The core package has **zero external dependencies**. You only install what you need.

### Quick reference

| Install command | What you get | Use when |
| :--- | :--- | :--- |
| `pip install toolops` | Core SDK only | Starting out, no extras needed |
| `pip install "toolops[postgres]"` | + PostgreSQL cache backend | Persistent/distributed cache |
| `pip install "toolops[semantic]"` | + Semantic cache support | NLP/RAG similarity matching |
| `pip install "toolops[otel]"` | + OpenTelemetry tracing | Production observability |
| `pip install "toolops[all]"` | Everything above | Full feature set |

---

### Platform-specific install commands

> **Important:** The `[extras]` syntax requires quotes on Linux and macOS because shells like `bash` and `zsh` treat square brackets as glob patterns. Windows CMD and PowerShell use double quotes.

#### 🐧 Linux / 🍎 macOS (bash, zsh, sh)

```bash
# Core only (no extras, no quotes needed)
pip install toolops

# Recommended: full install with all features
pip install "toolops[all]"

# Individual extras (examples)
pip install "toolops[postgres]"
pip install "toolops[semantic]"
pip install "toolops[otel]"

# Combine multiple extras
pip install "toolops[postgres,semantic,otel]"
```

#### 🪟 Windows (Command Prompt or PowerShell)

```cmd
# Core only
pip install toolops

# Recommended: full install with all features
pip install "toolops[all]"

# Individual extras
pip install "toolops[postgres]"
pip install "toolops[semantic]"
pip install "toolops[otel]"

# Combine multiple extras
pip install "toolops[postgres,semantic,otel]"
```

> **Windows note:** Both CMD and PowerShell accept double-quoted package specifiers. Single quotes (`'`) do **not** work in CMD — use double quotes only.

#### Alternative: using `python -m pip` (all platforms)

This form is more explicit and avoids PATH confusion, especially when you have multiple Python versions installed:

```bash
# Linux / macOS
python -m pip install "toolops[all]"

# Windows
py -m pip install "toolops[all]"
```

---

### Virtual environment setup

We strongly recommend isolating your project in a virtual environment before installing ToolOps.

#### Linux / macOS

```bash
# Create a virtual environment
python -m venv .venv

# Activate it
source .venv/bin/activate

# Install ToolOps
pip install "toolops[all]"

# Verify installation
toolops --version
```

#### Windows (Command Prompt)

```cmd
:: Create a virtual environment
python -m venv .venv

:: Activate it
.venv\Scripts\activate.bat

:: Install ToolOps
pip install "toolops[all]"

:: Verify installation
toolops --version
```

#### Windows (PowerShell)

```powershell
# Create a virtual environment
python -m venv .venv

# Activate it
.venv\Scripts\Activate.ps1

# Install ToolOps
pip install "toolops[all]"

# Verify installation
toolops --version
```

> **PowerShell note:** If you see an execution policy error, run:
> `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser`

---

### Verify your installation

After installing, confirm everything is working:

```bash
# Check CLI is available
toolops --version

# Run a system health check (checks all registered backends)
toolops doctor
```

Expected output from `toolops doctor`:

```
✔ ToolOps core        OK
✔ MemoryCache         OK
✔ PostgresCache       Connected (postgresql://localhost:5432/...)
✔ SemanticCache       OK (model: all-MiniLM-L6-v2)
✔ OpenTelemetry       Exporter configured
```

---

## Quickstart

This minimal example gets you from install to a working, cached, resilient tool in under 2 minutes.

```python
import asyncio
from toolops import readonly, sideeffect, cache_manager
from toolops.cache import MemoryCache

# Step 1: Register a cache backend (do this once at startup)
cache_manager.register("memory", MemoryCache(), is_default=True)

# Step 2: Decorate any async function with @readonly for read operations
# This adds: automatic caching (1 hour TTL) + 3 retries on failure
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simulate an external API call
    # In production, replace with your real API client
    return {"city": city, "temp": 22, "condition": "sunny"}

# Step 3: Decorate write operations with @sideeffect (no caching, but protected)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Simulate sending a notification
    print(f"Alert sent: {message}")
    return True

async def main():
    # First call hits the API
    result = await fetch_weather("Paris")
    print(f"First call (live): {result}")

    # Second call is served from cache — no API call made
    result = await fetch_weather("Paris")
    print(f"Second call (cached): {result}")

    # Write operation with circuit breaker protection
    await send_alert("Agent completed successfully.")

asyncio.run(main())
```

**What you get with zero extra configuration:**
- ✅ `fetch_weather("Paris")` is cached for 1 hour — subsequent calls return instantly
- ✅ If the API fails, it retries up to 3 times automatically
- ✅ `send_alert` is protected by a circuit breaker — it won't hammer a failing service
- ✅ Every call is logged as structured JSON — ready for your log aggregator

---

## Core Concepts

### 1. Cache Backends

Register backends once at application startup, then reference them by name in any decorator. ToolOps supports multiple backends simultaneously — for example, a fast in-memory cache for hot data and a persistent Postgres cache for expensive computations.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache

# In-memory: fastest, cleared on restart, no dependencies
cache_manager.register("memory", MemoryCache(), is_default=True)

# Postgres: persistent across restarts, shareable across processes
# Requires: pip install "toolops[postgres]"
cache_manager.register(
    "db",
    PostgresCache(connection_string="postgresql://user:pass@localhost:5432/mydb"),
)

# File-based: lightweight persistence without a database
cache_manager.register("disk", FileCache(directory="/tmp/toolops-cache"))
```

**Backend comparison:**

| Backend | Speed | Persistence | Multi-process | When to use |
| :--- | :--- | :--- | :--- | :--- |
| `MemoryCache` | ⚡ Fastest | ❌ Lost on restart | ❌ Single process | Dev, testing, single-instance apps |
| `FileCache` | 🐇 Fast | ✅ Survives restarts | ⚠️ Read-safe | Local scripts, prototyping |
| `PostgresCache` | 🐢 Moderate | ✅ Durable | ✅ Fully shared | Production, microservices, audit trails |
| `SemanticCache` | 🐢 Moderate | Depends on backend | Depends | NLP queries, RAG pipelines |

> **Tip:** You can register as many backends as you need. Use the `cache_backend=` parameter on each decorator to choose which one a specific function uses.

---

### 2. The `@readonly` Decorator

Use `@readonly` for any function that **reads** data and has no side effects: API lookups, database queries, LLM calls, file reads. It adds caching and retries.

```python
from toolops import readonly

@readonly(
    cache_backend="memory",   # Which registered backend to use
    cache_ttl=3600,           # Cache Time-to-Live in seconds (1 hour)
    retry_count=3,            # Number of retry attempts on failure
    timeout=10.0,             # Max seconds to wait per attempt
    stale_if_error=True,      # Serve stale cache if the live call fails
    stale_ttl=86400,          # How long stale data is acceptable (24h)
)
async def get_stock_price(ticker: str) -> dict:
    return await market_api.fetch(ticker)
```

**How caching works under the hood:**

1. ToolOps hashes the function name + arguments into a cache key
2. On each call, it checks the cache first
3. **Cache hit** → return the stored result immediately (no API call)
4. **Cache miss** → call the real function, store the result, return it
5. If the real function fails, `stale_if_error=True` serves the last known good value

---

### 3. The `@sideeffect` Decorator

Use `@sideeffect` for any function that **writes** data or triggers an action: sending emails, executing trades, posting messages, modifying state. Side effects are **never cached** (calling the same function twice should produce two real effects), but they are protected by retries and circuit breakers.

```python
from toolops import sideeffect

@sideeffect(
    circuit_breaker=True,              # Enable circuit breaker protection
    circuit_failure_threshold=5,       # Open circuit after 5 consecutive failures
    circuit_recovery_timeout=60,       # Try recovery after 60 seconds
    retry_count=3,                     # Retry on transient failures
    timeout=5.0,                       # Timeout per attempt in seconds
)
async def execute_trade(order: dict) -> dict:
    return await broker_api.submit(order)
```

> **When to use which decorator:**
> - Does the function have an observable side effect (writes, sends, modifies)? → `@sideeffect`
> - Is the function purely reading/querying with the same input always producing the same output? → `@readonly`

---

### 4. Resilience Patterns

#### Circuit Breaker

A circuit breaker prevents your agent from hammering a failing service and causing cascading failures. When a service fails repeatedly, the circuit "opens" and all calls fail fast — until the service recovers.

```
Normal state (Closed) → Too many failures → Circuit opens (Open)
         ↑                                          ↓
         └─────────── Recovery timeout ─────────────┘
                      (Half-Open probe)
```

```python
@sideeffect(
    circuit_breaker=True,
    circuit_failure_threshold=5,   # Open after 5 failures in a row
    circuit_recovery_timeout=60,   # Wait 60s before probing the service again
)
async def call_payment_api(payload: dict) -> dict:
    return await payment_service.process(payload)
```

#### Stale-if-Error

When a live API call fails, instead of raising an exception, ToolOps serves the last known good cached value. Useful for data that changes slowly (exchange rates, configuration, metadata).

```python
@readonly(
    cache_backend="db",
    cache_ttl=3600,         # Normally refresh every hour
    stale_if_error=True,
    stale_ttl=86400,        # But accept data up to 24h old if API is down
)
async def get_exchange_rates(base: str = "USD") -> dict:
    return await forex_api.fetch(base)
```

#### Request Coalescing

If 50 agents call `get_stock_price("AAPL")` simultaneously during a cache miss, ToolOps executes the real API call **once** and multicasts the result to all 50 callers. Without this, a cache miss under load can cause a thundering herd that overwhelms your API rate limits.

```python
# Coalescing is automatic when you use @readonly.
# All concurrent callers with the same arguments wait for a single execution.
@readonly(cache_backend="memory", cache_ttl=60)
async def get_stock_price(ticker: str) -> dict:
    return await market_api.fetch(ticker)
    # 50 concurrent calls for "AAPL" → 1 real API call, 49 coalesced responses
```

---

### 5. Semantic Cache

The standard cache only matches **exact** inputs — `"weather in Paris"` and `"Paris weather"` are treated as different keys. The Semantic Cache uses vector embeddings to match by **meaning**, not by string equality. If the semantic similarity between two queries exceeds a configurable threshold, they share the same cached result.

**Requires:** `pip install "toolops[semantic]"`

```python
from toolops import readonly, cache_manager
from toolops.cache import SemanticCache, SentenceTransformerEmbedder

# Initialize the embedder (downloads model on first run, ~90MB)
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")

# Create a semantic cache with a similarity threshold of 0.92
# (1.0 = identical, 0.0 = completely different — 0.92 is a good default)
semantic_cache = SemanticCache(embedder=embedder, threshold=0.92)
cache_manager.register("semantic", semantic_cache)

@readonly(cache_backend="semantic")
async def answer_question(query: str) -> str:
    return await llm.complete(query)

# Example — these two calls share the same cache entry:
r1 = await answer_question("What's the weather in Paris?")
r2 = await answer_question("How's the weather in Paris today?")  # Cache hit ✅
r3 = await answer_question("What is the Parisian weather like?")  # Cache hit ✅

# This is a different enough query to miss:
r4 = await answer_question("What's the temperature on the Moon?")  # Cache miss ✅
```

> **Performance note:** Semantic cache adds ~5–20ms of embedding inference per call (for the query vector). The first run downloads the model weights (~90MB). Subsequent runs load from disk in milliseconds. The payoff: up to 90% reduction in LLM calls for agents that handle natural language queries.

---

## Observability

ToolOps instruments every tool call automatically. You don't need to add logging — it's built in.

### Structured JSON Logging

Every cache hit, miss, retry, circuit-breaker event, and timeout is logged as structured JSON, ready for any log aggregator (Datadog, Loki, CloudWatch, etc.).

```json
{"event": "cache_hit",   "fn": "get_stock_price", "backend": "memory", "ttl_remaining": 2847, "latency_ms": 0.4}
{"event": "cache_miss",  "fn": "get_stock_price", "backend": "memory", "latency_ms": 142.7}
{"event": "retry",       "fn": "execute_trade",   "attempt": 2, "error": "ConnectionTimeout", "latency_ms": 5002}
{"event": "circuit_open","fn": "call_payment_api","failures": 5, "recovery_in": 60}
```

### OpenTelemetry (OTEL) Tracing

**Requires:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel

# Point at any OTEL-compatible backend
configure_otel(
    service_name="my-agent",
    exporter_endpoint="http://localhost:4317",  # Jaeger, Honeycomb, Datadog, etc.
)

# From this point, every @readonly and @sideeffect call emits a span
# with attributes: fn_name, cache_status, retry_count, latency_ms
```

You'll see spans like this in Jaeger or Honeycomb:

```
agent_run (450ms)
  ├── get_market_data (12ms)  [cache: hit]
  ├── get_news_feed (310ms)   [cache: miss, retries: 1]
  └── send_report (128ms)     [circuit: closed]
```

### Prometheus Metrics

**Requires:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_prometheus

configure_prometheus(port=8000)
# Metrics available at http://localhost:8000/metrics
```

Key metrics exposed:

| Metric | Type | Description |
| :--- | :--- | :--- |
| `toolops_cache_hits_total` | Counter | Total cache hits by function + backend |
| `toolops_cache_misses_total` | Counter | Total cache misses |
| `toolops_tool_latency_seconds` | Histogram | Per-function execution time distribution |
| `toolops_retries_total` | Counter | Total retry attempts by function |
| `toolops_circuit_opens_total` | Counter | Total circuit breaker open events |

---

## Framework Integration

ToolOps decorates plain Python async functions, so it works with any agent framework without modification. Below are integration patterns for the most common frameworks.

### LangChain / LangGraph

```python
from langchain.tools import tool
from toolops import readonly, cache_manager
from toolops.cache import MemoryCache

cache_manager.register("memory", MemoryCache(), is_default=True)

# Decorate before @tool — ToolOps wraps the raw function
@tool
@readonly(cache_backend="memory", cache_ttl=600, retry_count=3)
async def search_web(query: str) -> str:
    """Search the web and return a summary."""
    return await web_search_api.run(query)

# Use in your LangGraph agent as normal
# Every call to search_web is now automatically cached and retried
```

### CrewAI

```python
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from toolops import readonly, cache_manager
from toolops.cache import PostgresCache

cache_manager.register(
    "db",
    PostgresCache(connection_string="postgresql://..."),
    is_default=True,
)

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Fetches and caches research data."

    @readonly(cache_backend="db", cache_ttl=3600, retry_count=3)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)

researcher = Agent(
    role="Researcher",
    tools=[ResearchTool()],
    # ...
)
```

### LlamaIndex

```python
from llama_index.core.tools import FunctionTool
from toolops import readonly, cache_manager
from toolops.cache import SemanticCache, SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))

@readonly(cache_backend="semantic")
async def query_knowledge_base(question: str) -> str:
    return await vector_store.query(question)

knowledge_tool = FunctionTool.from_defaults(async_fn=query_knowledge_base)
```

### Model Context Protocol (MCP)

ToolOps has built-in support for MCP. Expose any decorated function as an MCP tool — compatible with Claude Desktop, Cursor, and any MCP-compatible host — without writing JSON schema by hand.

```python
from toolops import readonly, cache_manager
from toolops.cache import MemoryCache
from toolops.integrations.mcp import MCPIntegration

cache_manager.register("memory", MemoryCache(), is_default=True)

@readonly(cache_backend="memory", cache_ttl=600, retry_count=2)
async def get_weather(city: str) -> dict:
    """Get current weather for a city."""
    return await weather_api.fetch(city)

# Generate a fully typed MCP tool definition automatically
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
# Returns: {"name": "get_weather", "description": "...", "inputSchema": {...}}

# Register with your MCP server
mcp_server.register_tool(mcp_definition)
```

---

## CLI Reference

ToolOps ships with a command-line tool for managing and inspecting your tool infrastructure.

```bash
# Display all available commands and options
toolops --help

# Check the health of all registered backends
toolops doctor

# View live cache statistics for an app
# Replace 'my_app:setup_toolops' with your module:function path
toolops stats --app my_app:setup_toolops

# Clear a specific backend's cache
toolops clear memory --app my_app:setup_toolops
toolops clear postgres --app my_app:setup_toolops

# Clear all backends
toolops clear all --app my_app:setup_toolops
```

**Example output of `toolops stats`:**

```
Backend: memory
  Hit rate:       87.3%
  Total hits:     12,481
  Total misses:   1,814
  Avg latency:    0.3ms

Backend: postgres
  Hit rate:       94.1%
  Total hits:     8,320
  Total misses:   492
  Avg latency:    4.1ms
  Oldest entry:   2026-05-08 09:41:22
```

---

## Configuration Reference

### `@readonly` — all parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `cache_backend` | `str` | `"default"` | Name of the registered backend to use |
| `cache_ttl` | `int` | `300` | Cache Time-to-Live in seconds |
| `retry_count` | `int` | `0` | Number of retry attempts on exception |
| `retry_delay` | `float` | `1.0` | Base delay (seconds) between retries (exponential backoff) |
| `timeout` | `float` | `None` | Max execution time in seconds per attempt |
| `stale_if_error` | `bool` | `False` | Serve stale cache if the live call fails |
| `stale_ttl` | `int` | `None` | Max age (seconds) of stale data to serve on error |
| `circuit_breaker` | `bool` | `False` | Enable circuit breaker |
| `circuit_failure_threshold` | `int` | `5` | Failures before circuit opens |
| `circuit_recovery_timeout` | `int` | `60` | Seconds before attempting recovery |

### `@sideeffect` — all parameters

| Parameter | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| `retry_count` | `int` | `0` | Number of retry attempts |
| `retry_delay` | `float` | `1.0` | Base delay between retries |
| `timeout` | `float` | `None` | Max execution time per attempt |
| `circuit_breaker` | `bool` | `False` | Enable circuit breaker |
| `circuit_failure_threshold` | `int` | `5` | Failures before circuit opens |
| `circuit_recovery_timeout` | `int` | `60` | Seconds before attempting recovery |

---

## Ecosystem Compatibility

ToolOps is designed as framework-agnostic middleware — the "glue layer" of any Python-based agent stack.

#### First-class integrations (built-in helpers)

- **LangChain** / **LangGraph** — decorator-compatible with `@tool`
- **CrewAI** — compatible with `BaseTool._run()`
- **LlamaIndex** — compatible with `FunctionTool`
- **Model Context Protocol (MCP)** — `MCPIntegration.to_mcp_definition()`

#### General compatibility

Works with any framework that calls Python async functions:

- **PydanticAI**
- **AutoGPT**
- **Haystack**
- **Agno**
- Any custom function-based agent

> **Note:** ToolOps wraps the raw function. Apply the ToolOps decorator **before** any framework-specific decorator (e.g., `@tool` goes on top of `@readonly`), so the framework receives the fully-instrumented function.

---

## Common Patterns

### Pattern 1: Multi-backend strategy (hot + cold cache)

```python
from toolops import readonly, cache_manager
from toolops.cache import MemoryCache, PostgresCache

# Hot cache: in-memory, very fast, short TTL
cache_manager.register("hot", MemoryCache())

# Cold cache: persistent, shared across processes, longer TTL
cache_manager.register(
    "cold",
    PostgresCache(connection_string="postgresql://..."),
    is_default=True,
)

# Frequently accessed, low-latency need → hot cache
@readonly(cache_backend="hot", cache_ttl=60)
async def get_user_session(user_id: str) -> dict: ...

# Expensive computation, less frequent → cold cache
@readonly(cache_backend="cold", cache_ttl=86400)
async def generate_monthly_report(user_id: str) -> dict: ...
```

### Pattern 2: Full production setup

```python
# app/toolops_setup.py

from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, SemanticCache, SentenceTransformerEmbedder
from toolops.observability import configure_otel, configure_prometheus
import os

def setup_toolops():
    """Call this once at application startup."""

    # Register cache backends
    cache_manager.register("memory", MemoryCache(), is_default=True)
    cache_manager.register(
        "db",
        PostgresCache(connection_string=os.environ["DATABASE_URL"]),
    )

    embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
    cache_manager.register(
        "semantic",
        SemanticCache(embedder=embedder, threshold=0.92),
    )

    # Configure observability
    configure_otel(
        service_name=os.environ.get("SERVICE_NAME", "my-agent"),
        exporter_endpoint=os.environ.get("OTEL_ENDPOINT", "http://localhost:4317"),
    )
    configure_prometheus(port=int(os.environ.get("METRICS_PORT", "8000")))
```

### Pattern 3: Protecting expensive LLM calls

```python
from toolops import readonly, cache_manager
from toolops.cache import SemanticCache, SentenceTransformerEmbedder

embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register(
    "semantic",
    SemanticCache(embedder=embedder, threshold=0.90),
    is_default=True,
)

@readonly(
    cache_backend="semantic",
    cache_ttl=7200,       # 2-hour TTL for semantic results
    retry_count=3,        # Retry on rate limits or transient failures
    timeout=30.0,         # LLM calls can be slow
    stale_if_error=True,  # Return last known answer if the LLM is down
    stale_ttl=3600,       # Accept 1-hour-old answers as fallback
)
async def ask_llm(prompt: str) -> str:
    return await openai_client.chat(prompt)

# These three calls result in only ONE real LLM call:
a = await ask_llm("Summarize the latest news about AI")
b = await ask_llm("Give me a summary of recent AI news")       # Cache hit ✅
c = await ask_llm("What's happening in AI recently?")           # Cache hit ✅
```

---

## Troubleshooting

### `zsh: no matches found: toolops[all]`

You're on macOS/Linux and forgot the quotes. Use:
```bash
pip install "toolops[all]"
```

### `ModuleNotFoundError: No module named 'toolops.cache.postgres'`

You installed the core package without the Postgres extra. Run:
```bash
pip install "toolops[postgres]"
```

### `toolops doctor` shows a backend as `FAILED`

Common causes:
- **PostgresCache**: Check your connection string and that the Postgres server is running and reachable
- **SemanticCache**: The sentence-transformer model may not have downloaded yet — run a quick test call to trigger the download
- **OTEL**: Verify your exporter endpoint is reachable from your machine

### Retries are not triggering

`retry_count` only retries on `Exception` subclasses. If your function catches exceptions internally and returns an error dict instead of raising, ToolOps won't see the failure. Make sure your tool functions raise on error.

### Cache is not persisting between restarts

You're likely using `MemoryCache`. Switch to `PostgresCache` or `FileCache` for persistence across process restarts.

---

## Roadmap

- [ ] **Web Dashboard** — Real-time cache hit rates, cost attribution, and tool latency UI
- [ ] **Budget Control** — Hard limits on API costs per tool per hour/day
- [ ] **Native MCP Server** — One-command deployment of ToolOps tools as a standalone MCP host
- [ ] **Streaming Middleware** — Support for streaming tool outputs in real-time agents
- [ ] **Redis Backend** — High-performance distributed caching for microservice architectures
- [ ] **MariaDB / ChromaDB / Pinecone** — Additional cache backends
- [ ] **Async Dashboard CLI** — Live `top`-style monitoring of tool calls

---

## Contributing

Contributions, bug reports, and feature requests are welcome!

1. Fork the repository: [github.com/hedimanai-pro/toolops](https://github.com/hedimanai-pro/toolops)
2. Create a feature branch: `git checkout -b feature/my-improvement`
3. Make your changes and add tests
4. Submit a pull request with a clear description

For larger changes, please open an issue first to discuss the approach.

---

## Support & Community

ToolOps is built and maintained by **Hedi MANAI**.

| Channel | Link |
| :--- | :--- |
| 🐛 **Bug Reports / Feature Requests** | [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues) |
| 💼 **LinkedIn** | [linkedin.com/in/hedimanai](https://www.linkedin.com/in/hedimanai/) |
| 🐦 **X (Twitter)** | [@hedi_manaii](https://x.com/hedi_manaii) |
| 🌐 **Website** | [hedimanai.vercel.app](https://hedimanai.vercel.app/) |
| 📦 **PyPI** | [pypi.org/project/toolops](https://pypi.org/project/toolops/) |
| 📧 **Email** | [hedi.manai.pro@gmail.com](mailto:hedi.manai.pro@gmail.com) |
| 💬 **Discord** | `@hedimanai` |

---

## License

Distributed under the **Apache License 2.0**. See [LICENSE](LICENSE) for full details.

You are free to use, modify, and distribute ToolOps in personal and commercial projects.

---

<div align="center">

Built with ❤️ by <b>Hedi MANAI</b>

<i>Empowering the next generation of production-ready agentic workflows.</i>

<br><br>

<a href="https://github.com/hedimanai-pro/toolops">⭐ Star on GitHub</a> · <a href="https://pypi.org/project/toolops/">📦 PyPI</a> · <a href="https://hedimanai.vercel.app/projects/toolops.html">📖 Docs</a>

</div>