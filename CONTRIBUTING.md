# Contributing to ToolOps

First off, thank you for helping us build the resilience layer for AI agents! 🎉

ToolOps is built on the principle of **Clarity · No fluff**. We value robust, well-typed, and highly-tested code that solves real-world agent engineering problems.

---

## Development Setup

1. **Clone the repository**:
   ```bash
   git clone https://github.com/hedimanai-pro/toolops.git
   cd toolops
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -e ".[dev,all]"
   ```

---

## The Workflow

We use a `Makefile` to standardize development tasks:

- `make test` — Run the full test suite with coverage reporting.
- `make lint` — Run Ruff and Black checks.
- `make format` — Automatically format code with Black.
- `make typecheck` — Run mypy in strict mode.

---

## Pull Request Guidelines

1. **Branching**: Create a feature branch (e.g., `feature/semantic-cache-v2`).
2. **Testing**: Every new feature or bug fix **must** include tests.
3. **Coverage**: Ensure `make test` passes and coverage remains above **80%**.
4. **Documentation**: Update `README.md`, `docs/index.md`, and add a docstring to every new public function/class.
5. **Changelog**: Add your changes to `CHANGELOG.md` under the `[Unreleased]` section.

---

## Code Style & Standards

- **Formatting**: We strictly follow Black formatting.
- **Linting**: We use Ruff for fast, reliable linting.
- **Typing**: All code must pass `mypy --strict`. No `Any` unless absolutely necessary (and justified).
- **Architecture**: Keep the core (decorators) lightweight. Put specific service integrations in `toolops/integrations/`.

---

## Reporting Issues

If you find a bug or have a feature request, please use the GitHub issue tracker at [github.com/hedimanai-pro/toolops/issues](https://github.com/hedimanai-pro/toolops/issues). Be as descriptive as possible and include steps to reproduce for bugs.

---

## License

By contributing, you agree that your contributions will be licensed under the **Apache License 2.0**.