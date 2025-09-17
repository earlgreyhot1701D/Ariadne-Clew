
import pytest
from code_handler import extract_code_blocks, version_snippets, validate_snippet

# --- Fixtures ---

@pytest.fixture
def mock_chat():
    return """
    user: write a function
    assistant: Sure
    ```python
    def greet():
        print("Hello")
    ```
    user: make it more polite
    ```python
    def greet():
        print("Good day!")
    ```
    """

# --- Tests ---

def test_extract_code_blocks(mock_chat):
    blocks = extract_code_blocks(mock_chat)
    assert len(blocks) == 2
    assert "def greet()" in blocks[0]
    assert "Good day" in blocks[1]

def test_extract_raises_on_unmatched_fence():
    with pytest.raises(ValueError, match="Unmatched code fence"):
        extract_code_blocks("```incomplete")

def test_version_snippets_structure():
    snippets = ["print(1)", "print(2)"]
    result = version_snippets(snippets)
    assert len(result) == 2
    assert "snippet_id" in result[0]
    assert result[0]["version"] == 1
    assert result[1]["version"] == 2
    assert "diff_summary" in result[1]

def test_validate_snippet_valid():
    result = validate_snippet("print('Hello')")
    assert result["status"] == "valid"
    assert result["error"] == ""

def test_validate_snippet_partial():
    result = validate_snippet("x =")
    assert result["status"] == "partial"
    assert "incomplete" in result["error"]
