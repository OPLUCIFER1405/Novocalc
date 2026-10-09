"""Mathematical Calculation Engine for NovaCalc.

Evaluates AST-parsed mathematical expressions safely with angle mode support,
numerical domain validation, overflow prevention, and clean result formatting.
"""

from __future__ import annotations
import ast
import enum
import math
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Union

from .expression_parser import (
    CalculationOverflowError,
    CalculationZeroDivisionError,
    CalculatorError,
    CalculatorSyntaxError,
    ExpressionParser,
    MathDomainError,
    SecurityError,
)


class AngleMode(enum.Enum):
    """Trigonometric angle interpretation mode."""
    DEG = "DEG"
    RAD = "RAD"


@dataclass
class CalculationResult:
    """Represents the outcome of an expression evaluation."""
    expression: str
    sanitized_expression: str
    raw_result: Optional[Union[int, float]]
    formatted_result: str
    angle_mode: AngleMode
    success: bool
    error_message: Optional[str] = None


class CalculationEngine:
    """Safe, high-precision mathematical engine for scientific calculations."""

    MAX_EXPONENT = 10000
    MAX_FACTORIAL_INPUT = 170
    FLOAT_ROUND_DIGITS = 12
    EPSILON = 1e-14

    def __init__(self, angle_mode: AngleMode = AngleMode.DEG):
        self._angle_mode = angle_mode

    @property
    def angle_mode(self) -> AngleMode:
        return self._angle_mode

    @angle_mode.setter
    def angle_mode(self, mode: AngleMode) -> None:
        if not isinstance(mode, AngleMode):
            raise ValueError(f"Invalid angle mode: {mode}")
        self._angle_mode = mode

    def set_angle_mode(self, mode: AngleMode) -> None:
        """Set the current trigonometric angle mode."""
        self.angle_mode = mode

    # -------------------------------------------------------------------------
    # Scientific Mathematical Functions
    # -------------------------------------------------------------------------

    def _sin(self, x: float) -> float:
        if not math.isfinite(x):
            raise MathDomainError("Invalid argument for sin")

        if self._angle_mode == AngleMode.DEG:
            rem = x % 360
            if rem in (0, 180):
                return 0.0
            elif rem == 90:
                return 1.0
            elif rem == 270:
                return -1.0
            elif rem in (30, 150):
                return 0.5
            elif rem in (210, 330):
                return -0.5
            rad = math.radians(x)
            val = math.sin(rad)
            return 0.0 if abs(val) < self.EPSILON else val
        else:
            val = math.sin(x)
            return 0.0 if abs(val) < self.EPSILON else val

    def _cos(self, x: float) -> float:
        if not math.isfinite(x):
            raise MathDomainError("Invalid argument for cos")

        if self._angle_mode == AngleMode.DEG:
            rem = x % 360
            if rem in (90, 270):
                return 0.0
            elif rem == 0:
                return 1.0
            elif rem == 180:
                return -1.0
            elif rem in (60, 300):
                return 0.5
            elif rem in (120, 240):
                return -0.5
            rad = math.radians(x)
            val = math.cos(rad)
            return 0.0 if abs(val) < self.EPSILON else val
        else:
            val = math.cos(x)
            return 0.0 if abs(val) < self.EPSILON else val

    def _tan(self, x: float) -> float:
        if not math.isfinite(x):
            raise MathDomainError("Invalid argument for tan")

        if self._angle_mode == AngleMode.DEG:
            rem = x % 180
            if abs(rem - 90) < 1e-9:
                raise MathDomainError("Tangent is undefined at 90° + k·180°")
            if rem == 0:
                return 0.0
            elif rem == 45:
                return 1.0
            elif rem == 135:
                return -1.0
            rad = math.radians(x)
            val = math.tan(rad)
            return 0.0 if abs(val) < self.EPSILON else val
        else:
            half_pi = math.pi / 2
            rem = (x - half_pi) % math.pi
            if abs(rem) < 1e-12 or abs(rem - math.pi) < 1e-12:
                raise MathDomainError("Tangent is undefined at π/2 + k·π")
            val = math.tan(x)
            return 0.0 if abs(val) < self.EPSILON else val

    def _asin(self, x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise MathDomainError("asin argument must be in domain [-1, 1]")
        val = math.asin(x)
        return math.degrees(val) if self._angle_mode == AngleMode.DEG else val

    def _acos(self, x: float) -> float:
        if x < -1.0 or x > 1.0:
            raise MathDomainError("acos argument must be in domain [-1, 1]")
        val = math.acos(x)
        return math.degrees(val) if self._angle_mode == AngleMode.DEG else val

    def _atan(self, x: float) -> float:
        val = math.atan(x)
        return math.degrees(val) if self._angle_mode == AngleMode.DEG else val

    def _sqrt(self, x: float) -> float:
        if x < 0:
            raise MathDomainError("Cannot compute square root of a negative number")
        return math.sqrt(x)

    def _log10(self, x: float) -> float:
        if x <= 0:
            raise MathDomainError("Logarithm argument must be positive")
        return math.log10(x)

    def _ln(self, x: float) -> float:
        if x <= 0:
            raise MathDomainError("Natural logarithm argument must be positive")
        return math.log(x)

    def _exp(self, x: float) -> float:
        if x > 709.78:
            raise CalculationOverflowError("Exponential result exceeds numeric limit")
        return math.exp(x)

    def _fact(self, n: Any) -> int:
        if not isinstance(n, (int, float)):
            raise MathDomainError("Factorial requires a numeric input")
        if isinstance(n, float):
            if not n.is_integer():
                raise MathDomainError("Factorial requires an integer")
            n = int(n)
        if n < 0:
            raise MathDomainError("Factorial requires a non-negative integer")
        if n > self.MAX_FACTORIAL_INPUT:
            raise CalculationOverflowError(
                f"Factorial exceeds supported limit (maximum input is {self.MAX_FACTORIAL_INPUT})"
            )
        return math.factorial(n)

    def _pow(self, base: float, exponent: float) -> float:
        if abs(exponent) > self.MAX_EXPONENT:
            raise CalculationOverflowError("Exponent exceeds safety limit")
        if abs(base) > 10 and abs(exponent) > 300:
            raise CalculationOverflowError("Power calculation exceeds numeric bounds")
        if base < 0 and not float(exponent).is_integer():
            raise MathDomainError("Negative base with fractional exponent produces complex result")
        try:
            res = base ** exponent
            if isinstance(res, complex):
                raise MathDomainError("Complex results are not supported in real mode")
            if not math.isfinite(res):
                raise CalculationOverflowError("Result exceeds numerical limits")
            return res
        except OverflowError:
            raise CalculationOverflowError("Result exceeds numerical limits")

    def _build_context(self) -> Dict[str, Any]:
        """Construct the execution context with mathematical functions and constants."""
        return {
            "functions": {
                "sin": self._sin,
                "cos": self._cos,
                "tan": self._tan,
                "asin": self._asin,
                "acos": self._acos,
                "atan": self._atan,
                "arcsin": self._asin,
                "arccos": self._acos,
                "arctan": self._atan,
                "log": self._log10,
                "log10": self._log10,
                "ln": self._ln,
                "exp": self._exp,
                "sqrt": self._sqrt,
                "fact": self._fact,
                "factorial": self._fact,
                "abs": abs,
                "pow": self._pow,
            },
            "constants": {
                "pi": math.pi,
                "e": math.e,
            },
        }

    # -------------------------------------------------------------------------
    # AST Recursive Evaluator
    # -------------------------------------------------------------------------

    def _eval_node(self, node: ast.AST, context: Dict[str, Any]) -> Union[int, float]:
        if isinstance(node, ast.Expression):
            return self._eval_node(node.body, context)

        elif isinstance(node, ast.Constant):
            if isinstance(node.value, (int, float)):
                return node.value
            raise SecurityError(f"Unsupported literal type: {type(node.value).__name__}")

        elif isinstance(node, ast.Name):
            if node.id in context["constants"]:
                return context["constants"][node.id]
            raise CalculatorError(f"Unknown variable or constant: '{node.id}'")

        elif isinstance(node, ast.UnaryOp):
            operand = self._eval_node(node.operand, context)
            if isinstance(node.op, ast.UAdd):
                return +operand
            elif isinstance(node.op, ast.USub):
                return -operand
            raise CalculatorError(f"Unsupported unary operator: {type(node.op).__name__}")

        elif isinstance(node, ast.BinOp):
            left = self._eval_node(node.left, context)
            right = self._eval_node(node.right, context)

            if isinstance(node.op, ast.Add):
                res = left + right
            elif isinstance(node.op, ast.Sub):
                res = left - right
            elif isinstance(node.op, ast.Mult):
                res = left * right
            elif isinstance(node.op, ast.Div):
                if right == 0:
                    raise CalculationZeroDivisionError("Cannot divide by zero")
                res = left / right
            elif isinstance(node.op, ast.Mod):
                if right == 0:
                    raise CalculationZeroDivisionError("Cannot modulo by zero")
                res = left % right
            elif isinstance(node.op, ast.Pow):
                res = self._pow(left, right)
            else:
                raise CalculatorError(f"Unsupported binary operator: {type(node.op).__name__}")

            if not math.isfinite(res):
                raise CalculationOverflowError("Result exceeds supported numeric limits")
            return res

        elif isinstance(node, ast.Call):
            if not isinstance(node.func, ast.Name):
                raise SecurityError("Only direct named function calls are allowed")
            func_name = node.func.id
            funcs = context["functions"]
            if func_name not in funcs:
                raise SecurityError(f"Function '{func_name}' is not supported")

            args = [self._eval_node(arg, context) for arg in node.args]
            func = funcs[func_name]
            try:
                res = func(*args)
            except (CalculatorError, MathDomainError, CalculationOverflowError):
                raise
            except TypeError as e:
                raise CalculatorSyntaxError(f"Incorrect number of arguments for {func_name}: {str(e)}")
            except OverflowError:
                raise CalculationOverflowError(f"Calculation in {func_name} resulted in overflow")
            except Exception as e:
                raise CalculatorError(f"Error in {func_name}: {str(e)}")

            if isinstance(res, (int, float)) and not math.isfinite(res):
                raise CalculationOverflowError("Result exceeds supported numeric limits")
            return res

        else:
            raise SecurityError(f"Unsupported syntax construct: {type(node).__name__}")

    # -------------------------------------------------------------------------
    # Formatting
    # -------------------------------------------------------------------------

    @classmethod
    def format_result(cls, value: Union[int, float]) -> str:
        """Format calculation result for clean readability and numerical precision."""
        if isinstance(value, int):
            return str(value)

        # Check if float is an exact integer or within floating imprecision epsilon
        if value.is_integer():
            return str(int(value))

        nearest_int = round(value)
        if abs(value - nearest_int) < 1e-12 and abs(value) < 1e12:
            return str(int(nearest_int))

        # Scientific notation for extreme magnitudes
        abs_val = abs(value)
        if (abs_val >= 1e14) or (0 < abs_val < 1e-9):
            sci = f"{value:.8e}"
            parts = sci.split("e")
            mantissa = parts[0].rstrip("0").rstrip(".")
            return f"{mantissa}e{parts[1]}"

        # Standard clean floating precision (trimmed trailing zeros)
        rounded = round(value, cls.FLOAT_ROUND_DIGITS)
        s = f"{rounded:.12f}".rstrip("0").rstrip(".")
        return s if s else "0"

    # -------------------------------------------------------------------------
    # Public Evaluation Interface
    # -------------------------------------------------------------------------

    def evaluate(self, expression_str: str) -> CalculationResult:
        """Evaluate a mathematical expression string and return a CalculationResult."""
        original_expr = expression_str
        try:
            sanitized = ExpressionParser.sanitize(expression_str)
            tree = ExpressionParser.parse(expression_str)
            context = self._build_context()
            raw_res = self._eval_node(tree, context)

            formatted = self.format_result(raw_res)
            return CalculationResult(
                expression=original_expr,
                sanitized_expression=sanitized,
                raw_result=raw_res,
                formatted_result=formatted,
                angle_mode=self._angle_mode,
                success=True,
                error_message=None,
            )

        except (CalculatorError, MathDomainError, SecurityError, CalculationZeroDivisionError, CalculationOverflowError) as e:
            return CalculationResult(
                expression=original_expr,
                sanitized_expression="",
                raw_result=None,
                formatted_result="Error",
                angle_mode=self._angle_mode,
                success=False,
                error_message=str(e),
            )
        except Exception as e:
            return CalculationResult(
                expression=original_expr,
                sanitized_expression="",
                raw_result=None,
                formatted_result="Error",
                angle_mode=self._angle_mode,
                success=False,
                error_message=f"Evaluation error: {str(e)}",
            )
