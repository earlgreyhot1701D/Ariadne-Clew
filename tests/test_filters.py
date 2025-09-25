# backend/filters.py
import re

# Expanded deny-listed terms for MVP guardrails
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


def contains_deny_terms(text: str) -> bool:
    """
    Return True if text contains any deny-listed terms.
    Uses simple case-insensitive substring matching for robustness.
    """
    lower_text = text.lower()
    return any(term.lower() in lower_text for term in DENY_TERMS)


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
