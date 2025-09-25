"""
Validation tests for backend.filters guardrails.
Ensures deny list and PII scrubber behave as expected.
"""

import pytest
from backend import filters


def test_filters_block_deny_terms():
    """Every deny term in DENY_TERMS must be caught by contains_deny_terms."""
    for term in filters.DENY_TERMS:
        assert filters.contains_deny_terms(term), f"Failed to catch deny term: {term}"


def test_filters_block_known_dangerous_inputs():
    """Sanity check: obvious dangerous strings are blocked."""
    assert filters.contains_deny_terms("rm -rf /")
    assert filters.contains_deny_terms("BEGIN RSA PRIVATE KEY")
    assert filters.contains_deny_terms("password")


def test_scrub_pii_redacts():
    """Scrubber should redact emails, phone numbers, and SSNs."""
    sample = (
        "Email me at test@example.com or call 555-123-4567. "
        "My SSN is 123-45-6789 and card 4111111111111111."
    )
    scrubbed = filters.scrub_pii(sample)
    assert "[EMAIL_REDACTED]" in scrubbed
    assert "[PHONE_REDACTED]" in scrubbed
    assert "[SSN_REDACTED]" in scrubbed
    assert "[CC_REDACTED]" in scrubbed


def test_enforce_size_limit_passes_for_small_input():
    """enforce_size_limit should allow text under the max size."""
    filters.enforce_size_limit("hello world")  # should not raise


def test_enforce_size_limit_raises_for_large_input():
    """enforce_size_limit should raise ValueError for oversized text."""
    oversized = "a" * (filters.MAX_CHARS + 1)
    with pytest.raises(ValueError):
        filters.enforce_size_limit(oversized)
