<div align="center">

[🇬🇧 English](../README.md) | [🇫🇷 Français](README.fr.md) | [🇨🇳 中文](README.zh.md) | [🇯🇵 日本語](README.ja.md) | [🇪🇸 Español](README.es.md) | [🇩🇪 Deutsch](README.de.md) | [🇵🇹 Português](README.pt.md) | [🇰🇷 한국어](README.ko.md) | [🇷🇺 Русский](README.ru.md) | [🇮🇳 हिन्दी](README.hi.md)

</div>
<br/>

<div align="center">

<img src="https://raw.githubusercontent.com/hedimanai-pro/toolops/main/docs/assets/logo.png" width="180" alt="Logo ToolOps">

# ToolOps

### La Couche de Résilience et d'Efficacité de Qualité Industrielle pour les Outils pour Agents IA

[![Version PyPI](https://img.shields.io/pypi/v/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Python](https://img.shields.io/pypi/pyversions/toolops.svg?color=D4A017&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Tests](https://img.shields.io/badge/tests-passing-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops/actions)
[![Couverture](https://img.shields.io/badge/coverage-100%25-success.svg?style=for-the-badge)](https://github.com/hedimanai-pro/toolops)
[![Téléchargements PyPI](https://img.shields.io/pypi/dm/toolops.svg?color=2C7BB6&style=for-the-badge)](https://pypi.org/project/toolops/)
[![Licence](https://img.shields.io/badge/license-Apache%202.0-2C7BB6.svg?style=for-the-badge)](LICENSE)
[![Étoiles GitHub](https://img.shields.io/github/stars/hedimanai-pro/toolops.svg?color=D4A017&style=for-the-badge)](https://github.com/hedimanai-pro/toolops)

**Construisez des agents IA prêts pour la production. Arrêtez d'écrire du code d'infrastructure répétitif.**

[Site Web](https://hedimanai.vercel.app/) · [Documentation](https://hedimanai.vercel.app/projects/toolops.html) · [Démarrage Rapide](#démarrage-rapide) · [Changelog](CHANGELOG.md)

</div>

---

## ⚡ Pitch en 30 Secondes

> **"ToolOps est aux outils IA ce qu'un Service Mesh est aux microservices."**

Lorsque vous construisez des agents IA, les appels externes (LLM, API, bases de données) sont **coûteux**, **peu fiables** et **lents**.
ToolOps élimine ce code répétitif. C'est un SDK middleware agnostique (indépendant du framework) qui enveloppe n'importe quelle fonction Python avec un seul décorateur, l'améliorant instantanément avec de la mise en cache, de la résilience, de l'observabilité et un contrôle de la concurrence.

```python
# AVANT ToolOps : 80+ lignes de gestionnaires de cache, logique de retry, circuit breakers...

# APRÈS ToolOps :
@readonly(cache_backend="semantic", cache_ttl=3600, retry_count=3)
async def ask_llm(query: str) -> str:
    return await llm.complete(query)  # Automatiquement mis en cache, réessayé et tracé
```

### 🚀 Benchmarks & Impact
- **90% de réduction des appels LLM** via le Cache Sémantique.
- **<5ms de surcharge (overhead)** par exécution d'outil.
- **0 changement de code** dans votre logique métier principale.

---

## ⚖️ Pourquoi ToolOps ?

Chaque développeur d'agents se heurte à un mur lors du passage de la démo à la production. Voici comment ToolOps se compare aux alternatives standards :

| Fonctionnalité | `@lru_cache` standard | Natif au Framework | 🚀 ToolOps v0.2.0 |
| :--- | :---: | :---: | :---: |
| **Support natif Async / `await`** | ❌ | ✅ | ✅ Natif |
| **Cache sémantique (basé sur le sens)** | ❌ | ⚠️ Basique | ✅ Embeddings Avancés |
| **Cache distribué / persistant** | ❌ | ⚠️ Variable | ✅ Postgres, Fichier |
| **Disjoncteur (Circuit Breaker)** | ❌ | ❌ | ✅ Natif |
| **Réessais automatiques avec Backoff** | ❌ | ⚠️ Plugin requis | ✅ Natif |
| **Fusion de requêtes (Anti-Thundering Herd)**| ❌ | ❌ | ✅ Natif |
| **Repli Stale-if-error (Cache périmé)** | ❌ | ❌ | ✅ Natif |
| **Sécurité (Clés SHA-256, Auto-masquage)**| ❌ | ❌ | ✅ Natif |
| **OpenTelemetry & Prometheus** | ❌ | ⚠️ Callbacks requis | ✅ Natif |
| **Indépendant du Framework** | ✅ | ❌ Verrouillé | ✅ 100% Universel |

---

## 📦 Installation

ToolOps utilise un système d'installation modulaire. Le paquet principal n'a **aucune dépendance externe**. Vous n'installez que ce dont vous avez besoin.

### Référence Rapide

| Commande d'installation | Ce que vous obtenez | Quand l'utiliser |
| :--- | :--- | :--- |
| `pip install "toolops[all]"` | Ensemble complet de fonctionnalités | **Recommandé pour la production** |
| `pip install toolops` | SDK principal uniquement | Pour commencer, sans extras |

### 💻 Guides Spécifiques au Système d'Exploitation

Nous recommandons fortement d'isoler votre projet dans un environnement virtuel.

#### 🐧 Linux & 🍎 macOS
```bash
# 1. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate

# 2. Installer ToolOps (les guillemets sont requis pour bash/zsh)
pip install "toolops[all]"

# 3. Vérifier l'installation
toolops doctor
```

#### 🪟 Windows (PowerShell)
```powershell
# 1. Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\Activate.ps1

# 2. Installer ToolOps
pip install "toolops[all]"

# 3. Vérifier l'installation
toolops doctor
```

#### 🪟 Windows (Command Prompt)
```cmd
:: 1. Créer et activer un environnement virtuel
python -m venv .venv
.venv\Scripts\activate.bat

:: 2. Installer ToolOps (utilisez des guillemets doubles)
pip install "toolops[all]"

:: 3. Vérifier l'installation
toolops doctor
```

---

## 🚀 Démarrage Rapide

Cet exemple minimal vous permet de passer de l'installation à un outil fonctionnel, mis en cache et résilient en moins de 2 minutes.

```python
# Imports
import asyncio

from toolops.cache import MemoryCache
from toolops import readonly, sideeffect, cache_manager


# Étape 1 : Enregistrer un backend de cache (à faire une fois au démarrage)
cache_manager.register("memory", MemoryCache(), is_default=True)


# Étape 2 : Décorer toute fonction asynchrone avec @readonly pour les opérations de lecture
@readonly(cache_backend="memory", cache_ttl=3600, retry_count=3)
async def fetch_weather(city: str) -> dict:
    # Simule un appel d'API externe
    return {"city": city, "temp": 22, "condition": "sunny"}


# Étape 3 : Décorer les opérations d'écriture avec @sideeffect (pas de cache, mais protégé)
@sideeffect(circuit_breaker=True, timeout=5.0, retry_count=2)
async def send_alert(message: str) -> bool:
    # Simule l'envoi d'une notification
    print(f"Alerte envoyée : {message}")
    return True


async def main():
    # Le premier appel touche l'API (live)
    result = await fetch_weather("Paris")
    print(f"Premier appel (en direct) : {result}")

    # Le deuxième appel est servi depuis le cache — latence <5ms, 0 appel API
    result = await fetch_weather("Paris")
    print(f"Deuxième appel (en cache) : {result}")

    # Opération d'écriture avec protection par disjoncteur
    await send_alert("Agent terminé avec succès.")

asyncio.run(main())
```

---

## 🧠 Concepts Principaux

### 1. Backends de Cache

Enregistrez les backends une seule fois au démarrage de l'application, puis référencez-les par leur nom. ToolOps prend en charge plusieurs backends simultanément.

```python
from toolops import cache_manager
from toolops.cache import MemoryCache, PostgresCache, FileCache, SemanticCache


# En mémoire : le plus rapide, effacé au redémarrage, aucune dépendance
cache_manager.register("memory", MemoryCache(), is_default=True)


# Postgres : persistant après redémarrage, partageable entre processus
cache_manager.register("db", PostgresCache("postgresql://user:pass@localhost:5432/mydb"))


# Sémantique : embeddings vectoriels pour comparer par le sens, et non par égalité stricte
# Réduit les appels LLM jusqu'à 90%
from toolops.cache import SentenceTransformerEmbedder
embedder = SentenceTransformerEmbedder("all-MiniLM-L6-v2")
cache_manager.register("semantic", SemanticCache(embedder=embedder, threshold=0.92))
```

### 2. Patterns de Résilience

ToolOps fournit une résilience robuste et éprouvée en production dès la sortie de la boîte.

- **Disjoncteur (Circuit Breaker)** : Empêche de marteler un service défaillant et de provoquer des pannes en cascade.
- **Stale-if-Error** : Sert la dernière bonne valeur en cache connue si l'appel d'API en direct échoue.
- **Fusion de Requêtes (Request Coalescing)** : Si 50 agents appellent le même point de terminaison simultanément, ToolOps exécute l'appel d'API réel **une seule fois** et diffuse le résultat à tous.

```python
@readonly(
    cache_backend   = "db",
    cache_ttl       = 3600,
    retry_count     = 3,
    timeout         = 10.0,
    stale_if_error  = True,     # Repli (Fallback) en cas d'échec de l'API
    circuit_breaker = True      # Protège le service sous-jacent
)
async def get_market_data(ticker: str) -> dict:
    return await api.fetch(ticker)
```

### 3. Architecture & Sécurité (v0.2.0)

ToolOps v0.2.0 introduit une architecture de niveau entreprise :

- **Pipeline Middleware** : Le décorateur monolithique a été refactorisé en un pipeline composable (`Logging`, `Cache`, `CircuitBreaker`, `Retry`, `Coalescing`, `Fallback`).
- **Hachage des clés de cache en SHA-256** : Toutes les clés de cache sont strictement hachées. Aucune donnée sensible (tokens, PII) n'est exposée dans les stockages de cache.
- **Masquage Automatique des Paramètres** : Les arguments des outils contenant des mots-clés sensibles (`token`, `password`, `secret`, etc.) sont automatiquement masqués sous la forme `***MASKED***` dans les logs structurés.

---

## 📊 Observabilité

ToolOps instrumente chaque appel d'outil automatiquement.

### OpenTelemetry (OTEL) & Prometheus

**Nécessite :** `pip install "toolops[otel]"`

```python
from toolops.observability import configure_otel, configure_prometheus

# Pointer vers n'importe quel backend compatible OTEL (Jaeger, Datadog, Honeycomb, etc.)
configure_otel(service_name="my-agent", exporter_endpoint="http://localhost:4317")


# Exposer les métriques Prometheus
configure_prometheus(port=8000)
```

Les principales métriques exposées incluent `toolops_cache_hits_total`, `toolops_tool_latency_seconds`, et `toolops_circuit_opens_total`.

---

## 🔌 Intégration aux Frameworks

ToolOps décore de simples fonctions asynchrones Python, le rendant **100% compatible** avec vos frameworks d'agents préférés.

### LangChain / LangGraph
```python
from langchain.tools import tool

@tool
@readonly(cache_backend="memory", cache_ttl=600)
async def search_web(query: str) -> str:
    """Recherche sur le web et renvoie un résumé."""
    return await web_search_api.run(query)
```

### CrewAI
```python
from crewai.tools import BaseTool

class ResearchTool(BaseTool):
    name: str = "Research Tool"
    description: str = "Récupère et met en cache des données de recherche."

    @readonly(cache_backend="db", cache_ttl=3600)
    async def _run(self, query: str) -> str:
        return await research_api.fetch(query)
```

### Model Context Protocol (MCP)
```python
from toolops.integrations.mcp import MCPIntegration

# Génère automatiquement une définition d'outil MCP entièrement typée
mcp_definition = MCPIntegration.to_mcp_definition(get_weather)
mcp_server.register_tool(mcp_definition)
```

---

## 🛠️ Référence CLI

ToolOps est livré avec un outil en ligne de commande pour gérer votre infrastructure de cache.

```bash
# Vérifier la santé de tous les backends enregistrés
toolops doctor

# Voir les statistiques de cache en direct pour une application
toolops stats --app my_app:setup_toolops

# Vider le cache d'un backend spécifique
toolops clear memory --app my_app:setup_toolops
```

---

## 🤝 Contribution

ToolOps est construit pour la communauté, par la communauté. 

- Consultez notre [Guide de Contribution](CONTRIBUTING.md) pour commencer.
- Prenez connaissance de notre [Code de Conduite](CODE_OF_CONDUCT.md).
- Signalez les problèmes de sécurité en toute sécurité via notre [Politique de Sécurité](SECURITY.md).

---

## 💬 Communauté & Contact

Nous construisons activement l'avenir de l'infrastructure des agents IA. Rejoignez la discussion !

- **Créateur :** Hedi Manai ([LinkedIn](https://www.linkedin.com/in/hedimanai) | [GitHub](https://github.com/hedimanai-pro))
- **Signaler des Bugs & Demander des Fonctionnalités :** [GitHub Issues](https://github.com/hedimanai-pro/toolops/issues)
- **E-mail :** hedi.manai.pro@gmail.com

---

<div align="center">
<b>ToolOps — Conçu pour la Production.</b><br>
Sous licence <a href="LICENSE">Apache 2.0</a>
</div>
