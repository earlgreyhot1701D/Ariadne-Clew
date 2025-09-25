# tests/test_validation_suite.py
"""
Unified validation suite for Ariadne Clew MVP.
Covers schema contract, guardrails, persistence, metadata propagation, and agent flow.
"""

import pytest
from backend.schema import Recap
from backend import filters, memory_handler, diffcheck, code_handler
from backend.agent import RecapAgent


def test_contract_full_recap_validates():
    """Ensure diff_code_blocks output validates against Recap schema."""
    blocks = [
        {"type": "text", "content": "final version"},
        {"type": "code", "content": "print('hello world')"},
        {"type": "code", "content": "print('oops'"},
    ]
    recap = diffcheck.diff_code_blocks(blocks)
    # Raises ValidationError if schema drift exists
    model = Recap.model_validate(recap)
    dump = model.model_dump()
    assert "summary" in dump
    assert isinstance(dump["rejected_versions"], list)


def test_filters_block_dangerous_inputs():
    """Deny terms and PII scrubber must catch roadmap-required patterns."""
    bad_inputs = [
        "rm -rf /",
        "BEGIN RSA PRIVATE KEY",
        "contact me at user@example.com",
        "call 555-123-4567",
    ]
    for text in bad_inputs:
        assert filters.contains_deny_terms(text) or filters.contains_pii(text)


def test_memory_handler_failure(monkeypatch):
    """store_recap should raise on failure, never return None/False silently."""
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(IOError("disk full")),
    )
    with pytest.raises(IOError):
        memory_handler.store_recap("session123", {"ok": True})


def test_metadata_propagation():
    """Rejected versions should carry validation reasons from code_handler.validate_snippet."""
    valid = "print('ok')"
    invalid = "def bad(:"
    results = [
        {"type": "code", "content": valid, "validation": code_handler.validate_snippet(valid)},
        {"type": "code", "content": invalid, "validation": code_handler.validate_snippet(invalid)},
    ]
    recap = diffcheck.diff_code_blocks(results)
    rejected = recap.get("rejected_versions", [])
    assert any("reason" in r.get("validation", {}) for r in rejected)


def test_agent_end_to_end():
    """RecapAgent.run should return a schema-valid Recap with validation metadata."""
    chat_log = "```print('ok')```"
    agent = RecapAgent(strict=True, persist=False)
    recap = agent.run(chat_log, session_id="sess1")
    model = Recap.model_validate(recap)
    assert model.final or model.rejected_versions
