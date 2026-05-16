<div align="center">

[🇬🇧 English](README.md) | [🇫🇷 Français](readme/README.fr.md) | [🇨🇳 中文](readme/README.zh.md) | [🇯🇵 日本語](readme/README.ja.md) | [🇪🇸 Español](readme/README.es.md) | [🇩🇪 Deutsch](readme/README.de.md) | [🇵🇹 Português](readme/README.pt.md) | [🇰🇷 한국어](readme/README.ko.md) | [🇷🇺 Русский](readme/README.ru.md) | [🇮🇳 हिन्दी](readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### The Industrial-Grade Resilience & Efficiency Layer for AI Agent Tools

[![PyPI version](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Tests](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Coverage](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI Downloads](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![License](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Build production-ready AI agents. Stop writing infrastructure boilerplate.**

[Website](https://hedimanai.vercel.app/) · [Documentation](https://hedimanai.vercel.app/projects/toolops.html) · [Quickstart](#quickstart) · [Changelog](CHANGELOG.md)

</div>

---

## ⚡ 30-Second Pitch

> **"ToolOps is to AI Tools what a Service Mesh is to Microservices."**

When you build AI agents, external calls (LLMs, APIs, DBs) are **expensive**, **unreliable**, and **slow**.
ToolOps eliminates the boilerplate. It is a framework-agnostic middleware SDK that wraps any Python function in a single decorator, instantly upgrading it with caching, resilience, observability, and concurrency control.

```python
# BEFORE ToolOps: 80+ lines of cache managers, retry logic, circuit breakers...

# AFTER ToolOps:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Automatically cached, retried, and traced
```

### 🚀 Benchmarks & Impact
- **90% reduction in LLM calls** via Semantic Caching.
- **<5ms overhead** per tool call execution.
- **0 code changes** to your core business logic.

---

## ⚖️ Why ToolOps?

Every agent developer hits a wall when moving from demo to production. Here is how ToolOps compares to standard alternatives:

| Feature | Standard `@lru_cache` | Framework-Native | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **Async / `await` support** | ❌ | ✅ | ✅ Native |
| **Semantic (meaning-aware) cache** | ❌ | ⚠️ Basic | ✅ Advanced Embeddings |
| **Distributed / Persistent cache** | ❌ | ⚠️ Varies | ✅ Postgres, File |
| **Circuit Breaker** | ❌ | ❌ | ✅ Native |
| **Automatic Retries w/ Backoff** | ❌ | ⚠️ Plugin required | ✅ Native |
| **Request Coalescing (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Native |
| **Stale-if-error Fallback** | ❌ | ❌ | ✅ Native |
| **Security (SHA-256 keys, Auto-masking)**| ❌ | ❌ | ✅ Native |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Callbacks needed | ✅ Native |
| **Framework Agnostic** | ✅ | ❌ Locked-in | ✅ 100% Universal |

---

## 📦 Installation

ToolOps uses a modular install system. The core package has **zero external dependencies**. You only install what you need.

### Quick Reference

| Install command | What you get | Use when |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | Full feature set | **Recommended for production** |
| `pip install toolops` | Core SDK only | Starting out, no extras needed |

### 💻 OS-Specific Guides

We strongly recommend isolating your project in a virtual environment.

#### 🐧 Linux & 🍎 macOS
```bash
# 1. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate

# 2. Install ToolOps (quotes are required for bash/zsh)
pip install "toolops[all]"

# 3. Verify installation
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Install ToolOps
pip install "toolops[all]"

# 3. Verify installation
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. Install ToolOps (use double quotes)
pip install "toolops[all]"

:: 3. Verify installation
toolops doctor
```

---

## 🚀 Quickstart

This minimal example gets you from install to a working, cached, resilient tool in under 2 minutes.

```python
# Imports
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Step 1: Register a cache backend (do this once at startup)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Step 2: Decorate any async function with @readonly for read operations
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simulate an external API call
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

    # Second call is served from cache — <5ms latency, 0 API calls
    result = await fetch_weather("Paris")
    print(f"Second call (cached): {result}")

    # Write operation with circuit breaker protection
    await send_alert("Agent completed successfully.")

asyncio.run(main())
```

---

## 🧠 Core Concepts

### 1. Cache Backends

Register backends once at application startup, then reference them by name. ToolOps supports multiple backends simultaneously.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# In-memory: fastest, cleared on restart, no dependencies
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres: persistent across restarts, shareable across processes
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Semantic: vector embeddings to match by meaning, not string equality
# Reduces LLM calls up to 90%
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. Resilience Patterns

ToolOps provides robust, battle-tested resilience out of the box.

- **Circuit Breaker**: Prevents hammering a failing service and causing cascading failures.
- **Stale-if-Error**: Serves the last known good cached value if the live API call fails.
- **Request Coalescing**: If 50 agents call the same endpoint simultaneously, ToolOps executes the real API call **once** and multicasts the result.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Fallback on API failure
    circuit_breaker = True      # Protect the underlying service
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Architecture & Security (v0.2.0)

ToolOps v0.2.0 introduces an enterprise-grade architecture:

- **Middleware Pipeline**: The monolithic decorator has been refactored into a composable pipeline (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`).
- **SHA-256 Cache Key Hashing**: All cache keys are strictly hashed. No sensitive data (tokens, PII) is exposed in cache stores.
- **Automatic Parameter Masking**: Tool arguments containing sensitive keywords (`token`, `password`, `secret`, etc.) are automatically masked as `***MASKED***` in structured logs.

---

## 📊 Observability

ToolOps instruments every tool call automatically.

### OpenTelemetry (OTEL) & Prometheus

**Requires:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# Point at any OTEL-compatible backend (Jaeger, Datadog, Honeycomb, etc.)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Expose Prometheus metrics
configure_prometheus(port=8000)
```

Key metrics exposed include `toolops_cache_hits_total`, `toolops_tool_latency_seconds`, and `toolops_circuit_opens_total`.

---

## 🔌 Framework Integration

ToolOps decorates plain Python async functions, making it **100% compatible** with your favorite agent frameworks.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Search the web and return a summary."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Fetches and caches research data."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Generate a fully typed MCP tool definition automatically
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ CLI Reference

ToolOps ships with a command-line tool for managing your cache infrastructure.

```bash
# Check the health of all registered backends
toolops doctor

# View live cache statistics for an app
toolops stats --app my_app:setup_toolops

# Clear a specific backend's cache
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Contributing

ToolOps is built for the community, by the community. 

- Review our [Contributing Guide](CONTRIBUTING.md) to get started.
- Check out the [Code of Conduct](CODE_OF_CONDUCT.md).
- Report security issues safely via our [Security Policy](SECURITY.md).

---

## 💬 Community & Contact

We are actively building the future of AI Agent infrastructure. Join the discussion!

- **Creator:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Report Bugs & Feature Requests:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **Email:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Built for Production.</b><br>
Licensed under <a href="LICENSE">Apache 2.0</a>
</div>