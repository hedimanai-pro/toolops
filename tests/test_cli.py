"""
Name: test_cli.py

Description: Integration tests for the ToolOps CLI.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import json
from uuid import uuid4
from pathlib import Path

from toolops.cli import main


def _workspace_tmp(name: str) -> Path:
    """
    Create a temporary workspace directory for CLI tests.

    Args:
        name: Workspace name prefix.

    Returns:
        Path to the created directory.
    """

    path = Path.cwd() / ".tmp_test_cli" / f"{name}_{uuid4().hex}"
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_cli_doctor_and_inspect_key(monkeypatch, capsys):
    """Test 'doctor' and 'inspect-key' CLI commands."""

    tmp_dir = _workspace_tmp("doctor")
    app_file = tmp_dir / "demo_toolops_app.py"
    app_file.write_text(
        "\n".join(
            [
                "from toolops import build_cache_key, cache_manager",
                "from toolops.cache import MemoryCache",
                "",
                "async def setup_toolops():",
                "    cache_manager.register('cli', MemoryCache(), is_default=True)",
                "    key = build_cache_key('load_profile', {'user_id': 'alice'}, None)",
                "    await cache_manager.set('cli', key, {'user_id': 'alice'}, 60, tags=['seed'])",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_dir))

    main(["--app", "demo_toolops_app:setup_toolops", "doctor"])
    doctor_output = json.loads(capsys.readouterr().out)
    assert "cli" in doctor_output["registered_backends"]

    main(
        [
            "--app",
            "demo_toolops_app:setup_toolops",
            "inspect-key",
            "cli",
            "--tool",
            "load_profile",
            "--params-json",
            '{"user_id":"alice"}',
        ]
    )
    inspect_output = json.loads(capsys.readouterr().out)
    assert inspect_output["value"] == {"user_id": "alice"}


def test_cli_clear_backend(monkeypatch, capsys):
    """Test 'clear' CLI command."""

    tmp_dir = _workspace_tmp("clear")
    app_file = tmp_dir / "clear_toolops_app.py"
    app_file.write_text(
        "\n".join(
            [
                "from toolops import cache_manager",
                "from toolops.cache import MemoryCache",
                "",
                "async def setup_toolops():",
                "    cache_manager.register('clearme', MemoryCache(), is_default=True)",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_dir))

    main(["--app", "clear_toolops_app:setup_toolops", "clear", "clearme"])
    output = json.loads(capsys.readouterr().out)
    assert output == {"cleared": ["clearme"]}


def test_cli_metrics_and_invalidate(monkeypatch, capsys):
    """Test 'metrics' and 'invalidate-tags' CLI commands."""

    tmp_dir = _workspace_tmp("extra")
    app_file = tmp_dir / "extra_toolops_app.py"
    app_file.write_text(
        "\n".join(
            [
                "from toolops import cache_manager",
                "from toolops.cache import MemoryCache",
                "",
                "async def setup():",
                "    cache_manager.register('m1', MemoryCache(), is_default=True)",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.syspath_prepend(str(tmp_dir))

    # Call a tool to generate metrics
    from toolops import readonly
    @readonly(cache_backend='m1')
    async def some_tool(): return 1
    import asyncio
    asyncio.run(some_tool())

    main(["--app", "extra_toolops_app:setup", "metrics"])
    metrics_output = capsys.readouterr().out
    assert "toolops_tool_calls_total" in metrics_output

    main(["--app", "extra_toolops_app:setup", "invalidate-tags", "m1", "t1"])
    inv_output = json.loads(capsys.readouterr().out)
    assert inv_output["deleted"] == 0
    assert inv_output["tags"] == ["t1"]
