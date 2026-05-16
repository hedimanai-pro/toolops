"""
Name: test_resilience.py

Description: Tests for circuit breaker and retry patterns.

Last_updated: 2026-05-16

Updated_by: Hedi Manai
Github: https://github.com/hedimanai-pro
LinkedIn: https://www.linkedin.com/in/hedimanai

Note: This project is open source for knowledge sharing
"""

import asyncio

import pytest

from toolops.resilience import CircuitBreaker, CircuitOpenError


@pytest.mark.asyncio
async def test_circuit_breaker_manual_states():
    """Test the CircuitBreaker class directly for state transitions."""
    cb = CircuitBreaker(tool="test", failure_threshold=2, recovery_timeout=0.1)

    assert cb.state == "closed"

    # 1st failure
    cb.before_call()
    cb.record_failure()
    cb.finish_attempt()
    assert cb.state == "closed"

    # 2nd failure -> Open
    cb.before_call()
    cb.record_failure()
    cb.finish_attempt()
    assert cb.state == "open"

    # Rejected while open
    with pytest.raises(CircuitOpenError):
        cb.before_call()

    # Wait for recovery
    await asyncio.sleep(0.15)

    # Half-open
    cb.before_call()
    assert cb.state == "half_open"

    # Success in half-open -> Closed
    cb.record_success()
    cb.finish_attempt()
    assert cb.state == "closed"


@pytest.mark.asyncio
async def test_circuit_breaker_failures_increment():
    """Test that failures are counted correctly."""
    cb = CircuitBreaker(tool="test", failure_threshold=3)

    cb.record_failure()
    cb.record_failure()
    assert cb.state == "closed"

    cb.record_failure()
    assert cb.state == "open"
