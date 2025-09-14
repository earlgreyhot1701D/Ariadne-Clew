# schema.py
"""
Shared schema definitions and validation helpers for Ariadne Agent.
"""

from typing import TypedDict, List, Literal

# === Categories ===
Category = Literal["AHA", "MVP_CHANGE", "SCOPE_CREEP", "README_NOTE", "POST_MVP_IDEA"]


# === Structured Claude Output ===
class ClassifiedItem(TypedDict):
    category: Category
    text: str


class ClaudeResult(TypedDict):
    session_id: str
    timestamp: str
    aha_moments: List[str]
    mvp_changes: List[str]
    scope_creep: List[str]
    readme_notes: List[str]
    post_mvp_ideas: List[str]
    summary: str
    quality_flags: List[str]


# === Validators ===
def validate_claude_result(data: dict) -> bool:
    required_keys = [
        "session_id",
        "timestamp",
        "aha_moments",
        "mvp_changes",
        "scope_creep",
        "readme_notes",
        "post_mvp_ideas",
        "summary",
        "quality_flags",
    ]
    for key in required_keys:
        if key not in data:
            raise ValueError(f"Missing required field: {key}")

    if not isinstance(data["session_id"], str) or not data["session_id"]:
        raise ValueError("Invalid session_id")
    if not isinstance(data["timestamp"], str):
        raise ValueError("Invalid timestamp")
    for field in [
        "aha_moments",
        "mvp_changes",
        "scope_creep",
        "readme_notes",
        "post_mvp_ideas",
        "quality_flags",
    ]:
        if not isinstance(data[field], list):
            raise ValueError(f"Field {field} must be a list")
    return True
