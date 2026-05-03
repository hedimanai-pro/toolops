<div align="center">

<img src="docs/assets/logo.png" width="200" alt="ToolOps Logo">

# ToolOps
### The Industrial-Grade Resilience & Efficiency Layer for AI Agent Tools

[![PyPI version](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![License](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Build Production-Ready Agents. Stop Writing Infrastructure Boilerplate.**

[Website](https://hedimanai.vercel.app/) · [Documentation](https://hedimanai.vercel.app/projects/toolops.html) · [Quickstart](#quickstart) · [Changelog](CHANGELOG.md)

</div>

---

## Philosophy

AI Agents are only as reliable as the tools they wield. In production, tools are **expensive**, **unreliable**, and **slow**. 

**ToolOps** is a framework-agnostic middleware SDK that treats every tool call as a first-class operation. By wrapping your tools in a single decorator, you instantly upgrade them with industrial-grade caching, resilience, and observability.

> **"ToolOps is to AI Tools what Service Mesh is to Microservices."**

---

| Feature | Standard `@lru_cache` | ToolOps SDK |
| :--- | :--- | :--- |
| **Async Support** | ❌ No | ✅ Native |
| **Semantic Cache** | ❌ No | ✅ Yes (Embeddings) |
| **Resilience** | ❌ No | ✅ Circuit Breaker / Retries |
| **Distributed** | ❌ No | ✅ Postgres (S3 / Redis coming) |
| **Observability** | ❌ No | ✅ OTEL / Prometheus |
| **AI Native** | ❌ No | ✅ MCP / LangChain / LangGraph / CrewAI etc. Ready |

---

## The Production Wall

Every agent developer hits the same wall when moving from demo to production:

| The Problem | The Business Impact | The ToolOps Fix |
| :--- | :--- | :--- |
| **Redundant Calls** | 💸 Skyrocketing API costs | **Semantic Cache** (1 call, 99 hits) |
| **API Instability** | 💥 Agent crashes & loops | **Circuit Breaker & Retries** |
| **Concurrency** | 🐢 Bottlenecks on shared tools | **Request Coalescing** |
| **Observability** | 🌑 Blind operations | **Native OTEL & JSON Logging** |
| **Standardization** | 🧩 Framework lock-in | **Universal Decorator** |

---

## Quickstart

Install the SDK (Core is zero-dependency):
```bash
pip install toolops[all]
```

Supercharge your tools in seconds:

```python
from toolops import readonly, sideeffect, cache_manager
from toolops.cache import MemoryCache, PostgresCache

# 1. Plug-and-play Backends
cache_manager.register("fast", MemoryCache(), is_default=True)

# 2. Add Intelligence & Resilience to any function
@readonly(cache_backend="fast", cache_ttl=3600, retry_count=3)
async def get_market_data(ticker: str):
    return await api.fetch(ticker) # Automatically cached & retried

@sideeffect(circuit_breaker=True, timeout=5.0)
async def execute_trade(order: dict):
    return await broker.submit(order) # Protected by Circuit Breaker
```

---

## Engineering Features

### Semantic Caching
Don't just cache exact strings. ToolOps uses vector embeddings to understand the **meaning** of a query. If an agent asks "How's the weather in Paris?" and then "What is the Parisian weather like?", ToolOps serves the cached result.
*Reduces LLM latency by up to 90%.*

### Industrial Resilience
- **Circuit Breakers**: Stop pounding failing APIs before they take down your system.
- **Stale-if-Error**: If an upstream API fails, ToolOps can automatically serve the last known good value from the cache.
- **Request Coalescing**: If 50 agents call the same tool simultaneously, ToolOps executes it **once** and multicasts the result.

### MCP Integration (Model Context Protocol)
ToolOps is "AI-Native". It includes built-in support for **MCP**, allowing you to instantly expose your decorated tools to **Claude Desktop**, **Cursor**, or any MCP-compatible host without writing a single line of JSON Schema.

---

## Ecosystem Compatibility

ToolOps is designed to be the "glue" of the AI ecosystem. It works natively with:

#### Built-in Helpers
- **LangChain / LangGraph**
- **CrewAI**
- **LlamaIndex**
- **Model Context Protocol (MCP)**

#### General Compatibility
- **PydanticAI**
- **AutoGPT**
- Any Python function-based agent framework

---

## Observability & Metrics

ToolOps doesn't just run your tools; it measures them.
- **Structured Logging**: Every hit, miss, failure, and retry is logged in production-ready JSON.
- **OpenTelemetry**: Native traces and spans to visualize tool execution in Jaeger, Honeycomb, or Datadog.
- **Prometheus**: Real-time metrics for cache hit rates and tool latency.

---

## 🗺 Roadmap

- [ ] **Web Dashboard**: Real-time metrics, cost attribution, and hit rates UI.
- [ ] **Budget Control**: Hard limits on tool-induced API costs per hour/day.
- [ ] **Native MCP Server**: One-click deployment of ToolOps tools as a standalone host.
- [ ] **Streaming Middleware**: Support for streaming tool outputs in real-time.
- [ ] **New Backends**: MariaDB, ChromaDB, and Pinecone support.

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

# Clear a specific cache backend
toolops clear postgres --app my_app:setup_toolops
```

---

## Maintenance & Support

ToolOps is an open-source project by **Hedi MANAI**. I am building the future of Agentic Operations through lightweight, industrial-grade tools.

- **LinkedIn** [Connect with me](https://www.linkedin.com/in/hedimanai/)
- **GitHub** [Follow my work](https://github.com/hedimanai-pro)
- **Website** [Hedi Manai Portfolio](https://hedimanai.vercel.app/)
- **X (Twitter)** [Follow @hedi_manaii](https://x.com/hedi_manaii)
- **Discord** `@hedimanai`
- **Reddit** [Profile](https://www.reddit.com/user/Ornery_Charge_1033/)
- **Contact** [hedi.manai.pro@gmail.com](mailto:hedi.manai.pro@gmail.com)

---

## 📄 License

Apache License 2.0 — see [LICENSE](LICENSE) for details.

---

<div align="center">
Created by <b>Hedi MANAI</b>
<br>
<i>Empowering the next generation of Agentic Workflows.</i>
</div>