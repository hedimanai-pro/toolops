"""
Name: conftest.py

Description: Pytest configuration and global fixtures for ToolOps tests.

Last_updated: 2026-05-03

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

from __future__ import annotations

import pytest

from toolops import cache_manager
from toolops.observability import metrics
import toolops.decorators as decorators_module


@pytest.fixture(autouse=True)
def reset_toolops_globals():
    """
    Reset all ToolOps global states before and after each test.

    Returns:
        None (yields control to test).
    """

    original_backends = dict(cache_manager._backends)
    original_default = cache_manager._default

    decorators_module._circuit_breakers.clear()
    cache_manager._backends = {}
    cache_manager._default = None
    metrics.reset()

    yield

    decorators_module._circuit_breakers.clear()
    cache_manager._backends = original_backends
    cache_manager._default = original_default
    metrics.reset()
