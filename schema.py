# schema.py
"""
Shared schema definitions and validation helpers for Ariadne Agent.
"""
from typing import Dict, List, Any

REQUIRED_SNIPPET_FIELDS = ["version", "snippet_id", "content", "diff_summary"]

def _validate_snippet(snippet: Dict[str, Any], context: str) -> None:
    if not isinstance(snippet, dict):
        raise ValueError(f"{context} must be a dict")
    for field in REQUIRED_SNIPPET_FIELDS:
        if field not in snippet:
            raise ValueError(f"{context} missing required field: {field}")

def validate_recap_output(data: Dict[str, Any]) -> bool:
    """
    Validates the recap output structure from diff_code_blocks.

    Args:
        data (dict): Output dictionary expected to match RecapOutput format.

    Returns:
        bool: True if structure is valid, raises ValueError otherwise.
    """
    if not isinstance(data, dict):
        raise ValueError("Recap data must be a dictionary")

    for key in ["final", "rejected", "text_summary"]:
        if key not in data:
            raise ValueError(f"Missing recap field: {key}")

    _validate_snippet(data["final"], "Final snippet")

    if not isinstance(data["rejected"], list):
        raise ValueError("Rejected must be a list")

    for idx, snippet in enumerate(data["rejected"]):
        _validate_snippet(snippet, f"Rejected snippet at index {idx}")

    if not isinstance(data["text_summary"], str):
        raise ValueError("text_summary must be a string")

    return True
