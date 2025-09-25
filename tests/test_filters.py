# backend/filters.py
import re

# Expanded deny-listed terms (MVP guardrails)
DENY_TERMS = [
    "api_key",
    "password",
    "secret",
    "rm -rf /",
    "BEGIN RSA PRIVATE KEY",
]

MAX_CHARS = 100_000  # ~20k tokens max

# PII patterns: SSN, credit card, email, phone number
PII_PATTERNS = [
    re.compile(r"\b\d{3}-\d{2}-\d{4}\b"),  # SSN
    re.compile(r"\b\d{16}\b"),             # naive credit card
    re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),  # email
    re.compile(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b"),               # phone
]


def _build_patterns():
    """Build regex patterns for deny-listed terms."""
    patterns = []
    for term in DENY_TERMS:
        if " " in term or "/" in term:
            # Multi-word or command-like phrase → normalize whitespace
            flexible = re.sub(r"\s+", r"\\s+", re.escape(term))
            patterns.append(re.compile(flexible, re.IGNORECASE))
        else:
            # Single token → word boundary match
            patterns.append(re.compile(rf"\b{re.escape(term)}\b", re.IGNORECASE))
    return patterns


_DENY_PATTERNS = _build_patterns()


def contains_deny_terms(text: str) -> bool:
    """Return True if text contains any deny-listed terms (case-insensitive)."""
    return any(p.search(text) for p in _DENY_PATTERNS)


def enforce_size_limit(text: str) -> None:
    """Raise ValueError if text exceeds max char limit."""
    if len(text) > MAX_CHARS:
        raise ValueError(f"Input too long ({len(text)} chars). Limit is {MAX_CHARS:,}.")


def scrub_pii(text: str) -> str:
    """Scrub common PII (SSNs, credit cards, emails, phone numbers)."""
    scrubbed = text
    for pattern in PII_PATTERNS:
        scrubbed = pattern.sub("[REDACTED]", scrubbed)
    return scrubbed
