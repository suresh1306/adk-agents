"""
Custom Calculator Tools for Google ADK

This module provides mathematical calculation tools.
"""

import math
from typing import Dict, Union, Optional


def calculate(expression: str) -> Dict[str, Union[str, float]]:
    """
    Evaluate a mathematical expression safely.

    Use this tool to perform calculations like addition, subtraction,
    multiplication, division, exponents, and basic functions.

    Supported operations:
    - Basic arithmetic: +, -, *, /, //, %, **
    - Functions: sqrt, sin, cos, tan, log, ln, abs, round
    - Constants: pi, e

    Args:
        expression: A mathematical expression as a string (e.g., "2 + 2", "sqrt(16)", "sin(45)")

    Returns:
        A dictionary with the result and the original expression
    """
    try:
        # Define safe functions and constants
        safe_dict = {
            # Math functions
            "sqrt": math.sqrt,
            "sin": math.sin,
            "cos": math.cos,
            "tan": math.tan,
            "log": math.log10,
            "ln": math.log,
            "abs": abs,
            "round": round,
            "pow": pow,
            "exp": math.exp,
            "floor": math.floor,
            "ceil": math.ceil,
            # Constants
            "pi": math.pi,
            "e": math.e,
        }

        # Evaluate the expression safely
        result = eval(expression, {"__builtins__": {}}, safe_dict)

        return {
            "expression": expression,
            "result": float(result),
            "success": True
        }

    except Exception as e:
        return {
            "expression": expression,
            "error": f"Calculation error: {str(e)}",
            "success": False
        }


def advanced_math(operation: str, value: float, value2: Optional[float] = None) -> Dict[str, Union[str, float]]:
    """
    Perform advanced mathematical operations.

    Use this for trigonometric functions, logarithms, exponentials, and other
    advanced mathematical operations.

    Args:
        operation: The operation to perform (sin, cos, tan, log, ln, sqrt, exp, etc.)
        value: The primary input value
        value2: Optional second value for operations like pow(value, value2)

    Returns:
        A dictionary with the result of the operation
    """
    try:
        operations = {
            "sin": lambda x, y=None: math.sin(math.radians(x)),
            "cos": lambda x, y=None: math.cos(math.radians(x)),
            "tan": lambda x, y=None: math.tan(math.radians(x)),
            "log": lambda x, y=None: math.log10(x),
            "ln": lambda x, y=None: math.log(x),
            "sqrt": lambda x, y=None: math.sqrt(x),
            "exp": lambda x, y=None: math.exp(x),
            "pow": lambda x, y: pow(x, y),
            "abs": lambda x, y=None: abs(x),
            "factorial": lambda x, y=None: math.factorial(int(x)),
        }

        if operation not in operations:
            return {
                "operation": operation,
                "error": f"Unknown operation: {operation}",
                "success": False
            }

        result = operations[operation](value, value2)

        return {
            "operation": operation,
            "input": value if value2 is None else (value, value2),
            "result": float(result),
            "success": True
        }

    except Exception as e:
        return {
            "operation": operation,
            "error": f"Calculation error: {str(e)}",
            "success": False
        }
