from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)

_CACHE_DIR = Path(".cache")
_CACHE_DIR.mkdir(exist_ok=True)


def _key_to_path(key: str, session_id: Optional[str] = None) -> Path:
    """Sanitize key into a safe filename, optionally namespaced by session."""
    safe_key = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in key)
    if session_id:
        safe_session = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in session_id)
        ns_dir = _CACHE_DIR / safe_session
        ns_dir.mkdir(parents=True, exist_ok=True)
        return ns_dir / f"{safe_key}.json"
    return _CACHE_DIR / f"{safe_key}.json"


def store_recap(key: str, recap: Dict[str, Any], session_id: Optional[str] = None) -> bool:
    """
    Persist a recap dict to disk under a given key.
    Returns True if successful, False otherwise.
    """
    path = _key_to_path(key, session_id)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(recap, f, ensure_ascii=False, indent=2)
        return True
    except IOError as e:
        logger.error(f"Failed to store recap at {path}: {e}")
        return False


def load_cached_recap(key: str, session_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
    """
    Load a recap dict from disk if it exists.
    Returns None if not found or invalid/unreadable.
    """
    path = _key_to_path(key, session_id)
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if isinstance(raw, dict):
            return {str(k): v for k, v in raw.items()}
    except (IOError, JSONDecodeError) as e:
        logger.warning(f"Failed to load recap at {path}: {e}")

    return None
