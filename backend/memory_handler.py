# backend/memory_handler.py
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


def store_recap(key: str, recap: Dict[str, Any], session_id: Optional[str] = None) -> None:
    """
    Persist a recap dict to disk under a given key.
    Raises IOError if write fails.
    """
    path = _key_to_path(key, session_id)
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(recap, f, ensure_ascii=False, indent=2)
    except IOError as e:
        logger.error(f"Failed to store recap at {path}: {e}")
        raise


def load_cached_recap(key: str, session_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a recap dict from disk.
    Raises FileNotFoundError if missing, JSONDecodeError/IOError if unreadable,
    or ValueError if the data is not a dict.
    """
    path = _key_to_path(key, session_id)
    if not path.exists():
        raise FileNotFoundError(f"No recap found at {path}")

    try:
        with path.open("r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            raise ValueError(f"Invalid recap format at {path}")
        return {str(k): v for k, v in raw.items()}
    except (IOError, JSONDecodeError) as e:
        logger.error(f"Failed to load recap at {path}: {e}")
        raise
