"""Tests for error handling, validation, boundary conditions, and security enforcement.
"""

import pytest
from core.engine import CalculationEngine, AngleMode


@pytest.fixture
def engine():
    return CalculationEngine(AngleMode.DEG)


def test_division_by_zero(engine):
    res = engine.evaluate("10 / 0")
    assert res.success is False
    assert "divide by zero" in res.error_message.lower()


def test_modulo_by_zero(engine):
    res = engine.evaluate("15 % 0")
    assert res.success is False
    assert "modulo by zero" in res.error_message.lower()


def test_square_root_negative(engine):
    res = engine.evaluate("sqrt(-9)")
    assert res.success is False
    assert "negative" in res.error_message.lower()


def test_logarithm_non_positive(engine):
    res_zero = engine.evaluate("log(0)")
    assert res_zero.success is False
    assert "positive" in res_zero.error_message.lower()

    res_neg = engine.evaluate("ln(-5)")
    assert res_neg.success is False
    assert "positive" in res_neg.error_message.lower()


def test_tan_undefined_degree(engine):
    res = engine.evaluate("tan(90)")
    assert res.success is False
    assert "undefined" in res.error_message.lower()


def test_factorial_negative(engine):
    res = engine.evaluate("(-5)!")
    assert res.success is False
    assert "non-negative" in res.error_message.lower()


def test_factorial_fraction(engine):
    res = engine.evaluate("(3.5)!")
    assert res.success is False
    assert "integer" in res.error_message.lower()


def test_malformed_syntax(engine):
    cases = ["2 +", "((5 + 3)", "* 5", "5..5", ""]
    for case in cases:
        res = engine.evaluate(case)
        assert res.success is False
        assert res.error_message is not None


def test_security_imports_rejected(engine):
    malicious = [
        "__import__('os').system('dir')",
        "import os",
        "open('file.txt')",
        "eval('2+2')",
        "exec('a=1')",
        "[x for x in [1, 2]]",
        "lambda x: x + 1",
        "__builtins__",
    ]
    for expr in malicious:
        res = engine.evaluate(expr)
        assert res.success is False
        assert res.error_message is not None


def test_computational_limits(engine):
    # Enormous exponentiation
    res_pow = engine.evaluate("10 ^ 50000")
    assert res_pow.success is False
    assert "limit" in res_pow.error_message.lower() or "bound" in res_pow.error_message.lower()

    # Giant factorial
    res_fact = engine.evaluate("200!")
    assert res_fact.success is False
    assert "supported limit" in res_fact.error_message.lower()
