"""
code_handler.py
Handles detection, versioning, validation, and reconciliation of code snippets
in chat transcripts for Ariadne Clew.
"""

import logging
from typing import List, Dict
import difflib
import uuid
import ast

# Optional Bedrock AgentCore support
try:
    from agent import tools, memory  # Bedrock AgentCore runtime
    AGENTCORE_AVAILABLE = True
except ImportError as e:
    tools = None
    memory = None
    AGENTCORE_AVAILABLE = False
    logging.warning("AgentCore not available. Running in fallback mode: %s", e)


def extract_code_blocks(text: str) -> List[str]:
    """Detect fenced or inline code blocks in chat text."""
    blocks = []
    if text.count("```") % 2 != 0:
        raise ValueError("Unmatched code fence detected.")
    parts = text.split("```")
    for i in range(1, len(parts), 2):
        blocks.append(parts[i].strip())
    return blocks


def version_snippets(snippets: List[str]) -> List[Dict]:
    """Assign IDs and version numbers to snippets, and generate diffs between versions."""
    results = []
    for i, snippet in enumerate(snippets):
        diff_summary = ""
        if i > 0:
            diff = difflib.unified_diff(
                snippets[i - 1].splitlines(),
                snippet.splitlines(),
                lineterm="",
            )
            diff_summary = "\n".join(diff)

        results.append({
            "snippet_id": str(uuid.uuid4()),
            "version": i + 1,
            "code": snippet,
            "diff_summary": diff_summary
        })
    return results


def validate_snippet(snippet: str) -> Dict:
    """Validate a Python code snippet safely using AST parsing."""
    try:
        ast.parse(snippet)
        return {
            "status": "valid",
            "output": "Parsed successfully.",
            "error": ""
        }
    except SyntaxError as e:
        if "unexpected EOF" in str(e) or snippet.strip().endswith(("=", ":", "(", "[")):
            return {
                "status": "partial",
                "error": "incomplete snippet"
            }
        else:
            return {
                "status": "invalid",
                "error": f"Syntax error: {str(e)}"
            }
    except Exception as e:
        return {
            "status": "invalid",
            "error": str(e)
        }


def reconcile_intent(snippet_data: Dict, user_text: str) -> Dict:
    """Reconcile validation result with user intent inferred from conversation."""
    if "final" in user_text.lower():
        reconciliation = "final accepted"
    elif "maybe" in user_text.lower():
        reconciliation = "draft"
    elif "nevermind" in user_text.lower():
        reconciliation = "rejected"
    else:
        reconciliation = "unknown"

    snippet_data.update({
        "user_intent": reconciliation,
        "reconciliation": reconciliation
    })
    return snippet_data


def summarize_session(snippet_results: List[Dict]) -> Dict:
    """Generate a structured recap for the session."""
    final = None
    for s in reversed(snippet_results):
        if s.get("reconciliation") == "final accepted":
            final = s
            break

    return {
        "final": final or {},
        "all_snippets": snippet_results
    }
