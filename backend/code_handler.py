from __future__ import annotations

import ast

def validate_snippet(code: str) -> bool:
    """
    Validate if the provided string is valid Python code.

    Args:
        code: A string containing the code snippet to validate.

    Returns:
        True if the code is syntactically valid, otherwise False.
    """
    try:
        ast.parse(code)
        return True
    except SyntaxError:
        return False
