<div align="center">

[🇬🇧 English](https://github.com/hedimanai-pro/toolops/blob/main/README.md) | [🇫🇷 Français](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.fr.md) | [🇨🇳 中文](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.zh.md) | [🇯🇵 日本語](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ja.md) | [🇪🇸 Español](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.es.md) | [🇩🇪 Deutsch](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.de.md) | [🇵🇹 Português](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.pt.md) | [🇰🇷 한국어](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ko.md) | [🇷🇺 Русский](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ru.md) | [🇮🇳 हिन्दी](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### Промышленный Слой Отказоустойчивости и Эффективности для Инструментов ИИ-Агентов

[![Версия PyPI](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Тесты](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Покрытие](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![Скачивания PyPI](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Лицензия](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](../LICENSE)
[![Звезды GitHub](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Создавайте ИИ-агентов, готовых к production. Хватит писать шаблонный инфраструктурный код.**

[Веб-сайт](https://hedimanai.vercel.app/) · [Документация](https://hedimanai.vercel.app/projects/toolops.html) · [Быстрый старт](#🚀-быстрый-старт) · [История изменений](../CHANGELOG.md)

</div>

---

## ⚡ Обзор за 30 секунд

> **"ToolOps для инструментов ИИ — это то же самое, что Service Mesh для микросервисов."**

Когда вы создаете ИИ-агентов, внешние вызовы (LLM, API, базы данных) оказываются **дорогими**, **ненадежными** и **медленными**.
ToolOps устраняет этот шаблонный код (boilerplate). Это независимый от фреймворка SDK промежуточного ПО (middleware), который оборачивает любую функцию Python в один декоратор, мгновенно добавляя в нее кэширование, отказоустойчивость, наблюдаемость (observability) и контроль параллелизма.

```python
# ДО ToolOps: более 80 строк менеджеров кэша, логики повторных попыток, circuit breaker'ов...

# ПОСЛЕ ToolOps:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Автоматическое кэширование, повторные попытки и трассировка
```

### 🚀 Бенчмарки и влияние
- **Снижение количества вызовов LLM на 90%** благодаря семантическому кэшированию.
- **Накладные расходы <5 мс** на каждое выполнение инструмента.
- **0 изменений кода** в вашей основной бизнес-логике.

---

## ⚖️ Почему ToolOps?

Каждый разработчик агентов сталкивается с препятствиями при переходе от демо-версии к production. Вот как ToolOps соотносится со стандартными альтернативами:

| Функция | Стандартный `@lru_cache` | Встроенный во фреймворк | 🚀 ToolOps v1.0.0 |
| :--- | :---: | :---: | :---: |
| **Нативная поддержка Async / `await`** | ❌ | ✅ | ✅ Нативно |
| **Семантический кэш (по смыслу)** | ❌ | ⚠️ Базовый | ✅ Продвинутые эмбеддинги |
| **Распределенный / Постоянный кэш** | ❌ | ⚠️ По-разному | ✅ Postgres, SQLite, MySQL, Valkey/Redis |
| **Circuit Breaker (Предохранитель)** | ❌ | ❌ | ✅ Нативно |
| **Автоматические повторы с Backoff** | ❌ | ⚠️ Нужен плагин | ✅ Нативно |
| **Объединение запросов (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Нативно |
| **Fallback Stale-if-error (Устаревший кэш при ошибке)** | ❌ | ❌ | ✅ Нативно |
| **Безопасность (Ключи SHA-256, Авто-маскирование)**| ❌ | ❌ | ✅ Нативно |
| **OpenTelemetry и Prometheus** | ❌ | ⚠️ Нужны коллбэки | ✅ Нативно |
| **Независимость от фреймворка** | ✅ | ❌ Привязка (Lock-in) | ✅ 100% Универсально |

---

## 📦 Установка

ToolOps поставляется в комплекте со всеми функциями. Установка по умолчанию устанавливает все бэкенды кэширования (Memory, File, SQLite, Valkey, Redis, MySQL/MariaDB, Postgres и Semantic), функции отказоустойчивости и инструменты мониторинга OpenTelemetry/Prometheus.

```bash
pip install toolops
```

## 🚀 Быстрый старт

Этот минимальный пример позволит вам пройти путь от установки до работающего, кэшируемого и отказоустойчивого инструмента менее чем за 2 минуты.

```python
# Импорты
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Шаг 1: Зарегистрируйте бэкенд кэша (выполняется один раз при запуске)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Шаг 2: Декорируйте любую асинхронную функцию с помощью @readonly для операций чтения
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Имитация внешнего вызова API
    return {"city": city, "temp": 22, "condition": "sunny"}


# Шаг 3: Декорируйте операции записи с помощью @sideeffect (без кэширования, но с защитой)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Имитация отправки уведомления
    print(f"Уведомление отправлено: {message}")
    return True


async def main():
    # Первый вызов обращается к API (реальное время)
    result = await fetch_weather("Paris")
    print(f"Первый вызов (Live): {result}")

    # Второй вызов обслуживается из кэша — задержка <5 мс, 0 вызовов API
    result = await fetch_weather("Paris")
    print(f"Второй вызов (Кэш): {result}")

    # Операция записи с защитой circuit breaker
    await send_alert("Агент успешно завершил работу.")

asyncio.run(main())
```

---

## 🧠 Основные концепции

### 1. Бэкенды кэша

Зарегистрируйте бэкенды один раз при запуске приложения, затем обращайтесь к ним по имени. ToolOps поддерживает работу с несколькими бэкендами одновременно.

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

### 2. Паттерны отказоустойчивости

ToolOps предоставляет надежную, проверенную в production отказоустойчивость "из коробки".

- **Circuit Breaker (Предохранитель)**: Предотвращает перегрузку сбойного сервиса и возникновение каскадных сбоев.
- **Stale-if-Error (Устаревший кэш при ошибке)**: Возвращает последнее известное корректное значение из кэша, если вызов API завершается ошибкой.
- **Объединение запросов (Request Coalescing)**: Если 50 агентов одновременно обращаются к одной и той же конечной точке (endpoint), ToolOps выполняет реальный вызов API **только один раз** и транслирует результат всем.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Fallback при сбое API
    circuit_breaker = True      # Защищает нижележащий сервис
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Архитектура и безопасность (v1.0.0)

В ToolOps v1.0.0 представлена архитектура корпоративного уровня:

- **Конвейер Middleware**: Монолитный декоратор был преобразован в компонуемый конвейер (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`).
- **Хэширование ключей кэша SHA-256**: Все ключи кэша строго хэшируются. Никакие конфиденциальные данные (токены, PII) не сохраняются в хранилищах кэша в открытом виде.
- **Автоматическое маскирование параметров**: Аргументы инструментов, содержащие конфиденциальные ключевые слова (`token`, `password`, `secret` и т. д.), автоматически маскируются как `***MASKED***` в структурированных логах.

---

## 📊 Наблюдаемость (Observability)

ToolOps автоматически инструментирует каждый вызов инструмента.

### OpenTelemetry (OTEL) и Prometheus

```python
from toolops import configure_opentelemetry, prometheus_metrics

# 1. Configure OpenTelemetry tracing (accepts any standard tracer instance)
configure_opentelemetry(tracer)


# 2. Expose Prometheus metrics (returns a raw Prometheus text string)
metrics_string = prometheus_metrics()
```

Ключевые экспортируемые метрики включают `toolops_cache_hits_total`, `toolops_tool_latency_seconds` и `toolops_circuit_opens_total`.

---

## 🔌 Интеграция с фреймворками

ToolOps декорирует обычные асинхронные функции Python, что делает его **на 100% совместимым** с вашими любимыми фреймворками для агентов.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Поиск в Интернете и возврат сводки."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Получает и кэширует данные исследования."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Автоматическая генерация полностью типизированного определения инструмента MCP
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ Справочник CLI

ToolOps поставляется с инструментом командной строки для управления инфраструктурой кэширования.

```bash
# Проверка состояния всех зарегистрированных бэкендов
toolops doctor

# Просмотр статистики кэша для приложения в реальном времени
toolops stats --app my_app:setup_toolops

# Очистка кэша определенного бэкенда
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Участие в разработке

ToolOps создан для сообщества и самим сообществом. 

- Ознакомьтесь с нашим [Руководством по участию](../CONTRIBUTING.md), чтобы начать.
- Ознакомьтесь с [Кодексом поведения](../CODE_OF_CONDUCT.md).
- Сообщайте о проблемах безопасности через нашу [Политику безопасности](../SECURITY.md).

---

## 💬 Сообщество и контакты

Мы активно строим будущее инфраструктуры ИИ-агентов. Присоединяйтесь к обсуждению!

- **Создатель:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Сообщить об ошибке или запросить функцию:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **Email:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Создан для production.</b><br>
Лицензия <a href="LICENSE">Apache 2.0</a>
</div>
