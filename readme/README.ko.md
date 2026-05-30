<div align="center">

[🇬🇧 English](https://github.com/hedimanai-pro/toolops/blob/main/README.md) | [🇫🇷 Français](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.fr.md) | [🇨🇳 中文](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.zh.md) | [🇯🇵 日本語](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ja.md) | [🇪🇸 Español](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.es.md) | [🇩🇪 Deutsch](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.de.md) | [🇵🇹 Português](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.pt.md) | [🇰🇷 한국어](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ko.md) | [🇷🇺 Русский](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ru.md) | [🇮🇳 हिन्दी](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps 로고">

# ToolOps

### AI 에이전트 도구를 위한 산업용 수준의 복원력 및 효율성 레이어

[![PyPI 버전](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![테스트](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![커버리지](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI 다운로드](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![라이선스](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](../LICENSE)
[![GitHub Star](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**프로덕션 레벨의 AI 에이전트를 구축하세요. 인프라 보일러플레이트 코드 작성은 이제 그만하세요.**

[웹사이트](https://hedimanai.vercel.app/) · [공식 문서](https://hedimanai.vercel.app/projects/toolops.html) · [빠른 시작](#🚀-빠른-시작-quickstart) · [변경 내역](../CHANGELOG.md)

</div>

---

## ⚡ 30초 요약

> **"마이크로서비스에 서비스 메시(Service Mesh)가 있다면, AI 도구에는 ToolOps가 있습니다."**

AI 에이전트를 구축할 때 외부 호출(LLM, API, 데이터베이스)은 **비용이 많이 들고**, **신뢰할 수 없으며**, **느립니다**.
ToolOps는 이러한 보일러플레이트 코드를 제거합니다. 프레임워크에 구애받지 않는 미들웨어 SDK로서 단일 데코레이터로 파이썬 함수를 래핑하여 캐싱, 복원력, 관측 가능성(Observability), 그리고 동시성 제어 기능을 즉시 업그레이드합니다.

```python
# ToolOps 도입 전: 캐시 관리자, 재시도 로직, 서킷 브레이커 등 80줄 이상의 코드...

# ToolOps 도입 후:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # 자동으로 캐시, 재시도 및 추적(Tracing)됩니다
```

### 🚀 벤치마크 및 영향
- 시맨틱 캐싱을 통해 **LLM 호출 90% 감소**.
- 도구 실행당 **오버헤드 5ms 미만**.
- 핵심 비즈니스 로직의 **코드 변경 0**.

---

## ⚖️ 왜 ToolOps인가요?

모든 에이전트 개발자는 데모에서 프로덕션 환경으로 넘어갈 때 벽에 부딪힙니다. ToolOps와 표준 대안들의 비교는 다음과 같습니다:

| 기능 | 표준 `@lru_cache` | 프레임워크 네이티브 | 🚀 ToolOps v1.0.0 |
| :--- | :---: | :---: | :---: |
| **네이티브 Async / `await` 지원** | ❌ | ✅ | ✅ 네이티브 |
| **시맨틱(의미 인식) 캐시** | ❌ | ⚠️ 기본적 | ✅ 고급 임베딩 |
| **분산 / 영구 캐시** | ❌ | ⚠️ 상이함 | ✅ Postgres, SQLite, MySQL, Valkey/Redis |
| **서킷 브레이커 (Circuit Breaker)** | ❌ | ❌ | ✅ 네이티브 |
| **백오프(Backoff)를 적용한 자동 재시도** | ❌ | ⚠️ 플러그인 필요 | ✅ 네이티브 |
| **요청 병합 (Anti-Thundering Herd)**| ❌ | ❌ | ✅ 네이티브 |
| **오류 시 기존 캐시 사용 (Stale-if-error)** | ❌ | ❌ | ✅ 네이티브 |
| **보안 (SHA-256 키 해싱, 자동 마스킹)**| ❌ | ❌ | ✅ 네이티브 |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ 콜백 필요 | ✅ 네이티브 |
| **프레임워크 비종속성** | ✅ | ❌ 종속됨 | ✅ 100% 범용 |

---

## 📦 설치

ToolOps는 기본적으로 모든 기능을 제공합니다. 설치 시 모든 캐시 백엔드(Memory, File, SQLite, Valkey, Redis, MySQL/MariaDB, Postgres, Semantic), 회복성 기능 및 OpenTelemetry/Prometheus 모니터링 도구가 기본적으로 자동 설치됩니다.

```bash
pip install toolops
```

## 🚀 빠른 시작 (Quickstart)

이 최소한의 예제는 설치부터 캐싱 및 복원력을 갖춘 도구를 작동시키기까지 2분도 채 걸리지 않습니다.

```python
# 임포트
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# 1단계: 캐시 백엔드 등록 (시작 시 한 번만 수행)
cache_manager.register("memory", MemoryCache(), is_default=True)


# 2단계: 읽기 작업의 경우 비동기 함수를 @readonly로 데코레이션
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # 외부 API 호출 시뮬레이션
    return {"city": city, "temp": 22, "condition": "sunny"}


# 3단계: 쓰기 작업을 @sideeffect로 데코레이션 (캐싱 없음, 단 보호됨)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # 알림 전송 시뮬레이션
    print(f"알림 전송됨: {message}")
    return True


async def main():
    # 첫 번째 호출은 API에 도달합니다 (라이브)
    result = await fetch_weather("Paris")
    print(f"첫 번째 호출 (라이브): {result}")

    # 두 번째 호출은 캐시에서 제공됩니다 — 5ms 미만 지연 시간, API 호출 0회
    result = await fetch_weather("Paris")
    print(f"두 번째 호출 (캐시): {result}")

    # 서킷 브레이커 보호가 적용된 쓰기 작업
    await send_alert("에이전트가 성공적으로 완료되었습니다.")

asyncio.run(main())
```

---

## 🧠 핵심 개념

### 1. 캐시 백엔드 (Cache Backends)

애플리케이션 시작 시 백엔드를 한 번 등록한 후 이름으로 참조합니다. ToolOps는 여러 백엔드를 동시에 지원합니다.

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

### 2. 복원력 패턴 (Resilience Patterns)

ToolOps는 프로덕션에서 검증된 강력한 복원력을 기본적으로 제공합니다.

- **서킷 브레이커(Circuit Breaker)**: 실패하는 서비스에 계속 요청을 보내 연쇄적인 오류를 일으키는 것을 방지합니다.
- **오류 시 캐시 제공(Stale-if-Error)**: 실시간 API 호출이 실패할 경우 마지막으로 알려진 유효한 캐시 값을 제공합니다.
- **요청 병합(Request Coalescing)**: 50개의 에이전트가 동일한 엔드포인트를 동시에 호출하면 ToolOps는 실제 API 호출을 **한 번만** 실행하고 결과를 모든 요청에 브로드캐스트합니다.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # API 실패 시 폴백(Fallback)
    circuit_breaker = True      # 기본 서비스 보호
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. 아키텍처 및 보안 (v1.0.0)

ToolOps v1.0.0은 엔터프라이즈급 아키텍처를 도입했습니다:

- **미들웨어 파이프라인**: 모놀리식 데코레이터가 구성 가능한 파이프라인(`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`)으로 리팩터링되었습니다.
- **SHA-256 캐시 키 해싱**: 모든 캐시 키는 엄격하게 해시 처리됩니다. 캐시 저장소에는 민감한 데이터(토큰, 개인정보 등)가 노출되지 않습니다.
- **자동 매개변수 마스킹**: 민감한 키워드(`token`, `password`, `secret` 등)가 포함된 도구 인수는 구조화된 로그에서 `***MASKED***`로 자동 마스킹됩니다.

---

## 📊 관측 가능성 (Observability)

ToolOps는 모든 도구 호출을 자동으로 계측합니다.

### OpenTelemetry (OTEL) & Prometheus

```python
from toolops import configure_opentelemetry, prometheus_metrics

# 1. Configure OpenTelemetry tracing (accepts any standard tracer instance)
configure_opentelemetry(tracer)


# 2. Expose Prometheus metrics (returns a raw Prometheus text string)
metrics_string = prometheus_metrics()
```

노출되는 주요 메트릭에는 `toolops_cache_hits_total`, `toolops_tool_latency_seconds`, `toolops_circuit_opens_total`이 포함됩니다.

---

## 🔌 프레임워크 통합

ToolOps는 일반 파이썬 비동기 함수를 데코레이션하므로 선호하는 에이전트 프레임워크와 **100% 호환**됩니다.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """웹을 검색하고 요약을 반환합니다."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "연구 데이터를 가져오고 캐시합니다."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# 완전한 타입이 지정된 MCP 도구 정의를 자동으로 생성합니다.
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ CLI 참조

ToolOps는 캐시 인프라를 관리할 수 있는 명령줄 도구(CLI)와 함께 제공됩니다.

```bash
# 등록된 모든 백엔드의 상태 확인
toolops doctor

# 앱의 실시간 캐시 통계 확인
toolops stats --app my_app:setup_toolops

# 특정 백엔드의 캐시 삭제
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 기여하기 (Contributing)

ToolOps는 커뮤니티에 의해, 커뮤니티를 위해 구축되었습니다.

- 시작하려면 [기여 가이드](../CONTRIBUTING.md)를 검토하세요.
- [행동 강령](../CODE_OF_CONDUCT.md)을 확인하세요.
- [보안 정책](../SECURITY.md)을 통해 보안 문제를 안전하게 보고하세요.

---

## 💬 커뮤니티 및 연락처

우리는 AI 에이전트 인프라의 미래를 적극적으로 구축하고 있습니다. 토론에 참여하세요!

- **제작자:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **버그 보고 및 기능 요청:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **이메일:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — 프로덕션을 위해 구축되었습니다.</b><br>
<a href="LICENSE">Apache 2.0</a> 라이선스 적용.
</div>
