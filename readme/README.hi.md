<div align="center">

[🇬🇧 English](../README.md) | [🇫🇷 Français](README.fr.md) | [🇨🇳 中文](README.zh.md) | [🇯🇵 日本語](README.ja.md) | [🇪🇸 Español](README.es.md) | [🇩🇪 Deutsch](README.de.md) | [🇵🇹 Português](README.pt.md) | [🇰🇷 한국어](README.ko.md) | [🇷🇺 Русский](README.ru.md) | [🇮🇳 हिन्दी](README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### एआई एजेंट टूल्स (AI Agent Tools) के लिए औद्योगिक-स्तर (Industrial-Grade) की रेजिलिएंस और एफिशिएंसी लेयर

[![PyPI संस्करण](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![टेस्ट](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![कवरेज](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI डाउनलोड्स](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![लाइसेंस](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub स्टार्स](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**प्रोडक्शन के लिए तैयार (production-ready) एआई एजेंट बनाएं। इंफ्रास्ट्रक्चर का बॉयलरप्लेट (boilerplate) कोड लिखना बंद करें।**

[वेबसाइट](https://hedimanai.vercel.app/) · [दस्तावेज़](https://hedimanai.vercel.app/projects/toolops.html) · [त्वरित शुरुआत (Quickstart)](#🚀-त्वरित-शुरुआत-quickstart) · [चेंजलॉग](CHANGELOG.md)

</div>

---

## ⚡ 30-सेकंड की पिच

> **"एआई टूल्स (AI Tools) के लिए ToolOps वही है जो माइक्रोसर्विसेज (Microservices) के लिए सर्विस मेश (Service Mesh) है।"**

जब आप एआई एजेंट बनाते हैं, तो बाहरी कॉल (LLMs, APIs, DBs) **महंगे**, **अविश्वसनीय** और **धीमे** होते हैं।
ToolOps इस बॉयलरप्लेट (boilerplate) को खत्म कर देता है। यह एक फ्रेमवर्क-अज्ञेयवादी (framework-agnostic) मिडलवेयर SDK है जो किसी भी पायथन फ़ंक्शन को एक ही डेकोरेटर (decorator) में रैप (wrap) करता है, और इसे कैशिंग (caching), रेजिलिएंस (resilience), ऑब्ज़र्वेबिलिटी (observability), और कंक्यूरेंसी (concurrency) कंट्रोल के साथ तुरंत अपग्रेड करता है।

```python
# ToolOps से पहले: कैश मैनेजर, रीट्राई (retry) लॉजिक, सर्किट ब्रेकर... की 80+ लाइनें

# ToolOps के बाद:
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # स्वचालित रूप से कैश्ड (cached), रीट्राई (retried) और ट्रैक्ड (traced)
```

### 🚀 बेंचमार्क और प्रभाव
- सिमेंटिक कैशिंग (Semantic Caching) के माध्यम से **LLM कॉल्स में 90% की कमी**।
- प्रति टूल निष्पादन पर **<5ms ओवरहेड**।
- आपके कोर बिज़नेस लॉजिक में **0 कोड बदलाव**।

---

## ⚖️ ToolOps क्यों?

हर एजेंट डेवलपर डेमो (demo) से प्रोडक्शन (production) में जाते समय एक दीवार से टकराता है। यहां बताया गया है कि ToolOps मानक विकल्पों की तुलना में कैसा प्रदर्शन करता है:

| विशेषता | मानक `@lru_cache` | फ्रेमवर्क-नेटिव | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **नेटिव Async / `await` सपोर्ट** | ❌ | ✅ | ✅ नेटिव |
| **सिमेंटिक (अर्थ-आधारित) कैश** | ❌ | ⚠️ बेसिक | ✅ एडवांस्ड एम्बेडिंग |
| **डिस्ट्रिब्यूटेड / पर्सिस्टेंट कैश** | ❌ | ⚠️ भिन्न होता है | ✅ Postgres, फ़ाइल |
| **सर्किट ब्रेकर (Circuit Breaker)** | ❌ | ❌ | ✅ नेटिव |
| **बैकऑफ़ (Backoff) के साथ ऑटोमैटिक रीट्राई** | ❌ | ⚠️ प्लगइन आवश्यक | ✅ नेटिव |
| **रिक्वेस्ट कोलिसिंग (Anti-Thundering Herd)**| ❌ | ❌ | ✅ नेटिव |
| **Stale-if-error फॉलबैक (त्रुटि पर पुराना कैश)** | ❌ | ❌ | ✅ नेटिव |
| **सुरक्षा (SHA-256 कुंजी, ऑटो-मास्किंग)**| ❌ | ❌ | ✅ नेटिव |
| **OpenTelemetry और Prometheus** | ❌ | ⚠️ कॉलबैक आवश्यक | ✅ नेटिव |
| **फ्रेमवर्क-अज्ञेयवादी (Agnostic)** | ✅ | ❌ लॉक-इन | ✅ 100% यूनिवर्सल |

---

## 📦 स्थापना (Installation)

ToolOps एक मॉड्यूलर इंस्टॉलेशन सिस्टम का उपयोग करता है। कोर पैकेज में **शून्य बाहरी निर्भरताएँ (zero external dependencies)** हैं। आप केवल वही इंस्टॉल करते हैं जिसकी आपको आवश्यकता है।

### त्वरित संदर्भ

| स्थापना कमांड | आपको क्या मिलता है | कब उपयोग करें |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | पूर्ण फीचर सेट | **प्रोडक्शन के लिए अनुशंसित** |
| `pip install toolops` | केवल कोर SDK | शुरुआत करने के लिए, अतिरिक्त चीज़ों की आवश्यकता नहीं है |

### 💻 ओएस-विशिष्ट (OS-Specific) गाइड

हम आपके प्रोजेक्ट को वर्चुअल एनवायरनमेंट (virtual environment) में अलग रखने की पुरज़ोर सलाह देते हैं।

#### 🐧 Linux & 🍎 macOS
```bash
# 1. वर्चुअल एनवायरनमेंट बनाएं और सक्रिय करें
python -m venv .venv
source .venv/bin/activate

# 2. ToolOps इंस्टॉल करें (bash/zsh के लिए उद्धरण/quotes आवश्यक हैं)
pip install "toolops[all]"

# 3. इंस्टॉलेशन की जांच करें
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. वर्चुअल एनवायरनमेंट बनाएं और सक्रिय करें
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. ToolOps इंस्टॉल करें
pip install "toolops[all]"

# 3. इंस्टॉलेशन की जांच करें
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. वर्चुअल एनवायरनमेंट बनाएं और सक्रिय करें
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. ToolOps इंस्टॉल करें (दोहरे उद्धरण चिह्न का उपयोग करें)
pip install "toolops[all]"

:: 3. इंस्टॉलेशन की जांच करें
toolops doctor
```

---

## 🚀 त्वरित शुरुआत (Quickstart)

यह न्यूनतम उदाहरण आपको 2 मिनट से भी कम समय में इंस्टॉलेशन से लेकर एक काम करने वाले, कैश्ड (cached) और रेजिलिएंट (resilient) टूल तक ले जाता है।

```python
# आयात (Imports)
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# चरण 1: एक कैश बैकएंड रजिस्टर करें (स्टार्टअप पर इसे एक बार करें)
cache_manager.register("memory", MemoryCache(), is_default=True)


# चरण 2: पढ़ने (read) के संचालन के लिए किसी भी एसिंक (async) फ़ंक्शन को @readonly के साथ डेकोरेट करें
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # एक बाहरी API कॉल का अनुकरण (Simulate) करें
    return {"city": city, "temp": 22, "condition": "sunny"}


# चरण 3: लिखने (write) के संचालन को @sideeffect के साथ डेकोरेट करें (कैशिंग नहीं, लेकिन सुरक्षित)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # सूचना भेजने का अनुकरण (Simulate) करें
    print(f"सूचना भेजी गई: {message}")
    return True


async def main():
    # पहली कॉल API तक पहुँचती है (लाइव)
    result = await fetch_weather("Paris")
    print(f"पहली कॉल (लाइव): {result}")

    # दूसरी कॉल कैश से सर्व की जाती है — <5ms विलंबता (latency), 0 API कॉल
    result = await fetch_weather("Paris")
    print(f"दूसरी कॉल (कैश): {result}")

    # सर्किट ब्रेकर सुरक्षा के साथ लिखने (write) का संचालन
    await send_alert("एजेंट सफलतापूर्वक पूरा हुआ।")

asyncio.run(main())
```

---

## 🧠 मुख्य अवधारणाएँ (Core Concepts)

### 1. कैश बैकएंड्स (Cache Backends)

एप्लिकेशन स्टार्टअप पर एक बार बैकएंड्स को रजिस्टर करें, फिर नाम से उनका संदर्भ लें। ToolOps एक साथ कई बैकएंड्स का समर्थन करता है।

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# इन-मेमोरी: सबसे तेज़, रीस्टार्ट होने पर साफ़ हो जाता है, कोई निर्भरता (dependencies) नहीं
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres: रीस्टार्ट होने के बाद भी पर्सिस्टेंट (स्थायी), प्रक्रियाओं के बीच साझा करने योग्य
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# सिमेंटिक: सटीक स्ट्रिंग समानता के बजाय अर्थ के आधार पर मिलान करने के लिए वेक्टर एम्बेडिंग
# LLM कॉल को 90% तक कम करता है
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. रेजिलिएंस पैटर्न (Resilience Patterns)

ToolOps बॉक्स से बाहर (out of the box) मजबूत, युद्ध-परीक्षणित (battle-tested) रेजिलिएंस प्रदान करता है।

- **सर्किट ब्रेकर (Circuit Breaker)**: किसी विफल हो रही सर्विस पर बार-बार रिक्वेस्ट भेजने से रोकता है और कैस्केडिंग विफलता को टालता है।
- **Stale-if-Error**: यदि लाइव API कॉल विफल हो जाती है, तो पिछली ज्ञात अच्छी कैश्ड (cached) वैल्यू सर्व करता है।
- **रिक्वेस्ट कोलिसिंग (Request Coalescing)**: यदि 50 एजेंट एक ही समय में एक ही एंडपॉइंट (endpoint) को कॉल करते हैं, तो ToolOps वास्तविक API कॉल को **केवल एक बार** निष्पादित करता है और परिणाम को सभी के लिए मल्टीकास्ट (multicast) करता है।

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # API विफल होने पर फॉलबैक (Fallback)
    circuit_breaker = True      # अंतर्निहित (underlying) सर्विस को सुरक्षित रखें
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. आर्किटेक्चर और सुरक्षा (v0.2.0)

ToolOps v0.2.0 एक एंटरप्राइज़-ग्रेड आर्किटेक्चर पेश करता है:

- **मिडलवेयर पाइपलाइन**: मोनोलिथिक डेकोरेटर को एक कंपोज़ेबल पाइपलाइन (`लॉगिंग`, `कैश`, `सर्किटब्रेकर`, `रीट्राई`, `कोलिसिंग`, `फॉलबैक`) में रिफ़ैक्टर किया गया है।
- **SHA-256 कैश की (Key) हैशिंग**: सभी कैश कुंजियों (keys) को सख्ती से हैश किया जाता है। कैश स्टोर में कोई भी संवेदनशील डेटा (टोकन, PII) उजागर नहीं होता है।
- **स्वचालित पैरामीटर मास्किंग**: संवेदनशील कीवर्ड (`token`, `password`, `secret`, आदि) वाले टूल आर्गुमेंट्स स्वचालित रूप से संरचित लॉग (structured logs) में `***MASKED***` के रूप में मास्क किए जाते हैं।

---

## 📊 ऑब्ज़र्वेबिलिटी (Observability)

ToolOps स्वचालित रूप से प्रत्येक टूल कॉल को इंस्ट्रूमेंट (instrument) करता है।

### OpenTelemetry (OTEL) और Prometheus

**आवश्यकताएँ:** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# किसी भी OTEL-संगत (compatible) बैकएंड (Jaeger, Datadog, Honeycomb, आदि) को पॉइंट करें
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Prometheus मेट्रिक्स एक्सपोज़ करें
configure_prometheus(port=8000)
```

एक्सपोज़ की गई प्रमुख मेट्रिक्स (metrics) में `toolops_cache_hits_total`, `toolops_tool_latency_seconds`, और `toolops_circuit_opens_total` शामिल हैं।

---

## 🔌 फ्रेमवर्क एकीकरण (Integration)

ToolOps सादे पायथन एसिंक (async) फ़ंक्शंस को डेकोरेट करता है, जिससे यह आपके पसंदीदा एजेंट फ्रेमवर्क के साथ **100% संगत (compatible)** हो जाता है।

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """वेब पर खोजें और सारांश (summary) लौटाएं।"""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "शोध डेटा को फेच (fetch) और कैश (cache) करता है।"

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# स्वचालित रूप से एक पूरी तरह से टाइप की गई MCP टूल परिभाषा उत्पन्न करें
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ CLI संदर्भ

ToolOps आपके कैश इंफ्रास्ट्रक्चर को प्रबंधित करने के लिए कमांड-लाइन टूल के साथ आता है।

```bash
# सभी पंजीकृत (registered) बैकएंड्स के स्वास्थ्य (health) की जाँच करें
toolops doctor

# किसी ऐप के लिए लाइव कैश आँकड़े देखें
toolops stats --app my_app:setup_toolops

# किसी विशिष्ट बैकएंड का कैश साफ़ करें
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 योगदान (Contributing)

ToolOps समुदाय (community) के लिए, समुदाय द्वारा बनाया गया है।

- आरंभ करने के लिए हमारी [योगदान मार्गदर्शिका](CONTRIBUTING.md) की समीक्षा करें।
- [आचार संहिता (Code of Conduct)](CODE_OF_CONDUCT.md) देखें।
- हमारी [सुरक्षा नीति (Security Policy)](SECURITY.md) के माध्यम से सुरक्षा मुद्दों (security issues) की सुरक्षित रूप से रिपोर्ट करें।

---

## 💬 समुदाय और संपर्क

हम एआई एजेंट इंफ्रास्ट्रक्चर के भविष्य का सक्रिय रूप से निर्माण कर रहे हैं। चर्चा में शामिल हों!

- **निर्माता (Creator):** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **बग रिपोर्ट करें और सुविधा अनुरोध (Feature Requests):** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **ईमेल:** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — प्रोडक्शन के लिए निर्मित।</b><br>
<a href="LICENSE">Apache 2.0</a> के तहत लाइसेंस प्राप्त।
</div>
