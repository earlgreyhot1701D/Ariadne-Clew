import pytest
from schema import validate_claude_result


def test_valid_structure_passes():
    good = {
        "session_id": "abc",
        "timestamp": "now",
        "aha_moments": [],
        "mvp_changes": [],
        "scope_creep": [],
        "readme_notes": [],
        "post_mvp_ideas": [],
        "summary": "All good",
        "quality_flags": [],
    }
    assert validate_claude_result(good)


def test_missing_field_fails():
    bad = {
        "session_id": "abc",
        "timestamp": "now",
        "aha_moments": [],
        # mvp_changes missing
        "scope_creep": [],
        "readme_notes": [],
        "post_mvp_ideas": [],
        "summary": "All good",
        "quality_flags": [],
    }
    with pytest.raises(ValueError):
        validate_claude_result(bad)
