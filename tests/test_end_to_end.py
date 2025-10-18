from api_recap import create_recap_from_log
from backend.schema import Recap


def test_create_recap_pipeline_with_mocked_bedrock(monkeypatch):
    """Full recap pipeline should output a schema-valid Recap object."""
    monkeypatch.setattr(
        "api_recap.classify_with_bedrock",
        lambda prompt: [
            {
                "type": "code",
                "content": "print('ok')",
                "validation": {"status": "valid"},
            },
            {
                "type": "code",
                "content": "print('bad')",
                "validation": {"status": "invalid"},
            },
        ],
    )

    recap_payload = create_recap_from_log("dummy log", "pipeline-session")
    raw = recap_payload["raw_json"]

    recap = Recap.model_validate(raw)

    assert recap.final, "Expected final snippet"
    assert recap.summary, "Recap must have a summary"
    assert isinstance(recap.rejected_versions, list)
    assert recap.quality_flags
