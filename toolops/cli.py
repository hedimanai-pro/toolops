"""
Name: cli.py

Description: Command line interface for ToolOps SDK.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import argparse
import asyncio
import importlib
import inspect
import json
import os
import platform
import sys
from importlib.metadata import PackageNotFoundError, version
from typing import Any

from toolops import cache_manager
from toolops.decorators import build_cache_key
from toolops.observability import prometheus_metrics


def _toolops_version() -> str:
    """
    Get current ToolOps version.

    Returns:
        Version string.
    """

    try:
        return version("toolops")
    except PackageNotFoundError:
        return "0.0.0-dev"


async def _load_app(spec: str | None) -> None:
    """
    Dynamically load the ToolOps application.

    Args:
        spec: Module path specification.
    """

    if not spec:
        return

    module_name, _, attr_name = spec.partition(":")
    module = importlib.import_module(module_name)
    target_name = attr_name or "setup_toolops"
    target = getattr(module, target_name)
    result = target()

    if inspect.isawaitable(result):
        await result


def _dependency_status() -> dict[str, bool]:
    """
    Check status of optional dependencies.

    Returns:
        Dependency status dictionary.
    """

    modules = {
        "postgres": "asyncpg",
        "semantic": "sentence_transformers",
        "openai": "openai",
    }
    status: dict[str, bool] = {}

    for name, module_name in modules.items():
        try:
            importlib.import_module(module_name)
            status[name] = True

        except Exception:
            status[name] = False

    return status


async def _doctor(app: str | None) -> dict[str, Any]:
    """
    Run diagnostic check on environment.

    Args:
        app: Optional app spec.

    Returns:
        Diagnostic report dictionary.
    """

    payload: dict[str, Any] = {
        "toolops_version": _toolops_version(),
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "dependencies": _dependency_status(),
    }

    if app:
        await _load_app(app)

    payload["registered_backends"] = cache_manager.registered
    connect_errors: dict[str, str] = {}

    for name in cache_manager.registered:
        backend = cache_manager.backend(name)
        connect = getattr(backend, "connect", None)
        if callable(connect):
            try:
                result = connect()
                if inspect.isawaitable(result):
                    await result

            except Exception as exc:
                connect_errors[name] = str(exc)

    if connect_errors:
        payload["connect_errors"] = connect_errors

    return payload


async def _stats(app: str | None) -> dict[str, Any]:
    """
    Get cache backend statistics.

    Args:
        app: Optional app spec.

    Returns:
        Statistics dictionary.
    """

    await _load_app(app)
    return await cache_manager.stats()


def _resolve_inspect_key(args: argparse.Namespace) -> str:
    """
    Resolve cache key from CLI args.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Resolved cache key string.
    """

    if args.key:
        return str(args.key)

    params = json.loads(args.params_json)
    key_params = args.key_params.split(",") if args.key_params else None
    return build_cache_key(args.tool, params, key_params)


async def _inspect_key(args: argparse.Namespace) -> dict[str, Any] | None:
    """
    Inspect specific cache entry.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Entry metadata or None.
    """

    await _load_app(args.app)
    key = _resolve_inspect_key(args)
    return await cache_manager.inspect(args.backend, key)


async def _clear(args: argparse.Namespace) -> dict[str, Any]:
    """
    Clear cache backend(s).

    Args:
        args: Parsed CLI arguments.

    Returns:
        Status dictionary.
    """

    await _load_app(args.app)

    if args.backend == "all":
        cleared = []
        for backend in cache_manager.registered:
            await cache_manager.clear(backend)
            cleared.append(backend)

        return {"cleared": cleared}

    await cache_manager.clear(args.backend)
    return {"cleared": [args.backend]}


async def _invalidate_tags(args: argparse.Namespace) -> dict[str, Any]:
    """
    Invalidate entries by tags via CLI.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Status dictionary.
    """

    await _load_app(args.app)
    deleted = await cache_manager.invalidate(args.backend, tags=args.tags)
    return {"backend": args.backend, "deleted": deleted, "tags": args.tags}


def build_parser() -> argparse.ArgumentParser:
    """
    Construct the CLI argument parser.

    Returns:
        Populated ArgumentParser instance.
    """

    parser = argparse.ArgumentParser(prog="toolops")
    parser.add_argument(
        "--app",
        default=os.getenv("TOOLOPS_APP"),
        help="Module path like package.module:setup_toolops",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("doctor", help="Inspect runtime and backend readiness")
    subparsers.add_parser("stats", help="Show cache stats")
    subparsers.add_parser(
        "metrics", help="Print Prometheus-formatted in-process metrics"
    )

    clear_parser = subparsers.add_parser("clear", help="Clear one backend or all")
    clear_parser.add_argument("backend")

    inspect_parser = subparsers.add_parser(
        "inspect-key", help="Inspect a cache entry by raw key or by tool+params"
    )
    inspect_parser.add_argument("backend")
    inspect_parser.add_argument("key", nargs="?")
    inspect_parser.add_argument("--tool")
    inspect_parser.add_argument("--params-json")
    inspect_parser.add_argument("--key-params")

    invalidate_parser = subparsers.add_parser(
        "invalidate-tags", help="Invalidate entries by tags"
    )
    invalidate_parser.add_argument("backend")
    invalidate_parser.add_argument("tags", nargs="+")

    return parser


async def _dispatch(args: argparse.Namespace) -> Any:
    """
    Dispatch command to appropriate handler.

    Args:
        args: Parsed CLI arguments.

    Returns:
        Command execution result.
    """

    if args.command == "doctor":
        return await _doctor(args.app)

    if args.command == "stats":
        return await _stats(args.app)

    if args.command == "clear":
        return await _clear(args)

    if args.command == "inspect-key":
        if not args.key and not (args.tool and args.params_json):
            raise SystemExit(
                "inspect-key requires either a raw key or --tool with --params-json."
            )

        return await _inspect_key(args)

    if args.command == "invalidate-tags":
        return await _invalidate_tags(args)

    if args.command == "metrics":
        return prometheus_metrics()

    raise SystemExit(f"Unknown command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for CLI.

    Args:
        argv: Optional argument list.

    Returns:
        Exit code.
    """

    parser = build_parser()
    args = parser.parse_args(argv)
    result = asyncio.run(_dispatch(args))

    if isinstance(result, str):
        print(result)

    else:
        print(json.dumps(result, indent=2, sort_keys=True, default=str))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
