import pytest
from backend.diffcheck import diff_code_blocks
from backend.schema import Recap


def test_diff_code_blocks_propagates_metadata():
    blocks = [
        {"type": "code", "content": "print('ok')", "validation": {"status": "valid"}},
        {"type": "code", "content": "print('bad')", "validation": {"status": "invalid"}},
    ]

    recap_dict = diff_code_blocks(blocks)
    recap = Recap.model_validate(recap_dict)

    assert recap.final is not None
    assert recap.final.content == "print('ok')"

    # At least one rejected version
    assert recap.rejected_versions
    for rv in recap.rejected_versions:
        assert "reason" in rv.validation
        assert rv.validation["status"] in ("invalid", "unknown")
