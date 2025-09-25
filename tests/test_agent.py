import pytest
from backend.agent import RecapAgent, AgentConfig
from backend.schema import Recap


def test_agent_runs_full_pipeline(monkeypatch):
    """Agent should produce a valid Recap payload when Bedrock is mocked."""
    monkeypatch.setattr(
        "backend.agent.classify_with_bedrock",
        lambda prompt: [
            {"type": "code", "content": "print('ok')", "validation": {"status": "valid"}},
            {"type": "code", "content": "print('bad')", "validation": {"status": "invalid"}},
        ],
    )
    monkeypatch.setattr("backend.agent.store_recap", lambda *a, **kw: True)

    agent = RecapAgent(session_id="unit-test")
    payload = agent.run("dummy chat log")

    raw = payload["raw_json"]
    recap = Recap.model_validate(raw)

    assert recap.final
    assert recap.summary
    assert recap.rejected_versions


def test_agent_guardrail_strict(monkeypatch):
    """Strict mode should raise on unsafe input."""
    agent = RecapAgent(session_id="strict-test", config=AgentConfig(strict_guardrails=True))
    with pytest.raises(ValueError, match="unsafe terms"):
        agent.run("my password is 12345")


def test_agent_guardrail_relaxed(monkeypatch):
    """Relaxed mode should allow unsafe input with warning."""
    monkeypatch.setattr(
        "backend.agent.classify_with_bedrock",
        lambda prompt: [{"type": "code", "content": "print('ok')", "validation": {"status": "valid"}}],
    )
    monkeypatch.setattr("backend.agent.store_recap", lambda *a, **kw: True)

    agent = RecapAgent(session_id="relaxed-test", config=AgentConfig(strict_guardrails=False))
    payload = agent.run("contains password here")
    recap = Recap.model_validate(payload["raw_json"])
    assert recap.final


def test_agent_persistence_failure(monkeypatch):
    """If persistence enabled and store_recap fails, RuntimeError should bubble."""
    monkeypatch.setattr(
        "backend.agent.classify_with_bedrock",
        lambda prompt: [{"type": "code", "content": "print('ok')", "validation": {"status": "valid"}}],
    )
    monkeypatch.setattr("backend.agent.store_recap", lambda *a, **kw: False)

    agent = RecapAgent(session_id="fail-test", config=AgentConfig(persist_results=True))
    with pytest.raises(RuntimeError, match="Unable to persist recap"):
        agent.run("dummy log")


def test_agent_persistence_disabled(monkeypatch):
    """If persistence disabled, agent should return recap even if store_recap would fail."""
    monkeypatch.setattr(
        "backend.agent.classify_with_bedrock",
        lambda prompt: [{"type": "code", "content": "print('ok')", "validation": {"status": "valid"}}],
    )
    # store_recap is never called if persist_results=False
    monkeypatch.setattr("backend.agent.store_recap", lambda *a, **kw: (_ for _ in ()).throw(RuntimeError("should not be called")))

    agent = RecapAgent(session_id="no-persist-test", config=AgentConfig(persist_results=False))
    payload = agent.run("dummy log")
    recap = Recap.model_validate(payload["raw_json"])
    assert recap.final
