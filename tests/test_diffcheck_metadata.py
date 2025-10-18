from backend.diffcheck import diff_code_blocks
from backend.schema import Recap


def test_rejected_versions_always_have_reason():
    """Rejected snippets must include validation reasons for transparency."""
    blocks = [
        {"type": "code", "content": "print('ok')", "validation": {"status": "valid"}},
        {
            "type": "code",
            "content": "print('bad')",
            "validation": {"status": "invalid"},
        },
        {
            "type": "code",
            "content": "print('extra')",
            "validation": {"status": "valid"},
        },
    ]

    recap_dict = diff_code_blocks(blocks)
    recap = Recap.model_validate(recap_dict)

    assert recap.rejected_versions, "Expected at least one rejected snippet"
    for rv in recap.rejected_versions:
        assert "reason" in rv.validation, f"Rejected snippet missing reason: {rv}"
