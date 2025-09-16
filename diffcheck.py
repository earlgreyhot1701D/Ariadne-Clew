"""
Performs deduplication, versioning, and diffing of classified code blocks.
Used by Ariadne Clew to generate structured recaps from chat logs.
"""

import difflib
from typing import List, TypedDict, Optional


class CodeBlock(TypedDict):
    type: str
    content: str


class EnrichedSnippet(TypedDict):
    version: int
    snippet_id: str
    content: str
    diff_summary: str


class RecapOutput(TypedDict):
    final: EnrichedSnippet
    rejected: List[EnrichedSnippet]
    text_summary: str


def deduplicate_code_snippets(snippets: List[CodeBlock]) -> List[CodeBlock]:
    """
    Removes duplicate code snippets based on their content.

    Args:
        snippets: List of code blocks with 'content'.

    Returns:
        A list of unique code snippets (original order preserved).
    """
    seen = set()
    unique = []

    for snippet in snippets:
        content = snippet.get("content")
        if not content or content in seen:
            continue
        seen.add(content)
        unique.append(snippet)

    return unique


def add_versions(snippets: List[CodeBlock]) -> List[EnrichedSnippet]:
    """
    Adds version numbers, unique snippet IDs, and unified diff summaries.

    Args:
        snippets: Unique, ordered list of code snippets.

    Returns:
        List of enriched snippets with versioning and diffs.
    """
    result: List[EnrichedSnippet] = []
    prev_code = ""

    for i, snippet in enumerate(snippets):
        code = snippet.get("content", "")
        diff = list(
            difflib.unified_diff(
                prev_code.splitlines(),
                code.splitlines(),
                lineterm="",
                n=2,
            )
        )
        result.append({
            "version": i + 1,
            "snippet_id": f"snippet_{i + 1}",
            "content": code,
            "diff_summary": "\n".join(diff) if diff else "No change",
        })
        prev_code = code

    return result


def diff_code_blocks(blocks: List[CodeBlock]) -> RecapOutput:
    """
    Processes classified chat blocks and returns a structured recap.

    Args:
        blocks: List of classified blocks with 'type' and 'content'.

    Returns:
        RecapOutput: Dictionary containing:
            - final: Last (latest) version of code
            - rejected: All previous versions
            - text_summary: Most recent text block
    """
    if not isinstance(blocks, list) or not all(isinstance(b, dict) for b in blocks):
        raise ValueError("blocks must be a list of dicts")

    code_blocks = [b for b in blocks if b.get("type") == "code"]
    text_blocks = [b for b in blocks if b.get("type") == "text"]

    deduped = deduplicate_code_snippets(code_blocks)
    enriched = add_versions(deduped)

    empty_snippet: EnrichedSnippet = {
        "version": 0,
        "snippet_id": "none",
        "content": "",
        "diff_summary": "No snippets available",
    }

    return {
        "final": enriched[-1] if enriched else empty_snippet,
        "rejected": enriched[:-1] if len(enriched) > 1 else [],
        "text_summary": text_blocks[-1]["content"] if text_blocks else "",
    }

