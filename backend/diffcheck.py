from __future__ import annotations

from typing import Any, Dict, List


def diff_code_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pick one 'final' code block and mark the rest as rejected.

    Args:
        blocks: A list of dictionaries representing code blocks.
                Each must have a "content" key and a "validation" flag.

    Returns:
        A dictionary with two keys:
            - "final": The content of the first valid code block, or None if none found.
            - "rejected_versions": A list of rejected code blocks with reasons.
    """
    final: str | None = None
    rejected: List[Dict[str, str]] = []

    for block in blocks:
        if block.get("validation"):
            if final is None:
                final = block["content"]
            else:
                rejected.append({"code": block["content"], "reason": "Extra snippet"})
        else:
            rejected.append(
                {"code": block.get("content", ""), "reason": "Invalid Python"}
            )

    return {
        "final": final,
        "rejected_versions": rejected,
    }
