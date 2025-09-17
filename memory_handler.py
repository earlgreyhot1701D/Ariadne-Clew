""" 
memory_handler.py
Lightweight wrapper for Bedrock AgentCore Memory API.
Stores and retrieves final chosen code snippets across sessions.
"""

from typing import Dict, Optional

try:
    from agent import memory  # Bedrock AgentCore runtime
    AGENTCORE_AVAILABLE = True
except ImportError:
    AGENTCORE_AVAILABLE = False

_memory_store: Dict[str, Dict] = {}  # fallback local store

def store_memory(session_id: str, recap: Dict) -> str:
    """Stores a recap in Bedrock memory or fallback local store."""
    if not isinstance(session_id, str) or not isinstance(recap, dict):
        raise ValueError("Invalid session_id or recap format")

    if AGENTCORE_AVAILABLE:
        try:
            memory.store(key=session_id, value=recap)
            return session_id
        except Exception as e:
            return f"store_failed: {str(e)}"
    else:
        _memory_store[session_id] = recap
        return session_id

def retrieve_memory(session_id: str) -> Optional[Dict]:
    """Retrieves recap data for a given session ID."""
    if not isinstance(session_id, str):
        raise ValueError("Invalid session_id")

    if AGENTCORE_AVAILABLE:
        try:
            return memory.get(key=session_id)
        except Exception:
            return None
    else:
        return _memory_store.get(session_id)

def summarize_memory(memory_obj: Optional[Dict]) -> str:
    """Creates a summary message from stored memory object."""
    if not memory_obj or not isinstance(memory_obj, dict):
        return "No memory found for this session."

    try:
        snippets = memory_obj.get("snippets", [])
        if not snippets:
            return "No snippets were stored in this session."
        final = snippets[-1]
        return (
            f"In this session, the final snippet (v{final['version']}) "
            f"was validated and stored as the chosen version."
        )
    except Exception:
        return "Memory content was unreadable."
