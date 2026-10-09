"""Expression parser and sanitizer for NovaCalc.

Transforms mathematical expressions into safe AST representations,
resolving symbols, factorials, roots, implicit multiplication,
and verifying security constraints.
"""

from __future__ import annotations
import ast
import re
from typing import Set


class CalculatorError(Exception):
    """Base exception class for NovaCalc calculation errors."""
    pass


class CalculatorSyntaxError(CalculatorError):
    """Raised when an expression has invalid syntax or malformed tokens."""
    pass


# Alias for compatibility with PRD naming
SyntaxError = CalculatorSyntaxError


class MathDomainError(CalculatorError):
    """Raised when a mathematical operation receives an argument outside its domain."""
    pass


class SecurityError(CalculatorError):
    """Raised when an expression attempts unauthorized syntax or function calls."""
    pass


class CalculationZeroDivisionError(CalculatorError):
    """Raised when division or modulo by zero occurs."""
    pass


class CalculationOverflowError(CalculatorError):
    """Raised when a calculation exceeds supported numeric boundaries."""
    pass


class ExpressionParser:
    """Parses and validates mathematical expressions safely using Python's AST."""

    # Allowed function names in mathematical expressions
    ALLOWED_FUNCTIONS: Set[str] = {
        "sin", "cos", "tan",
        "asin", "acos", "atan",
        "arcsin", "arccos", "arctan",
        "log", "log10", "ln",
        "exp", "sqrt",
        "fact", "factorial",
        "abs", "pow",
    }

    # Allowed constant identifiers
    ALLOWED_CONSTANTS: Set[str] = {"pi", "e"}

    # Whitelist of permissible AST node types
    ALLOWED_NODES: tuple = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Call,
        ast.Constant,
        ast.Name,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Mod,
        ast.Pow,
        ast.UAdd,
        ast.USub,
        ast.Load,
    )

    @classmethod
    def sanitize(cls, expr: str) -> str:
        """Sanitize and normalize user mathematical expression string."""
        if not expr or not expr.strip():
            raise CalculatorSyntaxError("Expression is empty")

        cleaned = expr.strip()

        # 1. Normalize unicode mathematical symbols and characters
        cleaned = cleaned.replace("×", "*")
        cleaned = cleaned.replace("÷", "/")
        cleaned = cleaned.replace("−", "-")  # Unicode minus U+2212
        cleaned = cleaned.replace("–", "-")  # En-dash U+2013
        cleaned = cleaned.replace("—", "-")  # Em-dash U+2014
        cleaned = cleaned.replace("π", "pi")
        cleaned = cleaned.replace("²", "^2")
        cleaned = cleaned.replace("³", "^3")

        # 2. Normalize absolute value bars |expr| -> abs(expr)
        cleaned = cls._transform_absolute_bars(cleaned)

        # 3. Normalize square root symbols √
        cleaned = cls._transform_square_roots(cleaned)

        # 4. Normalize factorial operator ! -> fact(...)
        cleaned = cls._transform_factorials(cleaned)

        # 5. Normalize powers ^ -> **
        cleaned = cleaned.replace("^", "**")

        # 6. Normalize function aliases
        cleaned = re.sub(r"\barcsin\b", "asin", cleaned)
        cleaned = re.sub(r"\barccos\b", "acos", cleaned)
        cleaned = re.sub(r"\barctan\b", "atan", cleaned)

        # 7. Expand implicit multiplication
        cleaned = cls._expand_implicit_multiplication(cleaned)

        return cleaned

    @classmethod
    def _transform_absolute_bars(cls, expr: str) -> str:
        """Transform vertical bars |x| into abs(x)."""
        if "|" not in expr:
            return expr

        result = []
        i = 0
        n = len(expr)

        while i < n:
            ch = expr[i]
            if ch == "|":
                # Look backwards for previous non-whitespace character
                prev_ch = None
                j = len(result) - 1
                while j >= 0:
                    if not result[j].isspace():
                        prev_ch = result[j]
                        break
                    j -= 1

                # If at start or following an operator / open paren, it's an opening bar
                if prev_ch is None or prev_ch in "+-*/%^(,":
                    result.append("abs(")
                else:
                    result.append(")")
            else:
                result.append(ch)
            i += 1

        return "".join(result)

    @classmethod
    def _transform_square_roots(cls, expr: str) -> str:
        """Transform √16 or √(16) into sqrt(16)."""
        if "√" not in expr:
            return expr

        # Replace √(expr) with sqrt(expr)
        expr = re.sub(r"√\s*\(", "sqrt(", expr)

        # Replace √number with sqrt(number), e.g. √144 -> sqrt(144)
        expr = re.sub(r"√\s*([0-9]+(?:\.[0-9]+)?)", r"sqrt(\1)", expr)

        # Replace remaining standalone √ with sqrt
        expr = expr.replace("√", "sqrt")
        return expr

    @classmethod
    def _transform_factorials(cls, expr: str) -> str:
        """Transform postfix factorial '!' into fact(...) function calls."""
        # Check if there is any exclamation mark not part of !=
        while True:
            # Match an exclamation mark that is not preceded or followed by =
            idx = -1
            for k in range(len(expr)):
                if expr[k] == "!":
                    if (k + 1 < len(expr) and expr[k + 1] == "=") or (k > 0 and expr[k - 1] == "!"):
                        continue
                    idx = k
                    break

            if idx == -1:
                break

            # Find what precedes idx
            prev_idx = idx - 1
            while prev_idx >= 0 and expr[prev_idx].isspace():
                prev_idx -= 1

            if prev_idx < 0:
                raise CalculatorSyntaxError("Unexpected factorial operator '!' with no operand")

            if expr[prev_idx] == ")":
                # Find matching opening '('
                depth = 1
                start = prev_idx - 1
                while start >= 0 and depth > 0:
                    if expr[start] == ")":
                        depth += 1
                    elif expr[start] == "(":
                        depth -= 1
                    start -= 1
                start += 1  # Index of matching '('

                if depth > 0:
                    raise CalculatorSyntaxError("Mismatched parentheses before '!'")

                # If the parenthesis is part of a function call, like sqrt(16)!, wrap the whole function
                fn_start = start - 1
                while fn_start >= 0 and expr[fn_start].isspace():
                    fn_start -= 1
                if fn_start >= 0 and (expr[fn_start].isalnum() or expr[fn_start] == "_"):
                    word_start = fn_start
                    while word_start >= 0 and (expr[word_start].isalnum() or expr[word_start] == "_"):
                        word_start -= 1
                    start = word_start + 1

                target = expr[start:idx].strip()
                expr = expr[:start] + f"fact({target})" + expr[idx + 1:]

            else:
                # Preceding is identifier or number
                start = prev_idx
                while start >= 0 and (expr[start].isalnum() or expr[start] in "._"):
                    start -= 1
                start += 1

                target = expr[start:idx].strip()
                if not target:
                    raise CalculatorSyntaxError("Invalid operand for factorial")
                expr = expr[:start] + f"fact({target})" + expr[idx + 1:]

        return expr

    @classmethod
    def _expand_implicit_multiplication(cls, expr: str) -> str:
        """Insert '*' for implicit multiplications such as 2pi, 2(3), (2)(3), 3sin(30)."""
        # 1. Number immediately followed by parenthesis: e.g. 2(3) -> 2*(3)
        expr = re.sub(r"(\d+(?:\.\d+)?)\s*\(", r"\1*(", expr)

        # 2. Closing paren followed by opening paren: (2)(3) -> (2)*(3)
        expr = re.sub(r"\)\s*\(", r")*(", expr)

        # 3. Closing paren followed by number: (2)3 -> (2)*3
        expr = re.sub(r"\)\s*(\d+(?:\.\d+)?)", r")*\1", expr)

        # 4. Number followed by constant 'pi': 2pi -> 2*pi
        expr = re.sub(r"(\d+(?:\.\d+)?)\s*(pi)\b", r"\1*\2", expr)

        # 5. Number followed by constant 'e', when not scientific notation (e.g. 2e3 or 1e-4)
        # Match number followed by 'e' where 'e' is NOT followed by a digit or [+ -]\d
        expr = re.sub(r"(\d+(?:\.\d+)?)\s*e(?![+-]?\d)", r"\1*e", expr)

        # 6. Number followed by supported function name: e.g. 3sin(30) -> 3*sin(30)
        fn_pattern = "|".join(cls.ALLOWED_FUNCTIONS)
        expr = re.sub(rf"(\d+(?:\.\d+)?)\s*({fn_pattern})\b", r"\1*\2", expr)

        # 7. Closing paren followed by constant or function: (2)pi -> (2)*pi, (2)sin(30) -> (2)*sin(30)
        expr = re.sub(rf"\)\s*(pi|e|{fn_pattern})\b", r")*\1", expr)

        # 8. Constant 'pi' followed by '(' or number or function: pi(2) -> pi*(2)
        expr = re.sub(rf"\b(pi)\s*\(", r"\1*(", expr)
        expr = re.sub(rf"\b(pi)\s*(\d+(?:\.\d+)?)", r"\1*\2", expr)
        expr = re.sub(rf"\b(pi)\s*({fn_pattern})\b", r"\1*\2", expr)

        # 9. Constant 'e' followed by '(' or number or function: e(2) -> e*(2)
        expr = re.sub(rf"\b(e)\s*\(", r"\1*(", expr)
        expr = re.sub(rf"\b(e)\s*({fn_pattern})\b", r"\1*\2", expr)

        return expr

    @classmethod
    def validate_ast(cls, tree: ast.AST) -> None:
        """Traverse the AST and verify that all nodes and calls strictly conform to whitelist."""
        for node in ast.walk(tree):
            if not isinstance(node, cls.ALLOWED_NODES):
                raise SecurityError(
                    f"Disallowed syntax element '{type(node).__name__}'. Only mathematical expressions are permitted."
                )

            # Validate function calls
            if isinstance(node, ast.Call):
                if not isinstance(node.func, ast.Name):
                    raise SecurityError("Dynamic or attribute-based function calls are prohibited.")
                func_name = node.func.id
                if func_name not in cls.ALLOWED_FUNCTIONS:
                    raise SecurityError(f"Function '{func_name}' is not permitted.")
                if node.keywords:
                    raise SecurityError("Keyword arguments are not allowed in mathematical expressions.")

            # Validate variable/constant identifiers
            elif isinstance(node, ast.Name):
                var_name = node.id
                if var_name not in cls.ALLOWED_CONSTANTS and var_name not in cls.ALLOWED_FUNCTIONS:
                    raise SecurityError(f"Undefined identifier or variable '{var_name}'.")

            # Validate constants
            elif isinstance(node, ast.Constant):
                if not isinstance(node.value, (int, float)):
                    raise SecurityError("Only numerical constants (int, float) are permitted.")

    @classmethod
    def parse(cls, expr: str) -> ast.Expression:
        """Sanitize, parse, and validate an expression string into an AST Expression."""
        sanitized = cls.sanitize(expr)
        try:
            tree = ast.parse(sanitized, mode="eval")
        except SyntaxError as e:
            raise CalculatorSyntaxError(f"Syntax error in expression: {e.msg}") from e
        except Exception as e:
            raise CalculatorSyntaxError(f"Invalid expression: {str(e)}") from e

        cls.validate_ast(tree)
        return tree
