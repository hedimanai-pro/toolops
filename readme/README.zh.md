<div align="center">

[🇬🇧 English](../README.md) | [🇫🇷 Français](README.fr.md) | [🇨🇳 中文](README.zh.md) | [🇯🇵 日本語](README.ja.md) | [🇪🇸 Español](README.es.md) | [🇩🇪 Deutsch](README.de.md) | [🇵🇹 Português](README.pt.md) | [🇰🇷 한국어](README.ko.md) | [🇷🇺 Русский](README.ru.md) | [🇮🇳 हिन्दी](README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### 工业级 AI 智能体工具弹性与效能层

[![PyPI 版本](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![测试](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![覆盖率](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI 下载量](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![许可证](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Star](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**构建生产级 AI 智能体。停止编写基础设施样板代码。**

[官方网站](https://hedimanai.vercel.app/) · [文档说明](https://hedimanai.vercel.app/projects/toolops.html) · [快速开始](#🚀-快速开始) · [更新日志](CHANGELOG.md)

</div>

---

## ⚡ 30秒介绍

> **“ToolOps 对于 AI 工具而言，就像 Service Mesh（服务网格）对于微服务一样。”**

当您构建 AI 智能体时，外部调用（大语言模型、API、数据库）通常是**昂贵**、**不可靠**且**缓慢**的。
ToolOps 消除了这些样板代码。它是一个与框架无关的中间件 SDK，通过单个装饰器包装任何 Python 函数，瞬间为其提供缓存、弹性、可观测性和并发控制能力。

```python
# ToolOps 之前：80多行缓存管理、重试逻辑、熔断器代码……

# ToolOps 之后：
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # 自动实现缓存、重试和追踪
```

### 🚀 性能基准与影响
- 通过语义缓存（Semantic Caching），**大语言模型（LLM）调用减少 90%**。
- 每次工具执行的**额外开销 <5ms**。
- 您的核心业务逻辑**代码 0 更改**。

---

## ⚖️ 为什么选择 ToolOps？

每位智能体开发者在从演示阶段走向生产环境时都会遇到瓶颈。以下是 ToolOps 与标准替代方案的对比：

| 功能特性 | 标准 `@lru_cache` | 框架原生 | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **原生 Async / `await` 支持** | ❌ | ✅ | ✅ 原生支持 |
| **语义缓存 (基于含义感知)** | ❌ | ⚠️ 基础版 | ✅ 高级词向量 |
| **分布式 / 持久化缓存** | ❌ | ⚠️ 视情况而定 | ✅ Postgres, 文件 |
| **熔断器 (Circuit Breaker)** | ❌ | ❌ | ✅ 原生支持 |
| **带退避的自动重试** | ❌ | ⚠️ 需插件 | ✅ 原生支持 |
| **请求合并 (防雪崩效应)** | ❌ | ❌ | ✅ 原生支持 |
| **错误时使用过期缓存 (降级)** | ❌ | ❌ | ✅ 原生支持 |
| **安全性 (SHA-256 密钥, 自动脱敏)**| ❌ | ❌ | ✅ 原生支持 |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ 需回调 | ✅ 原生支持 |
| **框架无关** | ✅ | ❌ 强绑定 | ✅ 100% 通用 |

---

## 📦 安装

ToolOps 使用模块化的安装系统。核心包**零外部依赖**。您只需安装所需的部分。

### 快速参考

| 安装命令 | 您将获得 | 使用场景 |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | 完整功能集 | **生产环境推荐** |
| `pip install toolops` | 仅核心 SDK | 刚开始使用，无需额外功能 |

### 💻 操作系统指南

我们强烈建议您在虚拟环境中隔离您的项目。

#### 🐧 Linux & 🍎 macOS
```bash
# 1. 创建并激活虚拟环境
python -m venv .venv
source .venv/bin/activate

# 2. 安装 ToolOps（bash/zsh 需要引号）
pip install "toolops[all]"

# 3. 验证安装
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. 安装 ToolOps
pip install "toolops[all]"

# 3. 验证安装
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. 创建并激活虚拟环境
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. 安装 ToolOps（使用双引号）
pip install "toolops[all]"

:: 3. 验证安装
toolops doctor
```

---

## 🚀 快速开始

这个极简示例将引导您在 2 分钟内完成安装，并拥有一个具备缓存和弹性的可用工具。

```python
# 导入模块
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# 步骤 1：注册一个缓存后端（只需在启动时执行一次）
cache_manager.register("memory", MemoryCache(), is_default=True)


# 步骤 2：对于读取操作，使用 @readonly 装饰器装饰任何异步函数
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # 模拟外部 API 调用
    return {"city": city, "temp": 22, "condition": "sunny"}


# 步骤 3：对于写入操作，使用 @sideeffect 装饰器（无缓存，但受保护）
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # 模拟发送通知
    print(f"警报已发送: {message}")
    return True


async def main():
    # 第一次调用会访问 API（实时）
    result = await fetch_weather("Paris")
    print(f"第一次调用 (实时): {result}")

    # 第二次调用由缓存提供服务 — 延迟 <5ms，0 次 API 调用
    result = await fetch_weather("Paris")
    print(f"第二次调用 (缓存): {result}")

    # 带有熔断器保护的写入操作
    await send_alert("Agent 成功完成任务。")

asyncio.run(main())
```

---

## 🧠 核心概念

### 1. 缓存后端 (Cache Backends)

在应用程序启动时注册一次后端，然后通过名称引用它们。ToolOps 支持同时使用多个后端。

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# 内存缓存：速度最快，重启后清除，无依赖
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres 缓存：重启后持久化，可跨进程共享
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# 语义缓存：通过向量（embeddings）按语义匹配，而不是简单的字符串相等
# 最高可减少 90% 的 LLM 调用
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. 弹性模式 (Resilience Patterns)

ToolOps 开箱即用地提供了经过实战检验的强大弹性机制。

- **熔断器 (Circuit Breaker)**：防止不断请求故障服务并导致级联故障。
- **错误时降级 (Stale-if-Error)**：如果实时 API 调用失败，则返回最后已知的有效缓存值。
- **请求合并 (Request Coalescing)**：如果 50 个智能体同时调用同一个端点，ToolOps 只会执行**一次**真实的 API 调用，并将结果广播给所有请求。

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # API 失败时降级
    circuit_breaker = True      # 保护底层服务
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. 架构与安全性 (v0.2.0)

ToolOps v0.2.0 引入了企业级架构：

- **中间件流水线 (Middleware Pipeline)**：原本的单体装饰器已重构为可组合的流水线（日志记录、缓存、熔断器、重试、请求合并、降级）。
- **SHA-256 缓存键哈希**：所有缓存键都经过严格的哈希处理。缓存存储中不会暴露任何敏感数据（令牌、PII 等）。
- **参数自动脱敏**：在结构化日志中，包含敏感关键字（`token`、`password`、`secret` 等）的工具参数会自动被脱敏为 `***MASKED***`。

---

## 📊 可观测性

ToolOps 会自动对每个工具调用进行监控插桩。

### OpenTelemetry (OTEL) & Prometheus

**需要执行：** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# 指向任何兼容 OTEL 的后端 (Jaeger, Datadog, Honeycomb 等)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# 暴露 Prometheus 监控指标
configure_prometheus(port=8000)
```

暴露的关键指标包括 `toolops_cache_hits_total`、`toolops_tool_latency_seconds` 和 `toolops_circuit_opens_total`。

---

## 🔌 框架集成

ToolOps 可以装饰普通的 Python 异步函数，使其与您最喜欢的智能体框架 **100% 兼容**。

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """搜索网络并返回摘要。"""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "获取并缓存研究数据。"

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# 自动生成完全类型化的 MCP 工具定义
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ 命令行参考 (CLI)

ToolOps 附带一个命令行工具，用于管理您的缓存基础设施。

```bash
# 检查所有已注册后端的运行状况
toolops doctor

# 查看应用程序的实时缓存统计信息
toolops stats --app my_app:setup_toolops

# 清除特定后端的缓存
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 参与贡献

ToolOps 为社区而建，由社区共建。

- 阅读我们的[贡献指南](CONTRIBUTING.md)以开始。
- 了解我们的[行为准则](CODE_OF_CONDUCT.md)。
- 通过我们的[安全策略](SECURITY.md)安全地报告安全问题。

---

## 💬 社区与联系方式

我们正在积极构建 AI 智能体基础设施的未来。快来加入讨论吧！

- **创始人：** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **报告 Bug 与提交功能需求：** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **电子邮箱：** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — 专为生产环境打造。</b><br>
遵循 <a href="LICENSE">Apache 2.0</a> 许可证
</div>
