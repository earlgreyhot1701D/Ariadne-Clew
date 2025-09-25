# backend/filters.py
import re

# Example deny-listed terms — extend as needed
DENY_TERMS = ["api_key", "password", "secret"]
MAX_CHARS = 100_000  # ~20k tokens max
PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN pattern
    re.compile(r"\b\d{16}\b"),             # naive credit card
]

# Precompiled deny term patterns (word boundary, case-insensitive)
_DENY_PATTERNS = [re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE) for term in DENY_TERMS]


def contains_deny_terms(text: str) -> bool:
    """Return True if text contains any deny-listed terms (word-boundary, case-insensitive)."""
    return any(p.search(text) for p in _DENY_PATTERNS)


def enforce_size_limit(text: str) -> None:
    """Raise ValueError if text exceeds max char limit."""
    if len(text) > MAX_CHARS:
        raise ValueError(f"Input too long ({len(text)} chars). Limit is {MAX_CHARS:,}.")


def scrub_pii(text: str) -> str:
    """Naively scrub personally identifiable info using regex patterns."""
    scrubbed = text
    for pattern in PII_PATTERNS:
        scrubbed = pattern.sub("[REDACTED]", scrubbed)
    return scrubbed
