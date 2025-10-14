"""
Ariadne Clew: AWS AgentCore-powered reasoning agent.
Uses the real AWS AgentCore Runtime API with BedrockAgentCoreApp.

Built for AWS Agent Hackathon - demonstrates AgentCore integration
with reasoning extraction and structured recap generation.

Ariadne Clew: Bedrock AgentCore agent (HTML human_readable)

This variant returns `human_readable` as minimal HTML (<h2>, <ul><li>) so it looks
like a proper list in UIs that collapse newlines and ignore Markdown.

Everything else stays the same: robust Strands parsing + schema-safe normalization.
"""

from __future__ import annotations

import html
import json
import logging
import re
import sys
from typing import Any, Dict, List, Optional

# Real AWS AgentCore imports
from bedrock_agentcore import BedrockAgentCoreApp  # must exist in your env
from strands import Agent  # must exist in your env

# Schema + formatter (optional, but expected)
try:
    from backend.schema import Recap  # Pydantic model
except Exception:
    Recap = None  # tolerate absence

try:
    from backend.recap_formatter import format_recap
except Exception:
    def format_recap(model):  # graceful fallback
        try:
            return model.model_dump()  # type: ignore[attr-defined]
        except Exception:
            return {}

# Configure logging to stdout for CloudWatch
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger(__name__)

# Initialize AWS AgentCore app and agent
app = BedrockAgentCoreApp()
agent = Agent()

def debug_print(msg: str):
    """Print with flush for immediate CloudWatch visibility"""
    print(msg, flush=True)

# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------

_JSON_FENCE = re.compile(r"```json\s*(.+?)\s*```", re.DOTALL | re.IGNORECASE)

def _extract_json_from_text(text: str) -> Optional[Dict[str, Any]]:
    """Extract dict from either a ```json fenced block or raw JSON string."""
    if not isinstance(text, str):
        return None
    m = _JSON_FENCE.search(text)
    raw = m.group(1) if m else text
    raw = raw.strip()
    try:
        return json.loads(raw)
    except Exception:
        return None

def _looks_like_agent_wrapper(d: Dict[str, Any]) -> bool:
    """Detect a Strands-style wrapper: {'role':'assistant','content':[{'text': '...'}]}"""
    if not isinstance(d, dict):
        return False
    if "role" in d and "content" in d and isinstance(d["content"], list):
        if d["content"] and isinstance(d["content"][0], dict) and "text" in d["content"][0]:
            return True
    return False

def _parse_agent_result(result: Any) -> Dict[str, Any]:
    """
    Convert Strands result into the analysis dict with keys like aha_moments, code_snippets, etc.
    Order:
      1) result.content[0].text
      2) result.message (wrapper or raw/fenced JSON)
      3) dict wrapper
      4) already-dict
      5) {}
    """
    # 1) content[0].text
    try:
        content = getattr(result, "content", None)
        if isinstance(content, list) and content and isinstance(content[0], dict):
            text = content[0].get("text")
            parsed = _extract_json_from_text(text or "")
            if isinstance(parsed, dict) and parsed:
                return parsed
    except Exception:
        pass

    # 2) message
    try:
        message = getattr(result, "message", None)
        if isinstance(message, dict) and _looks_like_agent_wrapper(message):
            try:
                text = message["content"][0].get("text", "")
                parsed = _extract_json_from_text(text)
                if isinstance(parsed, dict) and parsed:
                    return parsed
            except Exception:
                pass
        parsed = _extract_json_from_text(message or "")
        if isinstance(parsed, dict) and parsed:
            return parsed
    except Exception:
        pass

    # 3) dict wrapper or already-dict
    if isinstance(result, dict):
        if _looks_like_agent_wrapper(result):
            try:
                text = result["content"][0].get("text", "")
                parsed = _extract_json_from_text(text)
                if isinstance(parsed, dict) and parsed:
                    return parsed
            except Exception:
                pass
        return result

    # Fallback
    return {}

