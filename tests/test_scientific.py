"""Tests for scientific functions, trigonometry, logarithms, powers, roots, and factorials.
"""

import math
import pytest
from core.engine import CalculationEngine, AngleMode


@pytest.fixture
def deg_engine():
    return CalculationEngine(AngleMode.DEG)


@pytest.fixture
def rad_engine():
    return CalculationEngine(AngleMode.RAD)


def test_trig_degrees(deg_engine):
    assert deg_engine.evaluate("sin(0)").formatted_result == "0"
    assert deg_engine.evaluate("sin(30)").formatted_result == "0.5"
    assert deg_engine.evaluate("sin(90)").formatted_result == "1"
    assert deg_engine.evaluate("sin(180)").formatted_result == "0"
    assert deg_engine.evaluate("sin(270)").formatted_result == "-1"

    assert deg_engine.evaluate("cos(0)").formatted_result == "1"
    assert deg_engine.evaluate("cos(60)").formatted_result == "0.5"
    assert deg_engine.evaluate("cos(90)").formatted_result == "0"
    assert deg_engine.evaluate("cos(180)").formatted_result == "-1"

    assert deg_engine.evaluate("tan(0)").formatted_result == "0"
    assert deg_engine.evaluate("tan(45)").formatted_result == "1"


def test_trig_radians(rad_engine):
    assert rad_engine.evaluate("cos(0)").formatted_result == "1"
    assert rad_engine.evaluate("sin(pi / 2)").formatted_result == "1"
    assert rad_engine.evaluate("tan(0)").formatted_result == "0"


def test_inverse_trig(deg_engine, rad_engine):
    assert deg_engine.evaluate("asin(0.5)").formatted_result == "30"
    assert deg_engine.evaluate("acos(0.5)").formatted_result == "60"
    assert deg_engine.evaluate("atan(1)").formatted_result == "45"

    assert rad_engine.evaluate("asin(0)").formatted_result == "0"
    assert rad_engine.evaluate("atan(0)").formatted_result == "0"


def test_logarithms(deg_engine):
    assert deg_engine.evaluate("log(10)").formatted_result == "1"
    assert deg_engine.evaluate("log(100)").formatted_result == "2"
    assert deg_engine.evaluate("log(1000)").formatted_result == "3"
    assert deg_engine.evaluate("ln(e)").formatted_result == "1"


def test_powers_and_roots(deg_engine):
    assert deg_engine.evaluate("2^3").formatted_result == "8"
    assert deg_engine.evaluate("3^2").formatted_result == "9"
    assert deg_engine.evaluate("4^0.5").formatted_result == "2"
    assert deg_engine.evaluate("sqrt(144)").formatted_result == "12"
    assert deg_engine.evaluate("√(144)").formatted_result == "12"
    assert deg_engine.evaluate("√25").formatted_result == "5"


def test_factorials(deg_engine):
    assert deg_engine.evaluate("0!").formatted_result == "1"
    assert deg_engine.evaluate("1!").formatted_result == "1"
    assert deg_engine.evaluate("5!").formatted_result == "120"
    assert deg_engine.evaluate("6!").formatted_result == "720"
    assert deg_engine.evaluate("(2 + 3)!").formatted_result == "120"
    assert deg_engine.evaluate("fact(5)").formatted_result == "120"


def test_absolute_value(deg_engine):
    assert deg_engine.evaluate("|-10|").formatted_result == "10"
    assert deg_engine.evaluate("|3 - 8|").formatted_result == "5"
    assert deg_engine.evaluate("abs(-7.5)").formatted_result == "7.5"


def test_constants_and_implicit(deg_engine):
    pi_val = deg_engine.evaluate("pi").raw_result
    assert math.isclose(pi_val, math.pi, rel_tol=1e-12)

    e_val = deg_engine.evaluate("e").raw_result
    assert math.isclose(e_val, math.e, rel_tol=1e-12)

    res_2pi = deg_engine.evaluate("2pi").raw_result
    assert math.isclose(res_2pi, 2 * math.pi, rel_tol=1e-12)
