# backend/filters.py
import re

# Example deny-listed terms — extend as needed
DENY_TERMS = [
    "api_key",
    "password",
    "secret",
    "rm -rf /",
    "BEGIN RSA PRIVATE KEY"
]
MAX_CHARS = 100_000  # ~20k tokens max
PII_PATTERNS = [
    (re.compile(r"\b\d{3}-\d{2}-\d{4}\b"), "[SSN_REDACTED]"),     # SSN pattern
    (re.compile(r"\b\d{16}\b"), "[CC_REDACTED]"),                 # naive credit card
    (re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"), "[EMAIL_REDACTED]"),  # email
    (re.compile(r"\b\d{3}-\d{3}-\d{4}\b"), "[PHONE_REDACTED]"),  # phone number
]

# Precompiled deny term patterns (case-insensitive)
# Use word boundaries for simple words, but exact match for complex phrases
_DENY_PATTERNS = []
for term in DENY_TERMS:
    if ' ' in term or any(char in term for char in ['-', '/', '\\', '.']):
        # For phrases with spaces or special chars, use exact string matching
        pattern = re.compile(re.escape(term), re.IGNORECASE)
    else:
        # For single words, use word boundaries
        pattern = re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE)
    _DENY_PATTERNS.append(pattern)


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
    for pattern, replacement in PII_PATTERNS:
        scrubbed = pattern.sub(replacement, scrubbed)
    return scrubbed