def _normalize_for_schema(analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a payload compatible with Recap.model_validate:
      - final: SINGLE snippet object
      - don't include unknown fields (e.g., scope_creep) here
    """
    snips = analysis.get("code_snippets") or []
    if isinstance(snips, list) and snips:
        s = snips[0] if isinstance(snips[0], dict) else {}
        final_snip = {
            "language": s.get("language", "text"),
            "content": s.get("content", ""),
            "user_marked_final": bool(s.get("user_marked_final", False)),
            "context": s.get("context", ""),
        }
    else:
        final_snip = {"language": "text", "content": "", "user_marked_final": False, "context": ""}

    return {
        "session_id": analysis.get("session_id"),
        "summary": analysis.get("summary", ""),
        "final": final_snip,
        "rejected_versions": analysis.get("rejected_versions", []),
        "aha_moments": analysis.get("aha_moments", []),
    }

def _to_html_list(items: List[str]) -> str:
    if not items:
        return ""
    safe = "".join(f"<li>{html.escape(str(i))}</li>" for i in items)
    return f"<ul>{safe}</ul>"

def _generate_human_summary_html(analysis: Dict[str, Any]) -> str:
    """
    Compose an HTML summary with clear sections and bullets.
    Works even if the consumer collapses newlines or ignores Markdown.
    """
    session_id = html.escape(analysis.get("session_id", "unknown-session"))
    aha = analysis.get("aha_moments") or []
    mvp = analysis.get("mvp_changes") or []
    tradeoffs = analysis.get("design_tradeoffs") or []
    post = analysis.get("post_mvp_ideas") or []
    snips = analysis.get("code_snippets") or []
    summary = html.escape(analysis.get("summary") or "")

    parts: List[str] = []
    parts.append(f"<h2>Session: {session_id}</h2>")

    if summary:
        parts.append("<h3>Summary</h3>")
        parts.append(f"<p>{summary}</p>")

    if aha:
        parts.append("<h3>Key Insights</h3>")
        parts.append(_to_html_list([str(a) for a in aha]))

    if mvp:
        parts.append("<h3>MVP Changes</h3>")
        parts.append(_to_html_list([str(c) for c in mvp]))

    if tradeoffs:
        parts.append("<h3>Design Tradeoffs</h3>")
        parts.append(_to_html_list([str(t) for t in tradeoffs]))

    if snips:
        parts.append("<h3>Code Discovered</h3>")
        labels = []
        for s in snips[:3]:
            lang = (s or {}).get("language", "text")
            ctx = (s or {}).get("context", "")
            label = f"[{lang}] {ctx}".strip() or f"[{lang}] snippet"
            labels.append(label)
        parts.append(_to_html_list(labels))

    if post:
        parts.append("<h3>Post-MVP Ideas</h3>")
        parts.append(_to_html_list([str(p) for p in post]))

    html_text = "".join(parts).strip()
    return html_text or "<p>No structured insights were returned by the agent.</p>"

# -----------------------------------------------------------------------------
# Core class
# -----------------------------------------------------------------------------

class AriadneClew:
    """
    AWS AgentCore-powered reasoning agent using the real BedrockAgentCoreApp.
    """

    def __init__(self, session_id: str = "default"):
        self.session_id = session_id
        self.app = app
        self.agent = agent
        debug_print(f"🎯 AriadneClew initialized for session: {session_id}")

    def process_transcript_sync(self, chat_log: str) -> Dict[str, Any]:
        """
        Build prompt → call Strands → parse → human_readable (HTML) + structured
        """
        debug_print("="*80)
        debug_print("🚀 STARTING TRANSCRIPT PROCESSING")
        debug_print(f"Session ID: {self.session_id}")
        debug_print(f"Chat log length: {len(chat_log)} chars")
        debug_print("="*80)

        if not chat_log or not isinstance(chat_log, str):
            raise ValueError("Invalid chat_log: must be non-empty string")

        # 1) Build prompt
        debug_print("📝 Building reasoning prompt...")
        prompt = self._build_reasoning_prompt(chat_log)
        debug_print(f"✓ Prompt built: {len(prompt)} chars")

        # 2) Call Strands
        debug_print("🤖 Calling Strands agent...")
        result = self.agent(prompt)
        debug_print("✓ Strands agent returned")

        # 3) Parse
        debug_print("🔧 Extracting analysis from result...")
        analysis = _parse_agent_result(result)
        if not analysis:
            debug_print("⚠️  No analysis extracted; defaulting to empty dict.")
            analysis = {}
        analysis["session_id"] = self.session_id
        debug_print("✓ Analysis extracted")

        # 4) Format
        debug_print("🎨 Formatting for output...")
        recap = self._format_for_demo(analysis)
        debug_print("✓ Formatting complete")

        debug_print("="*80)
        debug_print("✅ TRANSCRIPT PROCESSING COMPLETE")
        debug_print("="*80)

        return recap

    def _build_reasoning_prompt(self, chat_log: str) -> str:
        """Build the reasoning extraction prompt for AgentCore"""
        return f"""
You are Ariadne Clew, a reasoning preservation agent for AI-native builders.

Analyze this chat transcript and extract structured insights (aha_moments, mvp_changes, code_snippets, design_tradeoffs, scope_creep, readme_notes, post_mvp_ideas, quality_flags, summary).

Return ONLY valid JSON.
Chat transcript:
{chat_log}
"""

    def _format_for_demo(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Format output for the demo/bridge while validating against Recap if present."""
        debug_print("🎨 FORMATTING FOR DEMO")

        # Human summary (HTML)
        human_readable = _generate_human_summary_html(analysis)

        # Schema normalize + validate
        try:
            safe = _normalize_for_schema(analysis)
            if Recap is not None:
                recap_model = Recap.model_validate(safe)
                structured_data = format_recap(recap_model)
            else:
                structured_data = analysis
            debug_print("  ✅ Schema validation passed (or skipped)")
        except Exception as e:
            debug_print(f"  ⚠️  Schema validation failed: {e}")
            structured_data = analysis  # fallback

        return {
            "human_readable": human_readable,
            "structured_data": structured_data,
            "session_id": self.session_id,
            "agent_metadata": {
                "processed_by": "AriadneClew",
                "agentcore_runtime": "BedrockAgentCoreApp",
                "strands_agent": True,
                "code_snippets_found": len(analysis.get("code_snippets", [])),
                "insights_extracted": len(analysis.get("aha_moments", []))
            }
        }

# -----------------------------------------------------------------------------
# AgentCore entrypoint
# -----------------------------------------------------------------------------

@app.entrypoint
def invoke(payload):
    """
    AWS AgentCore entrypoint for Ariadne Clew.
    """
    debug_print("="*80)
    debug_print("🎯 AGENTCORE ENTRYPOINT INVOKED")
    debug_print(f"  Payload type: {type(payload)}")
    debug_print(f"  Payload keys: {list(payload.keys()) if isinstance(payload, dict) else 'NOT A DICT'}")
    debug_print("="*80)

    try:
        chat_log = payload.get("chat_log") or payload.get("prompt") or payload.get("message")
        session_id = payload.get("session_id", "agentcore-session")

        if not chat_log:
            error_msg = "Missing chat content."
            debug_print(f"  ❌ {error_msg}")
            return {"error": error_msg, "status": "failed"}

        ariadne = AriadneClew(session_id=session_id)
        result = ariadne.process_transcript_sync(chat_log)

        debug_print("="*80)
        debug_print("✅ AGENTCORE ENTRYPOINT COMPLETE")
        debug_print("="*80)

        return {"status": "success", "result": result}

    except Exception as e:
        error_msg = f"AgentCore entrypoint failed: {str(e)}"
        debug_print("="*80)
        debug_print(f"❌ ENTRYPOINT ERROR: {error_msg}")
        debug_print("="*80)
        logger.error(error_msg, exc_info=True)
        return {"status": "failed", "error": error_msg}

# For local bare run (AgentCore will normally handle the service lifecycle)
if __name__ == "__main__":
    debug_print("🚀 Starting Ariadne Clew AgentCore app...")
    app.run()
