<div align="center">

[🇬🇧 English](https://github.com/hedimanai-pro/toolops/blob/main/README.md) | [🇫🇷 Français](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.fr.md) | [🇨🇳 中文](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.zh.md) | [🇯🇵 日本語](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ja.md) | [🇪🇸 Español](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.es.md) | [🇩🇪 Deutsch](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.de.md) | [🇵🇹 Português](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.pt.md) | [🇰🇷 한국어](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ko.md) | [🇷🇺 Русский](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ru.md) | [🇮🇳 हिन्दी](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="Logo de ToolOps">

# ToolOps

### La Capa de Resiliencia y Eficiencia de Grado Industrial para Herramientas de Agentes de IA

[![Versión PyPI](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Pruebas](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Cobertura](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![Descargas PyPI](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Licencia](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![Estrellas GitHub](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Construye agentes de IA listos para producción. Deja de escribir código de infraestructura repetitivo.**

[Sitio Web](https://hedimanai.vercel.app/) · [Documentación](https://hedimanai.vercel.app/projects/toolops.html) · [Inicio Rápido](#🚀-inicio-rápido) · [Registro de Cambios](CHANGELOG.md)

</div>

---

## ⚡ Resumen en 30 Segundos

> **"ToolOps es para las herramientas de IA lo que un Service Mesh es para los microservicios."**

Cuando construyes agentes de IA, las llamadas externas (LLMs, APIs, bases de datos) son **costosas**, **poco confiables** y **lentas**.
ToolOps elimina ese código repetitivo (boilerplate). Es un SDK de middleware agnóstico al framework que envuelve cualquier función de Python en un solo decorador, mejorándola instantáneamente con caché, resiliencia, observabilidad y control de concurrencia.

```python
# ANTES de ToolOps: más de 80 líneas de administradores de caché, lógica de reintentos, circuit breakers...

# DESPUÉS de ToolOps:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Almacenado en caché, reintentado y rastreado automáticamente
```

### 🚀 Benchmarks e Impacto
- **90% de reducción en llamadas a LLMs** mediante Caché Semántico.
- **<5ms de sobrecarga (overhead)** por ejecución de herramienta.
- **0 cambios de código** en tu lógica de negocio principal.

---

## ⚖️ ¿Por qué ToolOps?

Todo desarrollador de agentes choca contra un muro al pasar de una demo a producción. Así es como ToolOps se compara con las alternativas estándar:

| Característica | `@lru_cache` estándar | Nativo del Framework | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **Soporte nativo Async / `await`** | ❌ | ✅ | ✅ Nativo |
| **Caché semántico (basado en significado)** | ❌ | ⚠️ Básico | ✅ Embeddings Avanzados |
| **Caché distribuido / persistente** | ❌ | ⚠️ Varía | ✅ Postgres, Archivo |
| **Circuit Breaker (Cortacircuitos)** | ❌ | ❌ | ✅ Nativo |
| **Reintentos automáticos con Backoff** | ❌ | ⚠️ Requiere plugin | ✅ Nativo |
| **Fusión de Solicitudes (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Nativo |
| **Fallback Stale-if-error (Caché caducado)** | ❌ | ❌ | ✅ Nativo |
| **Seguridad (Claves SHA-256, Auto-enmascaramiento)**| ❌ | ❌ | ✅ Nativo |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Requiere callbacks | ✅ Nativo |
| **Agnóstico al Framework** | ✅ | ❌ Bloqueado | ✅ 100% Universal |

---

## 📦 Instalación

ToolOps usa un sistema de instalación modular. El paquete principal tiene **cero dependencias externas**. Solo instalas lo que necesitas.

### Referencia Rápida

| Comando de instalación | Lo que obtienes | Cuándo usarlo |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | Conjunto completo de características | **Recomendado para producción** |
| `pip install toolops` | Solo SDK principal | Para empezar, sin extras necesarios |

### 💻 Guías Específicas del Sistema Operativo

Recomendamos encarecidamente aislar tu proyecto en un entorno virtual.

#### 🐧 Linux & 🍎 macOS
```bash
# 1. Crea y activa un entorno virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instala ToolOps (se requieren comillas para bash/zsh)
pip install "toolops[all]"

# 3. Verifica la instalación
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. Crea y activa un entorno virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instala ToolOps
pip install "toolops[all]"

# 3. Verifica la instalación
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. Crea y activa un entorno virtual
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. Instala ToolOps (usa comillas dobles)
pip install "toolops[all]"

:: 3. Verifica la instalación
toolops doctor
```

---

## 🚀 Inicio Rápido

Este ejemplo mínimo te lleva desde la instalación hasta tener una herramienta funcional, en caché y resiliente en menos de 2 minutos.

```python
# Importaciones
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Paso 1: Registrar un backend de caché (haz esto una vez al inicio)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Paso 2: Decorar cualquier función asíncrona con @readonly para operaciones de lectura
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simular una llamada a una API externa
    return {"city": city, "temp": 22, "condition": "sunny"}


# Paso 3: Decorar operaciones de escritura con @sideeffect (sin caché, pero protegido)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Simular el envío de una notificación
    print(f"Alerta enviada: {message}")
    return True


async def main():
    # La primera llamada consulta a la API (en vivo)
    result = await fetch_weather("Paris")
    print(f"Primera llamada (en vivo): {result}")

    # La segunda llamada se sirve desde el caché — latence <5ms, 0 llamadas a la API
    result = await fetch_weather("Paris")
    print(f"Segunda llamada (en caché): {result}")

    # Operación de escritura con protección de circuit breaker
    await send_alert("El agente se completó con éxito.")

asyncio.run(main())
```

---

## 🧠 Conceptos Principales

### 1. Backends de Caché

Registra los backends una vez al inicio de la aplicación, luego referéncialos por nombre. ToolOps soporta múltiples backends simultáneamente.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# En memoria: el más rápido, se borra al reiniciar, sin dependencias
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres: persistente a través de reinicios, compartible entre procesos
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Semántico: embeddings vectoriales para coincidir por significado, no por igualdad estricta de cadenas
# Reduce las llamadas a LLMs hasta en un 90%
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. Patrones de Resiliencia

ToolOps proporciona una resiliencia robusta y probada en producción desde el primer momento.

- **Circuit Breaker**: Evita bombardear un servicio fallido y causar fallos en cascada.
- **Stale-if-Error**: Sirve el último valor almacenado en caché conocido si falla la llamada a la API en vivo.
- **Fusión de Solicitudes (Request Coalescing)**: Si 50 agentes llaman al mismo endpoint simultáneamente, ToolOps ejecuta la llamada real a la API **una vez** y transmite (multicast) el resultado a todos.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Fallback en caso de fallo de la API
    circuit_breaker = True      # Protege el servicio subyacente
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Arquitectura y Seguridad (v0.2.0)

ToolOps v0.2.0 introduce una arquitectura de nivel empresarial:

- **Pipeline de Middleware**: El decorador monolítico ha sido refactorizado en un pipeline componible (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`).
- **Hashing de claves de caché SHA-256**: Todas las claves de caché están estrictamente hasheadas. No se exponen datos sensibles (tokens, PII) en los almacenes de caché.
- **Enmascaramiento Automático de Parámetros**: Los argumentos de las herramientas que contienen palabras clave sensibles (`token`, `password`, `secret`, etc.) se enmascaran automáticamente como `***MASKED***` en los logs estructurados.

---

## 📊 Observabilidad

ToolOps instrumenta cada llamada a la herramienta automáticamente.

### OpenTelemetry (OTEL) & Prometheus

**Requiere:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# Apunta a cualquier backend compatible con OTEL (Jaeger, Datadog, Honeycomb, etc.)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Exponer métricas de Prometheus
configure_prometheus(port=8000)
```

Las métricas clave expuestas incluyen `toolops_cache_hits_total`, `toolops_tool_latency_seconds` y `toolops_circuit_opens_total`.

---

## 🔌 Integración con Frameworks

ToolOps decora funciones asíncronas simples de Python, haciéndolo **100% compatible** con tus frameworks de agentes favoritos.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Buscar en la web y devolver un resumen."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Obtiene y almacena en caché datos de investigación."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Generar una definición de herramienta MCP completamente tipada de forma automática
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ Referencia de la CLI

ToolOps incluye una herramienta de línea de comandos para gestionar tu infraestructura de caché.

```bash
# Comprobar la salud de todos los backends registrados
toolops doctor

# Ver estadísticas de caché en vivo para una aplicación
toolops stats --app my_app:setup_toolops

# Borrar la caché de un backend específico
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Contribución

ToolOps está construido para la comunidad, por la comunidad. 

- Revisa nuestra [Guía de Contribución](CONTRIBUTING.md) para empezar.
- Consulta el [Código de Conducta](CODE_OF_CONDUCT.md).
- Reporta problemas de seguridad de forma segura a través de nuestra [Política de Seguridad](SECURITY.md).

---

## 💬 Comunidad y Contacto

Estamos construyendo activamente el futuro de la infraestructura de los agentes de IA. ¡Únete a la discusión!

- **Creador:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Reportar Bugs y Solicitar Funciones:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **Correo Electrónico:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Construido para Producción.</b><br>
Licenciado bajo <a href="LICENSE">Apache 2.0</a>
</div>
