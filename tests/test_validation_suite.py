# tests/test_validation_suite.py
"""
Unified validation suite for Ariadne Clew MVP.
Covers schema contract, guardrails, persistence, metadata propagation, and agent flow.
"""

from backend.schema import Recap
from backend import filters, memory_handler, diffcheck
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
    """Deny terms must catch roadmap-required patterns."""
    bad_inputs = [
        "rm -rf /",
        "BEGIN RSA PRIVATE KEY",
    ]
    for text in bad_inputs:
        assert filters.contains_deny_terms(text)


def test_memory_handler_failure(monkeypatch):
    """store_recap should signal failure (raise or return False/None)."""
    monkeypatch.setattr(
        "builtins.open",
        lambda *a, **k: (_ for _ in ()).throw(IOError("disk full")),
    )
    try:
        result = memory_handler.store_recap("session123", {"ok": True})
    except IOError:
        # acceptable: raising an error
        return
    # also acceptable: returning False/None
    assert result in (False, None)


def test_metadata_propagation_shape():
    """diff_code_blocks output must include rejected_versions list, even with invalid snippets."""
    blocks = [
        {"type": "code", "content": "print('ok')"},
        {"type": "code", "content": "def bad(:"},
    ]
    recap = diffcheck.diff_code_blocks(blocks)
    model = Recap.model_validate(recap)
    assert isinstance(model.rejected_versions, list)


def test_agent_end_to_end():
    """RecapAgent.run should return a schema-valid Recap."""
    chat_log = "```print('ok')```"
    agent = RecapAgent()  # use actual signature
    recap = agent.run(chat_log, session_id="sess1")
    model = Recap.model_validate(recap)
    assert model.final or model.rejected_versions
