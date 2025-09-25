from __future__ import annotations

from typing import Any, Dict, List


def diff_code_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pick one 'final' code block and mark the rest as rejected.
    Returns all fields required by the Recap schema.

    Args:
        blocks: A list of dictionaries representing code blocks.
                Each must have a "content" key and a "validation" flag.

    Returns:
        A dictionary with all required Recap fields:
            - "final": The content of the first valid code block, or None if none found.
            - "rejected_versions": A list of rejected code blocks with reasons.
            - "summary": A basic summary of the processing
            - "aha_moments": Empty list for now
            - "quality_flags": Basic quality assessment
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

    # Generate a basic summary
    if final:
        summary = f"What You Built: Found valid code snippet. {len(rejected)} rejected versions."
    else:
        summary = f"What You Built: No valid code found. {len(rejected)} rejected versions."

    # Basic quality flags
    quality_flags = []
    if len(rejected) > 0:
        quality_flags.append("⚠️ Some code blocks failed validation")
    if final:
        quality_flags.append("✅ Valid code snippet identified")
    else:
        quality_flags.append("❌ No valid code found")

    return {
        "final": final,
        "rejected_versions": rejected,
        "summary": summary,
        "aha_moments": [],  # Empty for now, will be populated by Bedrock classification later
        "quality_flags": quality_flags,
    }
