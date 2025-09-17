
import pytest
from memory_handler import store_memory, retrieve_memory, summarize_memory

@pytest.fixture
def sample_recap():
    return {
        "snippets": [
            {
                "snippet_id": "abc123",
                "version": 1,
                "content": "print('hello')",
                "diff_summary": "No change"
            },
            {
                "snippet_id": "def456",
                "version": 2,
                "content": "print('goodbye')",
                "diff_summary": "- print('hello')\n+ print('goodbye')"
            }
        ]
    }

def test_store_and_retrieve_memory(sample_recap):
    session_id = "test-session-1"
    ref = store_memory(session_id, sample_recap)
    assert ref == session_id
    retrieved = retrieve_memory(session_id)
    assert retrieved == sample_recap

def test_retrieve_nonexistent_memory():
    assert retrieve_memory("nonexistent-session") is None

def test_summarize_memory_with_data(sample_recap):
    summary = summarize_memory(sample_recap)
    assert "final snippet (v2)" in summary

def test_summarize_memory_empty():
    assert "No memory found" in summarize_memory({})
    assert "No memory found" in summarize_memory(None)
