import pytest
from pydantic import ValidationError
from backend.schema import Recap, EnrichedSnippet


def make_valid_recap():
    final = EnrichedSnippet(
        version=1,
        snippet_id="snippet_1",
        content="print('Hello World')",
        diff_summary="ok",
        validation={"status": "valid"},
    )
    return Recap(
        session_id="test-session-123",
        final=final,
        rejected_versions=[
            EnrichedSnippet(
                version=2,
                snippet_id="snippet_2",
                content="print('bad')",
                diff_summary="removed",
                validation={"status": "invalid", "reason": "test reason"},
            )
        ],
        summary="This is the final summary.",
        aha_moments=["aha"],
        quality_flags=["flag"],
    )


def test_valid_recap_passes():
    recap = make_valid_recap()
    dumped = recap.model_dump()
    assert dumped["summary"] == "This is the final summary."
    assert dumped["final"]["content"] == "print('Hello World')"


def test_missing_required_field():
    recap = make_valid_recap()
    data = recap.model_dump()
    del data["aha_moments"]
    with pytest.raises(ValidationError):
        Recap.model_validate(data)


def test_invalid_field_type():
    recap = make_valid_recap()
    data = recap.model_dump()
    data["summary"] = None  # should be string
    with pytest.raises(ValidationError):
        Recap.model_validate(data)
