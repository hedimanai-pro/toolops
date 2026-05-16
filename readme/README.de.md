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
[![Lizenz](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Stars](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Bauen Sie produktionsreife KI-Agenten. Hören Sie auf, Infrastruktur-Boilerplate zu schreiben.**

[Website](https://hedimanai.vercel.app/) · [Dokumentation](https://hedimanai.vercel.app/projects/toolops.html) · [Schnellstart](#🚀-schnellstart) · [Änderungsprotokoll](CHANGELOG.md)

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

| Funktion | Standard `@lru_cache` | Framework-Nativ | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **Nativer Async / `await` Support** | ❌ | ✅ | ✅ Nativ |
| **Semantischer (bedeutungsbezogener) Cache** | ❌ | ⚠️ Einfach | ✅ Erweiterte Embeddings |
| **Verteilter / Persistenter Cache** | ❌ | ⚠️ Variiert | ✅ Postgres, Datei |
| **Circuit Breaker** | ❌ | ❌ | ✅ Nativ |
| **Automatische Retries mit Backoff** | ❌ | ⚠️ Plugin benötigt | ✅ Nativ |
| **Request Coalescing (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Nativ |
| **Stale-if-error Fallback (Veralteter Cache bei Fehler)** | ❌ | ❌ | ✅ Nativ |
| **Sicherheit (SHA-256 Schlüssel, Auto-Masking)**| ❌ | ❌ | ✅ Nativ |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Callbacks benötigt | ✅ Nativ |
| **Framework-unabhängig (Agnostisch)** | ✅ | ❌ Eingesperrt (Lock-in) | ✅ 100% Universell |

---

## 📦 Installation

ToolOps verwendet ein modulares Installationssystem. Das Kernpaket hat **null externe Abhängigkeiten**. Sie installieren nur das, was Sie benötigen.

### Kurzübersicht

| Installationsbefehl | Was Sie erhalten | Wann Sie es verwenden sollten |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | Vollständiger Funktionsumfang | **Empfohlen für die Produktion** |
| `pip install toolops` | Nur Core SDK | Für den Einstieg, keine Extras benötigt |

### 💻 Betriebssystemspezifische Anleitungen

Wir empfehlen dringend, Ihr Projekt in einer virtuellen Umgebung zu isolieren.

#### 🐧 Linux & 🍎 macOS
```bash
# 1. Erstellen und aktivieren Sie eine virtuelle Umgebung
python -m venv .venv
source .venv/bin/activate

# 2. Installieren Sie ToolOps (Anführungszeichen sind für bash/zsh erforderlich)
pip install "toolops[all]"

# 3. Überprüfen Sie die Installation
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. Erstellen und aktivieren Sie eine virtuelle Umgebung
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Installieren Sie ToolOps
pip install "toolops[all]"

# 3. Überprüfen Sie die Installation
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. Erstellen und aktivieren Sie eine virtuelle Umgebung
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. Installieren Sie ToolOps (verwenden Sie doppelte Anführungszeichen)
pip install "toolops[all]"

:: 3. Überprüfen Sie die Installation
toolops doctor
```

---

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
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# In-Memory: am schnellsten, wird beim Neustart geleert, keine Abhängigkeiten
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres: persistent über Neustarts hinweg, teilbar zwischen Prozessen
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Semantisch: Vektor-Embeddings zum Abgleichen nach Bedeutung, nicht nach exakter Zeichenfolge
# Reduziert LLM-Aufrufe um bis zu 90%
from toolops.cache import SentenceTransformerEmbedder
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

### 3. Architektur & Sicherheit (v0.2.0)

ToolOps v0.2.0 führt eine Enterprise-Grade Architektur ein:

- **Middleware-Pipeline**: Der monolithische Dekorator wurde in eine zusammensetzbare Pipeline (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`) refaktorisiert.
- **SHA-256 Cache-Key-Hashing**: Alle Cache-Schlüssel werden strikt gehasht. Es werden keine sensiblen Daten (Tokens, PII) in Cache-Speichern offengelegt.
- **Automatisches Parameter-Masking**: Tool-Argumente, die sensible Schlüsselwörter (`token`, `password`, `secret` usw.) enthalten, werden in strukturierten Logs automatisch als `***MASKED***` maskiert.

---

## 📊 Observability (Beobachtbarkeit)

ToolOps instrumentiert jeden Tool-Aufruf automatisch.

### OpenTelemetry (OTEL) & Prometheus

**Erfordert:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# Verweist auf jedes OTEL-kompatible Backend (Jaeger, Datadog, Honeycomb usw.)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Prometheus-Metriken bereitstellen
configure_prometheus(port=8000)
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

- Lesen Sie unseren [Beitragsleitfaden](CONTRIBUTING.md) (Contributing Guide), um loszulegen.
- Werfen Sie einen Blick auf den [Verhaltenskodex](CODE_OF_CONDUCT.md).
- Melden Sie Sicherheitsprobleme sicher über unsere [Sicherheitsrichtlinie](SECURITY.md).

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
