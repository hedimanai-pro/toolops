<div align="center">

[🇬🇧 English](https://github.com/hedimanai-pro/toolops/blob/main/README.md) | [🇫🇷 Français](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.fr.md) | [🇨🇳 中文](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.zh.md) | [🇯🇵 日本語](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ja.md) | [🇪🇸 Español](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.es.md) | [🇩🇪 Deutsch](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.de.md) | [🇵🇹 Português](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.pt.md) | [🇰🇷 한국어](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ko.md) | [🇷🇺 Русский](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ru.md) | [🇮🇳 हिन्दी](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### Die industrietaugliche Resilienz- & Effizienzschicht für KI-Agenten-Tools

[![PyPI Version](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Tests](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Abdeckung](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI Downloads](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Lizenz](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](../LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Bauen Sie produktionsreife KI-Agenten. Hören Sie auf, Infrastruktur-Boilerplate zu schreiben.**

[Website](https://hedimanai.vercel.app/) · [Dokumentation](https://hedimanai.vercel.app/projects/toolops.html) · [Schnellstart](#🚀-schnellstart) · [Änderungsprotokoll](../CHANGELOG.md)

</div>

---

## ⚡ 30-Sekunden-Pitch

> **"ToolOps ist für KI-Tools das, was ein Service Mesh für Microservices ist."**

Wenn Sie KI-Agenten entwickeln, sind externe Aufrufe (LLMs, APIs, Datenbanken) oft **teuer**, **unzuverlässig** und **langsam**.
ToolOps eliminiert diese Boilerplate. Es ist ein Framework-unabhängiges Middleware-SDK, das jede beliebige Python-Funktion mit einem einzigen Dekorator umschließt und sie sofort mit Caching, Resilienz, Observability (Beobachtbarkeit) und Nebenläufigkeitskontrolle ausstattet.

```python
# VOR ToolOps: 80+ Zeilen für Cache-Manager, Retry-Logik, Circuit Breakers...

# NACH ToolOps:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Automatisch gecached, wiederholt und nachverfolgt
```

### 🚀 Benchmarks & Auswirkungen
- **90% Reduzierung von LLM-Aufrufen** durch semantisches Caching.
- **<5ms Overhead** pro Tool-Ausführung.
- **0 Code-Änderungen** an Ihrer Kern-Geschäftslogik.

---

## ⚖️ Warum ToolOps?

Jeder Agenten-Entwickler stößt an eine Grenze, wenn er vom Demo- in den Produktionsbetrieb wechselt. So vergleicht sich ToolOps mit Standardalternativen:

| Funktion | Standard `@lru_cache` | Framework-Nativ | 🚀 ToolOps v1.0.0 |
| :--- | :---: | :---: | :---: |
| **Nativer Async / `await` Support** | ❌ | ✅ | ✅ Nativ |
| **Semantischer (bedeutungsbezogener) Cache** | ❌ | ⚠️ Einfach | ✅ Erweiterte Embeddings |
| **Verteilter / Persistenter Cache** | ❌ | ⚠️ Variiert | ✅ Postgres, SQLite, MySQL, Valkey/Redis |
| **Circuit Breaker** | ❌ | ❌ | ✅ Nativ |
| **Automatische Retries mit Backoff** | ❌ | ⚠️ Plugin benötigt | ✅ Nativ |
| **Request Coalescing (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Nativ |
| **Stale-if-error Fallback (Veralteter Cache bei Fehler)** | ❌ | ❌ | ✅ Nativ |
| **Sicherheit (SHA-256 Schlüssel, Auto-Masking)**| ❌ | ❌ | ✅ Nativ |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Callbacks benötigt | ✅ Nativ |
| **Framework-unabhängig (Agnostisch)** | ✅ | ❌ Eingesperrt (Lock-in) | ✅ 100% Universell |

---

## 📦 Installation

ToolOps ist standardmäßig komplett ausgestattet. Die Installation installiert automatisch alle Cache-Backends (Memory, File, SQLite, Valkey, Redis, MySQL/MariaDB, Postgres und Semantic), Resilienz-Features sowie OpenTelemetry/Prometheus-Überwachungstools.

```bash
pip install toolops
```

## 🚀 Schnellstart

Dieses Minimalbeispiel bringt Sie in weniger als 2 Minuten von der Installation zu einem funktionierenden, gecachten und resilienten Tool.

```python
# Importe
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Schritt 1: Registrieren Sie ein Cache-Backend (einmalig beim Start durchführen)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Schritt 2: Dekorieren Sie jede asynchrone Funktion mit @readonly für Leseoperationen
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simuliert einen externen API-Aufruf
    return {"city": city, "temp": 22, "condition": "sunny"}


# Schritt 3: Dekorieren Sie Schreiboperationen mit @sideeffect (kein Caching, aber geschützt)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Simuliert das Senden einer Benachrichtigung
    print(f"Benachrichtigung gesendet: {message}")
    return True


async def main():
    # Erster Aufruf fragt die API ab (Live)
    result = await fetch_weather("Paris")
    print(f"Erster Aufruf (Live): {result}")

    # Zweiter Aufruf wird aus dem Cache bedient — <5ms Latenz, 0 API-Aufrufe
    result = await fetch_weather("Paris")
    print(f"Zweiter Aufruf (Cache): {result}")

    # Schreiboperation mit Circuit Breaker-Schutz
    await send_alert("Agent erfolgreich abgeschlossen.")

asyncio.run(main())
```

---

## 🧠 Kernkonzepte

### 1. Cache-Backends

Registrieren Sie Backends einmalig beim Anwendungsstart und referenzieren Sie diese dann nach Namen. ToolOps unterstützt mehrere Backends gleichzeitig.

```python
from toolops import cache_manager
from toolops.cache import (
    MemoryCache,
    FileCache,
    PostgresCache,
    SQLiteCache,
    ValkeyCache,
    RedisCache,
    MySQLCache,
    SemanticCache,
    SentenceTransformerEmbedder,
)


# In-memory: fastest, cleared on restart, no extra dependencies
cache_manager.register("memory", MemoryCache(), is_default=True)


# File: zero-dependency persistent cache, ideal for single-process apps
cache_manager.register("file", FileCache("/tmp/toolops-cache"))


# SQLite: lightweight persistent cache, single-file, no server required
cache_manager.register("sqlite", SQLiteCache("toolops_cache.db"))


# Postgres: persistent across restarts, shareable across processes
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Valkey / Redis: distributed in-memory cache with async pooling
cache_manager.register("valkey", ValkeyCache(host="localhost", port=6379))
cache_manager.register("redis", RedisCache(url="redis://localhost:6379/0"))


# MySQL / MariaDB: persistent relational cache
cache_manager.register("mysql", MySQLCache(host="localhost", db="myapp", user="root", password="secret"))
# — or via DSN —
cache_manager.register("mysql", MySQLCache(dsn="mysql://root:secret@localhost:3306/myapp"))


# Semantic: vector embeddings to match by meaning, not string equality
# Reduces LLM calls up to 90%
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. Resilienz-Muster (Resilience Patterns)

ToolOps bietet sofort einsatzbereite, robuste und praxiserprobte Resilienz.

- **Circuit Breaker**: Verhindert, dass ein ausfallender Service überlastet wird und kaskadierende Fehler verursacht.
- **Stale-if-Error**: Liefert den zuletzt bekannten, gültigen Cache-Wert, wenn der Live-API-Aufruf fehlschlägt.
- **Request Coalescing (Anfragezusammenführung)**: Wenn 50 Agenten gleichzeitig denselben Endpunkt aufrufen, führt ToolOps den echten API-Aufruf **genau einmal** aus und leitet das Ergebnis an alle weiter (Multicast).

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Fallback bei API-Fehler
    circuit_breaker = True      # Schützt den zugrunde liegenden Service
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Architektur & Sicherheit (v1.0.0)

ToolOps v1.0.0 führt eine Enterprise-Grade Architektur ein:

- **Middleware-Pipeline**: Der monolithische Dekorator wurde in eine zusammensetzbare Pipeline (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`) refaktorisiert.
- **SHA-256 Cache-Key-Hashing**: Alle Cache-Schlüssel werden strikt gehasht. Es werden keine sensiblen Daten (Tokens, PII) in Cache-Speichern offengelegt.
- **Automatisches Parameter-Masking**: Tool-Argumente, die sensible Schlüsselwörter (`token`, `password`, `secret` usw.) enthalten, werden in strukturierten Logs automatisch als `***MASKED***` maskiert.

---

## 📊 Observability (Beobachtbarkeit)

ToolOps instrumentiert jeden Tool-Aufruf automatisch.

### OpenTelemetry (OTEL) & Prometheus

```python
from toolops import configure_opentelemetry, prometheus_metrics

# 1. Configure OpenTelemetry tracing (accepts any standard tracer instance)
configure_opentelemetry(tracer)


# 2. Expose Prometheus metrics (returns a raw Prometheus text string)
metrics_string = prometheus_metrics()
```

Zu den wichtigsten Metriken gehören `toolops_cache_hits_total`, `toolops_tool_latency_seconds` und `toolops_circuit_opens_total`.

---

## 🔌 Framework-Integration

ToolOps dekoriert gewöhnliche asynchrone Python-Funktionen und ist daher **100% kompatibel** mit Ihren bevorzugten Agenten-Frameworks.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Das Web durchsuchen und eine Zusammenfassung zurückgeben."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Ruft Forschungsdaten ab und speichert sie im Cache."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Generiert automatisch eine vollständig typisierte MCP-Tool-Definition
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ CLI-Referenz

ToolOps wird mit einem Kommandozeilen-Tool zur Verwaltung Ihrer Cache-Infrastruktur geliefert.

```bash
# Überprüfen Sie den Status aller registrierten Backends
toolops doctor

# Live-Cache-Statistiken für eine App anzeigen
toolops stats --app my_app:setup_toolops

# Den Cache eines bestimmten Backends leeren
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Mitwirken (Contributing)

ToolOps wurde für die Community und von der Community entwickelt.

- Lesen Sie unseren [Beitragsleitfaden](../CONTRIBUTING.md) (Contributing Guide), um loszulegen.
- Werfen Sie einen Blick auf den [Verhaltenskodex](../CODE_OF_CONDUCT.md).
- Melden Sie Sicherheitsprobleme sicher über unsere [Sicherheitsrichtlinie](../SECURITY.md).

---

## 💬 Community & Kontakt

Wir bauen aktiv die Zukunft der KI-Agenten-Infrastruktur. Nehmen Sie an der Diskussion teil!

- **Entwickler:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Bugs melden & Features anfragen:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **E-Mail:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Gebaut für die Produktion.</b><br>
Lizenziert unter <a href="LICENSE">Apache 2.0</a>
</div>
