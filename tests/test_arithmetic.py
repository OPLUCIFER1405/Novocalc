"""Tests for basic arithmetic, precedence, decimals, and implicit multiplication.
"""

import pytest
from core.engine import CalculationEngine, AngleMode


@pytest.fixture
def engine():
    return CalculationEngine(AngleMode.DEG)


def test_basic_addition(engine):
    res = engine.evaluate("25 + 15")
    assert res.success is True
    assert res.formatted_result == "40"
    assert res.raw_result == 40


def test_basic_subtraction(engine):
    res = engine.evaluate("50 - 18")
    assert res.success is True
    assert res.formatted_result == "32"


def test_basic_multiplication(engine):
    res = engine.evaluate("12 * 8")
    assert res.success is True
    assert res.formatted_result == "96"


def test_basic_division(engine):
    res = engine.evaluate("10 / 4")
    assert res.success is True
    assert res.formatted_result == "2.5"
    assert res.raw_result == 2.5


def test_modulo_operation(engine):
    res = engine.evaluate("10 % 3")
    assert res.success is True
    assert res.formatted_result == "1"


def test_decimal_arithmetic(engine):
    res = engine.evaluate("2.5 + 1.5")
    assert res.success is True
    assert res.formatted_result == "4"

    res2 = engine.evaluate("0.1 + 0.2")
    assert res2.success is True
    assert res2.formatted_result == "0.3"


def test_operator_precedence(engine):
    res = engine.evaluate("2 + 3 * 4")
    assert res.success is True
    assert res.formatted_result == "14"


def test_nested_parentheses(engine):
    res = engine.evaluate("((2 + 3) * (4 - 1)) / 5")
    assert res.success is True
    assert res.formatted_result == "3"


def test_unicode_symbols(engine):
    res = engine.evaluate("12 × 8 − 6 ÷ 2")
    assert res.success is True
    assert res.formatted_result == "93"


def test_implicit_multiplication(engine):
    assert engine.evaluate("2(3 + 4)").formatted_result == "14"
    assert engine.evaluate("(2 + 3)(4 + 1)").formatted_result == "25"
    assert engine.evaluate("3(2)").formatted_result == "6"
    assert engine.evaluate("(5)4").formatted_result == "20"


def test_unary_signs(engine):
    assert engine.evaluate("-5 + 3").formatted_result == "-2"
    assert engine.evaluate("+10 - (-5)").formatted_result == "15"
    assert engine.evaluate("-(-8)").formatted_result == "8"
