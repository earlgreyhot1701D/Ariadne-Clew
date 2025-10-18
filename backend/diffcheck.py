# backend/diffcheck.py
from __future__ import annotations
from typing import Any, Dict, List
from backend.schema import EnrichedSnippet, Recap


def diff_code_blocks(blocks: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Pick one 'final' code block, mark the rest as rejected.
    Returns a dict matching the Recap schema.
    """
    final: EnrichedSnippet | None = None
    rejected_versions: List[EnrichedSnippet] = []

    for i, block in enumerate(blocks):
        snippet = EnrichedSnippet(
            version=i + 1,
            snippet_id=block.get("snippet_id", f"snippet_{i+1}"),
            content=block.get("content", ""),
            diff_summary="No change",  # real diffing logic could go here
            validation=block.get("validation", {"status": "unknown"}),
        )

        if block.get("validation", {}).get("status") == "valid":
            if final is None:
                final = snippet
            else:
                snippet.validation["reason"] = "Extra snippet"
                rejected_versions.append(snippet)
        else:
            snippet.validation["reason"] = "Invalid Python"
            rejected_versions.append(snippet)

    summary = (
        f"What You Built: Found valid code snippet. {len(rejected_versions)} rejected versions."
        if final
        else f"What You Built: No valid code found. {len(rejected_versions)} rejected versions."
    )

    quality_flags: List[str] = []
    if rejected_versions:
        quality_flags.append("⚠️ Some code blocks failed validation")
    if final:
        quality_flags.append("✅ Valid code snippet identified")
    else:
        quality_flags.append("❌ No valid code found")

    return Recap(
        final=final,
        rejected_versions=rejected_versions,
        summary=summary,
        aha_moments=[],
        quality_flags=quality_flags,
    ).model_dump()
