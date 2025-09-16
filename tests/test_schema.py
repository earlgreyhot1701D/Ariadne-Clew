
import pytest
from schema import validate_recap_output

VALID_RECAP = {
    "final": {
        "version": 2,
        "snippet_id": "snippet_2",
        "content": "print('Goodbye')",
        "diff_summary": "- print('Hello')\n+ print('Goodbye')"
    },
    "rejected": [
        {
            "version": 1,
            "snippet_id": "snippet_1",
            "content": "print('Hello')",
            "diff_summary": "No change"
        }
    ],
    "text_summary": "This is the final text."
}

def test_valid_recap_output():
    assert validate_recap_output(VALID_RECAP) is True

def test_missing_final_raises():
    invalid = VALID_RECAP.copy()
    del invalid["final"]
    with pytest.raises(ValueError, match="Missing recap field: final"):
        validate_recap_output(invalid)

def test_final_not_dict():
    invalid = VALID_RECAP.copy()
    invalid["final"] = "not a dict"
    with pytest.raises(ValueError, match="Final snippet must be a dict"):
        validate_recap_output(invalid)

def test_rejected_not_list():
    invalid = VALID_RECAP.copy()
    invalid["rejected"] = "not a list"
    with pytest.raises(ValueError, match="Rejected must be a list"):
        validate_recap_output(invalid)

def test_text_summary_not_string():
    invalid = VALID_RECAP.copy()
    invalid["text_summary"] = None
    with pytest.raises(ValueError, match="text_summary must be a string"):
        validate_recap_output(invalid)
