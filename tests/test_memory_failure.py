import pytest
from api_recap import create_recap_from_log


def test_persistence_failure_raises(monkeypatch):
    """If store_recap fails, RuntimeError should bubble up to caller."""
    monkeypatch.setattr(
        "api_recap.classify_with_bedrock",
        lambda prompt: [
            {
                "type": "code",
                "content": "print('ok')",
                "validation": {"status": "valid"},
            }
        ],
    )
    monkeypatch.setattr("api_recap.store_recap", lambda *a, **kw: False)

    with pytest.raises(RuntimeError, match="Unable to persist recap"):
        create_recap_from_log("dummy log", "fail-session")
