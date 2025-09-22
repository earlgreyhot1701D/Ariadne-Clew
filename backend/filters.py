# filters.py
import re

MAX_CHARS = 100_000
DENY_TERMS = ["password", "api_key", "rm -rf /", "BEGIN RSA PRIVATE KEY"]

PII_PATTERNS = [
    (re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"), "[redacted email]"),
    (re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"), "[redacted phone]"),
]

def enforce_size_limit(text: str) -> None:
    """Raise ValueError if input exceeds MAX_CHARS."""
    if len(text) > MAX_CHARS:
        raise ValueError(f"Input too large ({len(text)} chars). Limit is {MAX_CHARS}.")

def contains_deny_terms(text: str) -> bool:
    """Return True if text contains any deny-listed term."""
    lowered = text.lower()
    return any(term in lowered for term in DENY_TERMS)

def scrub_pii(text: str) -> str:
    """Replace emails and phone numbers with redacted tags."""
    cleaned = text
    for pattern, replacement in PII_PATTERNS:
        cleaned = pattern.sub(replacement, cleaned)
    return cleaned
