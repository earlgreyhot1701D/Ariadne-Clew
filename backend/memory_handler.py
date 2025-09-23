from __future__ import annotations

import json
from json import JSONDecodeError
from pathlib import Path
from typing import Any, Dict, Optional

_CACHE_DIR = Path(".cache")
_CACHE_DIR.mkdir(exist_ok=True)


def _key_to_path(key: str) -> Path:
    """Sanitize key into a safe filename under .cache/."""
    safe = "".join(ch if ch.isalnum() or ch in ("-", "_") else "_" for ch in key)
    return _CACHE_DIR / f"{safe}.json"


def store_recap(key: str, recap: Dict[str, Any]) -> None:
    """
    Persist a recap dict to disk under a given key.

    Args:
        key: Identifier for this recap (e.g., session or request ID).
        recap: Recap data to persist (must be JSON-serializable).
    """
    path = _key_to_path(key)
    with path.open("w", encoding="utf-8") as f:
        json.dump(recap, f, ensure_ascii=False, indent=2)


def load_cached_recap(key: str) -> Optional[Dict[str, Any]]:
    """
    Load a recap dict from disk if it exists. Returns None if not found
    or if the file contents are invalid.
    """
    path = _key_to_path(key)
    if not path.exists():
        return None

    try:
        with path.open("r", encoding="utf-8") as f:
            raw: Any = json.load(f)
    except JSONDecodeError:
        return None

    if isinstance(raw, dict):
        # Force keys to str to guarantee Dict[str, Any] type
        return {str(k): v for k, v in raw.items()}
    return None
