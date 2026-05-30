# Contributing to ToolOps

First off, thank you for helping us build the resilience layer for AI agents! Your contributions make ToolOps better for everyone.

ToolOps is built on the principle of **Clarity — No fluff**. We value robust, well-typed, and highly-tested code that solves real-world agent engineering problems.

---

## Table of Contents

1. [Development Setup](#development-setup)
2. [Project Structure](#project-structure)
3. [Development Workflow](#development-workflow)
4. [Code Style & Standards](#code-style--standards)
5. [Testing Requirements](#testing-requirements)
6. [Pull Request Process](#pull-request-process)
7. [Commit Message Convention](#commit-message-convention)
8. [Reporting Issues](#reporting-issues)
9. [Release Process](#release-process)
10. [License](#license)

---

## Development Setup

### Prerequisites

- **Python 3.9+** (we test against 3.9, 3.10, 3.11, 3.12)
- **Git**
- **Docker** (optional, for PostgreSQL integration tests)

### 1. Clone the repository

```bash
git clone https://github.com/hedimanai-pro/toolops.git
cd toolops
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install in development mode

```bash
pip install -r requirements.txt
```

This installs ToolOps in editable mode with development tools (pytest, pytest-cov, black, ruff, mypy) alongside its default-installed caching, database, and telemetry drivers.

### 4. Verify your setup

```bash
make test        # Run the full test suite
make lint        # Run linting checks
make typecheck   # Run type checking
```

All three commands should pass before you start making changes.

### 5. (Optional) Start PostgreSQL with Docker

For integration tests with PostgresCache:

```bash
make docker-up   # Starts PostgreSQL in a Docker container
make docker-down # Stops the container
```

Default connection string: `postgresql://toolops:toolops@localhost:5432/toolops_test`

---

## Project Structure

```
toolops/
├── toolops/                    # Core package
│   ├── __init__.py            # Public API exports
│   ├── decorators.py          # @tool, @readonly, @sideeffect, @stateful
│   ├── cache/                 # Cache backend package (base, memory, file, postgres, sqlite, valkey, mysql, semantic)
│   ├── resilience.py          # Circuit breaker implementation
│   ├── coalescer.py           # Request coalescing
│   ├── logger.py              # Structured JSON logging
│   ├── observability.py       # Prometheus metrics + OTEL tracing
│   ├── cli.py                 # Command-line interface
│   └── integrations/          # Framework integrations
│       ├── __init__.py
│       ├── langchain.py
│       ├── crewai.py
│       ├── llamaindex.py
│       ├── langgraph.py
│       └── mcp.py
tests/                          # Test suite
│   ├── conftest.py            # Pytest fixtures (global state reset)
│   ├── test_backends.py       # Cache backend tests
│   ├── test_cli.py            # CLI integration tests
│   ├── test_core_features.py  # Stale-if-error, circuit breaker, tags
│   ├── test_sync_wrapper.py   # Synchronous function wrapping
│   ├── test_observability.py  # Prometheus metrics tests
│   ├── test_mcp.py            # MCP integration tests
│   └── test_langgraph_integration.py  # LangGraph integration tests
├── .github/workflows/          # CI/CD pipelines
├── benchmarks/                 # Performance benchmarks
├── examples/                   # Usage examples
├── pyproject.toml             # Package configuration (PEP 621)
├── Makefile                   # Development commands
├── CHANGELOG.md               # Release history
├── CONTRIBUTING.md            # This file
├── CODE_OF_CONDUCT.md         # Community standards
└── SECURITY.md                # Security policy
```

---

## Development Workflow

We use the `Makefile` to standardize all development tasks:

| Command | Description |
| :--- | :--- |
| `make test` | Run the full test suite with coverage reporting (80% minimum) |
| `make lint` | Run Ruff and Black checks |
| `make format` | Auto-format code with Black |
| `make typecheck` | Run mypy in strict mode |
| `make coverage` | Generate HTML coverage report |
| `make clean` | Remove build artifacts and cache files |

### Before every commit

```bash
make format      # Ensure consistent formatting
make lint        # Catch style issues
make typecheck   # Catch type errors
make test        # Ensure nothing is broken
```

---

## Code Style & Standards

### Formatting

- **Black** is our formatter. Configuration lives in `pyproject.toml`.
- Line length: **88 characters** (Black default).
- String quotes: Black handles this automatically.

### Linting

- **Ruff** handles all linting. Configuration lives in `pyproject.toml`.
- Rules enabled: E, W, F, I (isort), N (pep8-naming), UP (pyupgrade), B (flake8-bugbear), C4 (flake8-comprehensions), SIM (flake8-simplify).

### Type Checking

- **mypy** in strict mode is required.
- All public functions must have type annotations.
- No `Any` unless absolutely necessary — and it must be justified in a comment.

### Docstrings

Every public class and function must have a complete docstring with:

```python
def example(param: str) -> int:
    """
    Short description of what this does.

    Longer description if needed, spanning multiple lines.
    Can include code examples for complex functions.

    Args:
        param: Description of the parameter.

    Returns:
        Description of the return value.

    Raises:
        ValueError: When and why this is raised.
    """
```

### Architecture Principles

1. **Keep the core lightweight.** The `decorators.py` module is the heart of the SDK — keep it focused.
2. **Integrations go in `toolops/integrations/`.** Framework-specific code is isolated.
3. **All backends implement `CacheBackend`.** The ABC interface is the contract.
4. **Prefer composition over inheritance.** Middlewares are composed, not inherited.
5. **Zero dependencies for core usage.** Everything optional must be import-guarded.

---

## Testing Requirements

### Test Coverage

- **Minimum coverage: 80%**. The CI enforces this.
- Every new feature must include tests.
- Every bug fix must include a regression test.

### Test Organization

| File | What to test |
| :--- | :--- |
| `test_backends.py` | Cache backend operations (get, set, delete, invalidate, stats) |
| `test_cli.py` | CLI commands (doctor, stats, clear, inspect-key) |
| `test_core_features.py` | Stale-if-error, circuit breaker, fallback, tags |
| `test_sync_wrapper.py` | Synchronous function wrapping |
| `test_observability.py` | Prometheus metrics rendering |
| `test_mcp.py` | MCP definition conversion |
| `test_langgraph_integration.py` | LangGraph node binding |

### Test Conventions

- Use `@pytest.mark.asyncio` for async tests.
- Use `AsyncMock` and `MagicMock` from `unittest.mock` for mocking.
- Use descriptive test names: `test_<what>_<condition>_<expected_result>`.
- Reset global state via the `reset_toolops_globals` fixture (auto-used in `conftest.py`).

### Running specific tests

```bash
pytest tests/test_backends.py -v                    # Backend tests only
pytest tests/test_core_features.py::test_stale_if_error_returns_last_good_value -v  # Single test
pytest tests/ -k "not postgres" -v                  # Skip Postgres tests
```

---

## Pull Request Process

### 1. Branch naming

```bash
git checkout -b feature/semantic-cache-v2
git checkout -b fix/postgres-invalidate-tags
git checkout -b docs/api-reference
git checkout -b refactor/middleware-pipeline
```

Prefixes: `feature/`, `fix/`, `docs/`, `refactor/`, `perf/`, `test/`.

### 2. Before submitting

```bash
make format
make lint
make typecheck
make test
```

All four must pass.

### 3. PR description template

Your PR description should include:

- **What** — What changed and why
- **How** — How the change works (for complex changes)
- **Testing** — How you tested it
- **Breaking changes** — List any (or confirm none)

### 4. Review process

- A maintainer will review within 48 hours.
- Address review feedback promptly.
- Squash commits if requested.

### 5. Merge criteria

- CI passes (lint, typecheck, test matrix)
- At least one maintainer approval
- No outstanding review comments

---

## Commit Message Convention

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

**Types:**

| Type | Use when |
| :--- | :--- |
| `feat` | Adding a new feature |
| `fix` | Fixing a bug |
| `docs` | Documentation changes only |
| `style` | Code style changes (formatting, no logic change) |
| `refactor` | Code refactoring (no feature change) |
| `perf` | Performance improvements |
| `test` | Adding or fixing tests |
| `chore` | Build, CI, tooling changes |

**Examples:**

```
feat(cache): add Redis backend support
fix(semantic): resolve O(n) eviction with deque
docs(readme): update installation instructions
refactor(decorators): extract middleware pipeline
perf(postgres): use GIN index for tag invalidation
```

---

## Reporting Issues

### Bug reports

Use the [Bug Report template](https://github.com/hedimanai-pro/toolops/issues/new?template=bug_report.md) and include:

1. ToolOps version (`toolops --version`)
2. Python version
3. Steps to reproduce
4. Expected behavior
5. Actual behavior
6. Error traceback (if any)

### Feature requests

Use the [Feature Request template](https://github.com/hedimanai-pro/toolops/issues/new?template=feature_request.md) and include:

1. Use case — what problem are you solving?
2. Proposed solution
3. Alternatives considered

---

## Release Process

Releases are automated via GitHub Actions:

1. Update `CHANGELOG.md` with the new version.
2. Bump version in `pyproject.toml`.
3. Commit: `git commit -m "chore(release): bump version to v0.X.Y"`
4. Tag: `git tag -a v0.X.Y -m "Release v0.X.Y"`
5. Push: `git push origin main --tags`

The [release.yml](.github/workflows/release.yml) workflow will:
- Run the full test suite
- Build the distribution
- Publish to PyPI automatically

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.
