# tests/test_filters.py
import pytest
from filters import enforce_size_limit, contains_deny_terms, scrub_pii, MAX_CHARS

def test_enforce_size_limit_too_large():
    big_input = "x" * (MAX_CHARS + 1)
    with pytest.raises(ValueError, match="Input too large"):
        enforce_size_limit(big_input)

def test_enforce_size_limit_ok():
    small_input = "ok"
    enforce_size_limit(small_input)  # should not raise

def test_contains_deny_terms_true():
    assert contains_deny_terms("This has a PASSWORD inside")

def test_contains_deny_terms_false():
    assert not contains_deny_terms("Just some safe text")

def test_scrub_pii_email():
    text = "Contact me at test@example.com"
    cleaned = scrub_pii(text)
    assert "test@example.com" not in cleaned
    assert "[redacted email]" in cleaned

def test_scrub_pii_phone():
    text = "Call 555-123-4567 for info"
    cleaned = scrub_pii(text)
    assert "555-123-4567" not in cleaned
    assert "[redacted phone]" in cleaned
