<div align="center">

[🇬🇧 English](https://github.com/hedimanai-pro/toolops/blob/main/README.md) | [🇫🇷 Français](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.fr.md) | [🇨🇳 中文](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.zh.md) | [🇯🇵 日本語](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ja.md) | [🇪🇸 Español](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.es.md) | [🇩🇪 Deutsch](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.de.md) | [🇵🇹 Português](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.pt.md) | [🇰🇷 한국어](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ko.md) | [🇷🇺 Русский](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.ru.md) | [🇮🇳 हिन्दी](https://github.com/hedimanai-pro/toolops/blob/main/readme/README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="Logo ToolOps">

# ToolOps

### A Camada de Resiliência e Eficiência de Nível Industrial para Ferramentas de Agentes de IA

[![Versão PyPI](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Testes](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Cobertura](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![Downloads PyPI](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Licença](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![Estrelas GitHub](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Construa agentes de IA prontos para produção. Pare de escrever código de infraestrutura repetitivo.**

[Site](https://hedimanai.vercel.app/) · [Documentação](https://hedimanai.vercel.app/projects/toolops.html) · [Início Rápido](#🚀-início-rápido) · [Registro de Alterações](CHANGELOG.md)

</div>

---

## ⚡ Resumo em 30 Segundos

> **"O ToolOps é para as Ferramentas de IA o que um Service Mesh é para os Microsserviços."**

Quando você constrói agentes de IA, as chamadas externas (LLMs, APIs, bancos de dados) são **caras**, **não confiáveis** e **lentas**.
O ToolOps elimina esse código repetitivo (boilerplate). É um SDK de middleware agnóstico de framework que envolve qualquer função Python em um único decorador, atualizando-a instantaneamente com cache, resiliência, observabilidade e controle de concorrência.

```python
# ANTES do ToolOps: mais de 80 linhas de gerenciadores de cache, lógica de repetição, circuit breakers...

# DEPOIS do ToolOps:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Armazenado em cache, repetido e rastreado automaticamente
```

### 🚀 Benchmarks e Impacto
- **90% de redução nas chamadas a LLMs** através do Cache Semântico.
- **<5ms de sobrecarga (overhead)** por execução da ferramenta.
- **0 mudanças de código** na sua lógica de negócios principal.

---

## ⚖️ Por que o ToolOps?

Todo desenvolvedor de agentes bate de frente com um muro ao passar da demonstração (demo) para a produção. Veja como o ToolOps se compara às alternativas padrão:

| Característica | `@lru_cache` padrão | Nativo do Framework | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **Suporte nativo Async / `await`** | ❌ | ✅ | ✅ Nativo |
| **Cache semântico (baseado no significado)** | ❌ | ⚠️ Básico | ✅ Embeddings Avançados |
| **Cache distribuído / persistente** | ❌ | ⚠️ Varia | ✅ Postgres, Arquivo |
| **Circuit Breaker** | ❌ | ❌ | ✅ Nativo |
| **Repetições automáticas com Backoff** | ❌ | ⚠️ Requer plugin | ✅ Nativo |
| **Fusão de Requisições (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Nativo |
| **Fallback Stale-if-error (Cache em caso de erro)** | ❌ | ❌ | ✅ Nativo |
| **Segurança (Chaves SHA-256, Auto-mascaramento)**| ❌ | ❌ | ✅ Nativo |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Requer callbacks | ✅ Nativo |
| **Agnóstico de Framework** | ✅ | ❌ Bloqueado | ✅ 100% Universal |

---

## 📦 Instalação

O ToolOps usa um sistema de instalação modular. O pacote principal possui **zero dependências externas**. Você só instala o que precisa.

### Referência Rápida

| Comando de instalação | O que você obtém | Quando usar |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | Conjunto completo de recursos | **Recomendado para produção** |
| `pip install toolops` | Apenas o SDK principal | Para começar, sem necessidade de extras |

### 💻 Guias Específicos por Sistema Operacional

Recomendamos fortemente isolar seu projeto em um ambiente virtual.

#### 🐧 Linux & 🍎 macOS
```bash
# 1. Crie e ative um ambiente virtual
python -m venv .venv
source .venv/bin/activate

# 2. Instale o ToolOps (aspas são obrigatórias para bash/zsh)
pip install "toolops[all]"

# 3. Verifique a instalação
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Instale o ToolOps
pip install "toolops[all]"

# 3. Verifique a instalação
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. Crie e ative um ambiente virtual
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. Instale o ToolOps (use aspas duplas)
pip install "toolops[all]"

:: 3. Verifique a instalação
toolops doctor
```

---

## 🚀 Início Rápido

Este exemplo mínimo leva você da instalação a uma ferramenta funcional, com cache e resiliente, em menos de 2 minutos.

```python
# Importações
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Passo 1: Registre um backend de cache (faça isso uma vez na inicialização)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Passo 2: Decore qualquer função assíncrona com @readonly para operações de leitura
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simular uma chamada de API externa
    return {"city": city, "temp": 22, "condition": "sunny"}


# Passo 3: Decore as operações de gravação com @sideeffect (sem cache, mas protegido)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Simular o envio de uma notificação
    print(f"Alerta enviado: {message}")
    return True


async def main():
    # A primeira chamada atinge a API (ao vivo)
    result = await fetch_weather("Paris")
    print(f"Primeira chamada (ao vivo): {result}")

    # A segunda chamada é servida a partir do cache — latência <5ms, 0 chamadas de API
    result = await fetch_weather("Paris")
    print(f"Segunda chamada (em cache): {result}")

    # Operação de gravação com proteção de circuit breaker
    await send_alert("O agente foi concluído com sucesso.")

asyncio.run(main())
```

---

## 🧠 Conceitos Principais

### 1. Backends de Cache

Registre os backends uma vez na inicialização do aplicativo e, em seguida, referencie-os por nome. O ToolOps suporta vários backends simultaneamente.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# Em memória: o mais rápido, limpo ao reiniciar, sem dependências
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres: persistente após reinicializações, compartilhável entre processos
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Semântico: embeddings de vetor para corresponder pelo significado, não por igualdade estrita de strings
# Reduz as chamadas de LLMs em até 90%
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. Padrões de Resiliência

O ToolOps fornece resiliência robusta e comprovada em produção de imediato.

- **Circuit Breaker**: Evita bombardear um serviço com falha e causar falhas em cascata.
- **Stale-if-Error**: Serve o último valor válido conhecido em cache se a chamada da API ao vivo falhar.
- **Fusão de Requisições (Request Coalescing)**: Se 50 agentes chamarem o mesmo endpoint simultaneamente, o ToolOps executará a chamada real da API **apenas uma vez** e transmitirá (multicast) o resultado para todos.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Fallback em caso de falha da API
    circuit_breaker = True      # Protege o serviço subjacente
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Arquitetura e Segurança (v0.2.0)

A versão v0.2.0 do ToolOps introduz uma arquitetura de nível corporativo:

- **Pipeline de Middleware**: O decorador monolítico foi refatorado em um pipeline combinável (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`).
- **Hash de Chaves de Cache SHA-256**: Todas as chaves de cache têm hash estrito. Nenhum dado confidencial (tokens, PII) é exposto nos armazenamentos de cache.
- **Mascaramento Automático de Parâmetros**: Argumentos de ferramentas que contêm palavras-chave sensíveis (`token`, `senha`, `segredo`, etc.) são automaticamente mascarados como `***MASKED***` nos logs estruturados.

---

## 📊 Observabilidade

O ToolOps instrumenta cada chamada de ferramenta automaticamente.

### OpenTelemetry (OTEL) & Prometheus

**Requer:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# Aponte para qualquer backend compatível com OTEL (Jaeger, Datadog, Honeycomb, etc.)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Expor métricas do Prometheus
configure_prometheus(port=8000)
```

As principais métricas expostas incluem `toolops_cache_hits_total`, `toolops_tool_latency_seconds` e `toolops_circuit_opens_total`.

---

## 🔌 Integração com Frameworks

O ToolOps decora funções assíncronas simples em Python, tornando-o **100% compatível** com seus frameworks de agentes favoritos.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Pesquisar na web e retornar um resumo."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Busca e armazena em cache dados de pesquisa."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Gerar uma definição de ferramenta MCP totalmente tipada automaticamente
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ Referencia da CLI

O ToolOps vem com uma ferramenta de linha de comando para gerenciar sua infraestrutura de cache.

```bash
# Verificar a integridade de todos os backends registrados
toolops doctor

# Ver estatísticas de cache ao vivo para um aplicativo
toolops stats --app my_app:setup_toolops

# Limpar o cache de um backend específico
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Contribuição

O ToolOps foi desenvolvido para a comunidade, pela comunidade. 

- Revise nosso [Guia de Contribuição](CONTRIBUTING.md) para começar.
- Confira o [Código de Conduta](CODE_OF_CONDUCT.md).
- Relate problemas de segurança com segurança por meio de nossa [Política de Segurança](SECURITY.md).

---

## 💬 Comunidade e Contato

Estamos construindo ativamente o futuro da infraestrutura de agentes de IA. Junte-se à discussão!

- **Criador:** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Relatar Bugs e Solicitar Recursos:** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **E-mail:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Construído para Produção.</b><br>
Licenciado sob <a href="LICENSE">Apache 2.0</a>
</div>
