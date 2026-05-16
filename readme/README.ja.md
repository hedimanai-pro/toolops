<div align="center">

[🇬🇧 English](../README.md) | [🇫🇷 Français](README.fr.md) | [🇨🇳 中文](README.zh.md) | [🇯🇵 日本語](README.ja.md) | [🇪🇸 Español](README.es.md) | [🇩🇪 Deutsch](README.de.md) | [🇵🇹 Português](README.pt.md) | [🇰🇷 한국어](README.ko.md) | [🇷🇺 Русский](README.ru.md) | [🇮🇳 हिन्दी](README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="ToolOps Logo">

# ToolOps

### AIエージェントツールのための産業グレードの回復力と効率性レイヤー

[![PyPI バージョン](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![テスト](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![カバレッジ](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![PyPI ダウンロード](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![ライセンス](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![GitHub Star](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**本番稼働可能なAIエージェントを構築する。インフラストラクチャの定型コードを書くのはもうやめましょう。**

[ウェブサイト](https://hedimanai.vercel.app/) · [ドキュメント](https://hedimanai.vercel.app/projects/toolops.html) · [クイックスタート](#🚀-クイックスタート-quickstart) · [更新履歴](CHANGELOG.md)

</div>

---

## ⚡ 30秒でわかる概要 (30-Second Pitch)

> **「ToolOpsがAIツールにもたらすものは、サービスメッシュがマイクロサービスにもたらすものと同じです。」**

AIエージェントを構築する際、外部呼び出し（LLM、API、データベース）は**高価**で、**信頼性が低く**、**低速**です。
ToolOpsはこのようなボイラープレート（定型コード）を排除します。これはフレームワークに依存しないミドルウェアSDKであり、任意のPython関数を1つのデコレータでラップするだけで、キャッシング、回復力（レジリエンス）、可観測性（オブザーバビリティ）、同時実行制御を即座に追加してアップグレードします。

```python
# ToolOps導入前：キャッシュ管理、再試行ロジック、サーキットブレーカーなど、80行以上のコード...

# ToolOps導入後：
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # 自動的にキャッシュ、再試行、トレースされます
```

### 🚀 ベンチマークと影響 (Benchmarks & Impact)
- セマンティックキャッシュによる**LLM呼び出しの90%削減**。
- ツール実行あたりの**オーバーヘッド <5ms**。
- コアビジネスロジックの**コード変更ゼロ (0)**。

---

## ⚖️ なぜToolOpsを選ぶのか？ (Why ToolOps?)

すべてのエージェント開発者は、デモから本番環境へ移行する際に壁にぶつかります。ToolOpsと標準的な代替手段の比較は以下の通りです。

| 機能 | 標準 `@lru_cache` | フレームワークネイティブ | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **ネイティブ Async / `await` サポート** | ❌ | ✅ | ✅ ネイティブサポート |
| **セマンティックキャッシュ (意味に基づくキャッシュ)** | ❌ | ⚠️ 基本的 | ✅ 高度なエンベディング |
| **分散型 / 永続化キャッシュ** | ❌ | ⚠️ 様々 | ✅ Postgres, ファイル |
| **サーキットブレーカー** | ❌ | ❌ | ✅ ネイティブサポート |
| **バックオフ付き自動再試行** | ❌ | ⚠️ プラグイン必須 | ✅ ネイティブサポート |
| **リクエスト合体 (Thundering Herd対策)**| ❌ | ❌ | ✅ ネイティブサポート |
| **エラー時の古いキャッシュの提供 (フォールバック)** | ❌ | ❌ | ✅ ネイティブサポート |
| **セキュリティ (SHA-256キー, 自動マスキング)**| ❌ | ❌ | ✅ ネイティブサポート |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ コールバック必須 | ✅ ネイティブサポート |
| **フレームワーク非依存** | ✅ | ❌ ロックイン | ✅ 100% ユニバーサル |

---

## 📦 インストール (Installation)

ToolOpsはモジュール式のインストールシステムを採用しています。コアパッケージには**外部依存関係が一切ありません**。必要なものだけをインストールできます。

### クイックリファレンス

| インストールコマンド | 得られるもの | 使用シナリオ |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | 全機能セット | **本番環境で推奨** |
| `pip install toolops` | コアSDKのみ | 使い始めの段階で、追加機能が不要な場合 |

### 💻 OS別のガイド (OS-Specific Guides)

仮想環境でプロジェクトを分離することを強くお勧めします。

#### 🐧 Linux & 🍎 macOS
```bash
# 1. 仮想環境を作成してアクティブ化する
python -m venv .venv
source .venv/bin/activate

# 2. ToolOpsをインストールする（bash/zshでは引用符が必要です）
pip install "toolops[all]"

# 3. インストールを確認する
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. 仮想環境を作成してアクティブ化する
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. ToolOpsをインストールする
pip install "toolops[all]"

# 3. インストールを確認する
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. 仮想環境を作成してアクティブ化する
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. ToolOpsをインストールする（ダブルクォーテーションを使用してください）
pip install "toolops[all]"

:: 3. インストールを確認する
toolops doctor
```

---

## 🚀 クイックスタート (Quickstart)

この最小限の例を使えば、インストールから、キャッシュされ、回復力のあるツールを機能させるまで2分以内で完了します。

```python
# インポート
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# ステップ 1：キャッシュバックエンドを登録する（起動時に1回だけ実行）
cache_manager.register("memory", MemoryCache(), is_default=True)


# ステップ 2：読み取り操作を行う任意の非同期関数を @readonly でデコレートする
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # 外部API呼び出しをシミュレートする
    return {"city": city, "temp": 22, "condition": "sunny"}


# ステップ 3：書き込み操作を @sideeffect でデコレートする（キャッシュなし、ただし保護される）
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # 通知の送信をシミュレートする
    print(f"アラートが送信されました: {message}")
    return True


async def main():
    # 1回目の呼び出しはAPIにアクセスします（リアルタイム）
    result = await fetch_weather("Paris")
    print(f"1回目の呼び出し (リアルタイム): {result}")

    # 2回目の呼び出しはキャッシュから提供されます — 遅延 <5ms、API呼び出し0回
    result = await fetch_weather("Paris")
    print(f"2回目の呼び出し (キャッシュ): {result}")

    # サーキットブレーカーで保護された書き込み操作
    await send_alert("エージェントが正常に完了しました。")

asyncio.run(main())
```

---

## 🧠 コアコンセプト (Core Concepts)

### 1. キャッシュバックエンド (Cache Backends)

アプリケーションの起動時にバックエンドを1回登録し、名前で参照します。ToolOpsは複数のバックエンドを同時にサポートしています。

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# インメモリ：最速、再起動時にクリアされる、依存関係なし
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres：再起動後も永続化され、プロセス間で共有可能
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# セマンティック：単なる文字列の一致ではなく、意味によって一致させるベクトルエンベディング
# LLMの呼び出しを最大90%削減
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. 回復力パターン (Resilience Patterns)

ToolOpsは、すぐに使える堅牢で実戦テスト済みの回復力（レジリエンス）を提供します。

- **サーキットブレーカー (Circuit Breaker)**：障害が発生しているサービスへの連続したアクセスを防ぎ、連鎖的な障害を回避します。
- **エラー時の古いキャッシュ (Stale-if-Error)**：リアルタイムのAPI呼び出しが失敗した場合、最後に確認された正常なキャッシュ値を提供します。
- **リクエスト合体 (Request Coalescing)**：50個のエージェントが同じエンドポイントを同時に呼び出した場合、ToolOpsは実際のAPI呼び出しを**1回だけ**実行し、その結果をすべてのエージェントにマルチキャスト（一斉配信）します。

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # API障害時のフォールバック
    circuit_breaker = True      # 基礎となるサービスを保護する
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. アーキテクチャとセキュリティ (v0.2.0)

ToolOps v0.2.0では、エンタープライズグレードのアーキテクチャが導入されています。

- **ミドルウェア・パイプライン**：モノリシックなデコレータが、構成可能なパイプライン（ロギング、キャッシュ、サーキットブレーカー、再試行、合体、フォールバック）にリファクタリングされました。
- **SHA-256 キャッシュキーのハッシュ化**：すべてのキャッシュキーは厳密にハッシュ化されます。トークンや個人を特定できる情報（PII）などの機密データがキャッシュストアに公開されることはありません。
- **パラメータの自動マスキング**：機密キーワード（`token`、`password`、`secret` など）を含むツール引数は、構造化ログ内で自動的に `***MASKED***` としてマスクされます。

---

## 📊 可観測性 (Observability)

ToolOpsは、すべてのツールの呼び出しを自動的に計測（計装）します。

### OpenTelemetry (OTEL) & Prometheus

**必要要件：** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# OTEL互換のバックエンド（Jaeger、Datadog、Honeycombなど）を指定する
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Prometheusメトリクスを公開する
configure_prometheus(port=8000)
```

公開される主要なメトリクスには、`toolops_cache_hits_total`、`toolops_tool_latency_seconds`、および `toolops_circuit_opens_total` が含まれます。

---

## 🔌 フレームワーク統合 (Framework Integration)

ToolOpsは通常のPython非同期関数をデコレートするため、お気に入りのエージェントフレームワークと**100%の互換性**を持ちます。

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """ウェブを検索して要約を返す。"""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "調査データを取得してキャッシュする。"

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# 完全に型付けされたMCPツール定義を自動的に生成する
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ CLIリファレンス (コマンドラインインターフェース)

ToolOpsには、キャッシュインフラストラクチャを管理するためのコマンドラインツールが付属しています。

```bash
# 登録されているすべてのバックエンドの正常性を確認する
toolops doctor

# アプリのリアルタイムのキャッシュ統計を表示する
toolops stats --app my_app:setup_toolops

# 特定のバックエンドのキャッシュをクリアする
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 コントリビューション (貢献)

ToolOpsはコミュニティによって、コミュニティのために構築されています。

- まずは[コントリビューティングガイド](CONTRIBUTING.md)をご覧ください。
- [行動規範](CODE_OF_CONDUCT.md)をご確認ください。
- セキュリティ上の問題は、[セキュリティポリシー](SECURITY.md)を通じて安全に報告してください。

---

## 💬 コミュニティと連絡先

私たちはAIエージェントインフラストラクチャの未来を積極的に構築しています。ぜひ議論に参加してください！

- **開発者：** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **バグの報告と機能の要望：** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **Eメール：** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — 本番環境向けに構築されています。</b><br>
<a href="LICENSE">Apache 2.0</a> ライセンスの下で提供されます。
</div>
