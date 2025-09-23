import pytest
from diffcheck import deduplicate_code_snippets, add_versions, diff_code_blocks

# --- Fixtures ---


@pytest.fixture
def raw_blocks():
    return [
        {"type": "code", "content": "print('Hello World')"},
        {"type": "text", "content": "This is just a test"},
        {"type": "code", "content": "print('Hello World')"},  # Duplicate
        {"type": "code", "content": "print('Goodbye World')"},
        {"type": "text", "content": "Final note"},
    ]


# --- Tests ---


def test_deduplicate_code_snippets():
    snippets = [
        {"type": "code", "content": "a = 1"},
        {"type": "code", "content": "a = 1"},
        {"type": "code", "content": "b = 2"},
    ]
    result = deduplicate_code_snippets(snippets)
    assert len(result) == 2
    assert result[0]["content"] == "a = 1"
    assert result[1]["content"] == "b = 2"


def test_add_versions():
    snippets = [
        {"type": "code", "content": "x = 1"},
        {"type": "code", "content": "x = 2"},
    ]
    enriched = add_versions(snippets)
    assert enriched[0]["version"] == 1
    assert enriched[1]["version"] == 2
    assert "snippet_1" in enriched[0]["snippet_id"]
    assert "diff_summary" in enriched[1]


def test_diff_code_blocks_full(raw_blocks):
    recap = diff_code_blocks(raw_blocks)
    assert "final" in recap
    assert "rejected" in recap
    assert "text_summary" in recap
    assert recap["final"]["version"] == 2
    assert len(recap["rejected"]) == 1
    assert recap["text_summary"] == "Final note"


def test_diff_code_blocks_empty():
    recap = diff_code_blocks([])
    assert recap["final"]["version"] == 0
    assert recap["rejected"] == []
    assert recap["text_summary"] == ""
