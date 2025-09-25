# tests/test_api_recap.py

import pytest
from unittest.mock import patch
from api_recap import app


@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.testing = True
    with app.test_client() as client:
        yield client


@pytest.fixture(autouse=True)
def mock_prompts(monkeypatch, request):
    """Mock load_prompts to avoid file system dependencies during testing."""
    # Skip mocking for the specific test that wants to test file errors
    if request.node.name == "test_missing_prompt_file_throws":
        return
    monkeypatch.setattr("api_recap.load_prompts", lambda: "Mock system prompt\n\nMock classifier prompt")


@pytest.fixture
def mock_bedrock_success():
    """Mock successful Bedrock classification."""
    return patch(
        "api_recap.classify_with_bedrock",
        return_value=[{"content": "```print('hello')```", "type": "code"}]
    )


@pytest.fixture
def mock_bedrock_simple():
    """Mock simple Bedrock classification."""
    return patch(
        "api_recap.classify_with_bedrock",
        return_value=[{"content": "code", "type": "code"}]
    )


@pytest.fixture
def mock_store():
    """Mock the store_recap function."""
    return patch("api_recap.store_recap")


def test_valid_input(client, mock_store, mock_bedrock_success):
    """Test successful processing of valid input."""
    with mock_store, mock_bedrock_success, \
         patch("api_recap.diff_code_blocks", return_value={
             "final": "print('hello')",
             "rejected_versions": [],
             "summary": "What You Built: Test summary",
             "aha_moments": [],
             "quality_flags": []
         }):
        response = client.post("/v1/recap", json={"chat_log": "```print('hello')```"})
        assert response.status_code == 200
        data = response.get_json()
        # The API returns {"human_readable": "...", "raw_json": {...}}
        assert "human_readable" in data
        assert "raw_json" in data
        assert "final" in data["raw_json"]
        assert "summary" in data["raw_json"]


def test_missing_input(client, mock_store, mock_bedrock_simple):
    """Test handling of missing chat_log field."""
    with mock_store, mock_bedrock_simple:
        response = client.post("/v1/recap", json={})
        assert response.status_code == 400
        assert "error" in response.get_json()


def test_wrong_content_type(client, mock_store, mock_bedrock_simple):
    """Test rejection of non-JSON content type."""
    with mock_store, mock_bedrock_simple:
        response = client.post("/v1/recap", data="not json")
        assert response.status_code == 415


def test_oversized_input(client, mock_store, mock_bedrock_simple):
    """Test handling of oversized input."""
    with mock_store, mock_bedrock_simple, \
         patch("api_recap.enforce_size_limit", side_effect=ValueError("Too large")):
        response = client.post("/v1/recap", json={"chat_log": "x" * 200000})
        assert response.status_code == 400
        assert "error" in response.get_json()


def test_input_with_deny_terms(client, mock_store, mock_bedrock_simple):
    """Test handling of input with deny terms."""
    with mock_store, mock_bedrock_simple, \
         patch("api_recap.contains_deny_terms", return_value=True):
        response = client.post("/v1/recap", json={"chat_log": "contains password"})
        assert response.status_code == 400
        assert "error" in response.get_json()


def test_pii_stripping(client, mock_store, mock_bedrock_simple):
    """Test PII scrubbing functionality."""
    with mock_store, mock_bedrock_simple, \
         patch("api_recap.scrub_pii", return_value="Cleaned chat") as mock_scrub, \
         patch("api_recap.diff_code_blocks", return_value={
             "final": "print('clean')",
             "rejected_versions": [],
             "summary": "What You Built: Clean summary",
             "aha_moments": [],
             "quality_flags": []
         }):
        response = client.post("/v1/recap", json={"chat_log": "test@example.com"})
        assert response.status_code == 200
        assert "test@example.com" not in str(response.get_json())
        mock_scrub.assert_called_once()


def test_schema_compliance(client, mock_store):
    """Test that response conforms to expected schema."""
    with mock_store, \
         patch("api_recap.classify_with_bedrock",
               return_value=[{"content": "```print('schema')```", "type": "code"}]), \
         patch("api_recap.diff_code_blocks", return_value={
             "final": "print('schema')",
             "rejected_versions": [],
             "summary": "What You Built: Schema test",
             "aha_moments": [],
             "quality_flags": []
         }):
        response = client.post("/v1/recap", json={"chat_log": "```print('schema')```"})
        data = response.get_json()
        # Check top-level API response format
        assert "human_readable" in data
        assert "raw_json" in data

        # Check the raw_json contains expected fields
        raw_data = data["raw_json"]
        allowed_keys = {
            "session_id", "final", "rejected_versions",
            "aha_moments", "summary", "quality_flags"
        }
        assert set(raw_data.keys()).issubset(allowed_keys)


def test_human_summary_present(client, mock_store):
    """Test that human-readable summary is present."""
    with mock_store, \
         patch("api_recap.classify_with_bedrock",
               return_value=[{"content": "```print('hi')```", "type": "code"}]), \
         patch("api_recap.diff_code_blocks", return_value={
             "final": "print('hi')",
             "rejected_versions": [],
             "summary": "What You Built: Test with greeting",
             "aha_moments": [],
             "quality_flags": []
         }):
        response = client.post("/v1/recap", json={"chat_log": "```print('hi')```"})
        data = response.get_json()
        # Check both the human_readable field and the raw summary
        human_readable = data.get("human_readable", "")
        raw_summary = data.get("raw_json", {}).get("summary", "")
        assert "What You Built" in human_readable or "What You Built" in raw_summary


def test_missing_prompt_file_throws():
    """Test that missing prompt files raise RuntimeError."""
    with patch("api_recap.Path.read_text", side_effect=FileNotFoundError("Mock file not found")):
        from api_recap import load_prompts
        with pytest.raises(RuntimeError):
            load_prompts()


def test_bedrock_failure_returns_500(client):
    """Test that Bedrock failures return 500 status."""
    with patch("api_recap.bedrock.invoke_model", side_effect=Exception("AWS error")):
        response = client.post("/v1/recap", json={"chat_log": "```print('oops')```"})
        assert response.status_code == 500
        assert "error" in response.get_json()
