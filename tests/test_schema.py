import pytest
from backend.schema import Recap, RejectedVersion, validate_recap_output

VALID_RECAP = {
    "session_id": "test-session-123",
    "final": {
        "version": 2,
        "snippet_id": "snippet_2",
        "content": "print('Hello World')"
    },
    "rejected_versions": [
        {
            "code": "print('Hello')",
            "reason": "Incomplete implementation"
        }
    ],
    "summary": "This is the final summary.",
    "aha_moments": ["Realized the importance of proper output formatting"],
    "quality_flags": ["Well-structured session", "Clear progression"]
}


def test_valid_recap_output():
    assert validate_recap_output(VALID_RECAP) is True


def test_missing_recap_field():
    invalid = VALID_RECAP.copy()
    del invalid["aha_moments"]
    with pytest.raises(ValueError, match="Missing recap field: aha_moments"):
        validate_recap_output(invalid)


def test_final_not_dict():
    invalid = VALID_RECAP.copy()
    invalid["final"] = "not a dict"  # String instead of dict
    with pytest.raises(ValueError, match="Final snippet must be a dict"):
        validate_recap_output(invalid)


def test_rejected_versions_not_list():
    invalid = VALID_RECAP.copy()
    invalid["rejected_versions"] = "not a list"
    with pytest.raises(ValueError, match="Rejected must be a list"):
        validate_recap_output(invalid)


def test_summary_not_string():
    invalid = VALID_RECAP.copy()
    invalid["summary"] = None
    with pytest.raises(ValueError, match="summary must be a string"):
        validate_recap_output(invalid)
