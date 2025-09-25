# tests/test_api_recap.py

import pytest
from api_recap import app
from unittest.mock import patch


@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client


@patch("api_recap.store_recap")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "```print('hello')```", "type": "code"}],
)
def test_valid_input(mock_bedrock, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "```print('hello')```"})
    assert response.status_code == 200
    data = response.get_json()
    assert "final" in data
    assert "summary" in data


@patch("api_recap.store_recap")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "code", "type": "code"}],
)
def test_missing_input(mock_bedrock, mock_store, client):
    response = client.post("/v1/recap", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("api_recap.store_recap")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "code", "type": "code"}],
)
def test_wrong_content_type(mock_bedrock, mock_store, client):
    response = client.post("/v1/recap", data="not json")
    assert response.status_code == 415


@patch("api_recap.store_recap")
@patch("api_recap.enforce_size_limit", side_effect=ValueError("Too large"))
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "code", "type": "code"}],
)
def test_oversized_input(mock_bedrock, mock_enforce, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "x" * 200000})
    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("api_recap.store_recap")
@patch("api_recap.contains_deny_terms", return_value=True)
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "code", "type": "code"}],
)
def test_input_with_deny_terms(mock_bedrock, mock_deny, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "contains password"})
    assert response.status_code == 400
    assert "error" in response.get_json()


@patch("api_recap.store_recap")
@patch("api_recap.scrub_pii", return_value="Cleaned chat")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "code", "type": "code"}],
)
def test_pii_stripping(mock_bedrock, mock_scrub, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "test@example.com"})
    assert response.status_code == 200
    assert "test@example.com" not in str(response.get_json())


@patch("api_recap.store_recap")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "```print('schema')```", "type": "code"}],
)
def test_schema_compliance(mock_bedrock, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "```print('schema')```"})
    data = response.get_json()
    allowed = {
        "session_id",
        "final",
        "rejected_versions",
        "aha_moments",
        "summary",
        "quality_flags",
    }
    assert set(data.keys()).issubset(allowed)


@patch("api_recap.store_recap")
@patch(
    "api_recap.classify_with_bedrock",
    return_value=[{"content": "```print('hi')```", "type": "code"}],
)
def test_human_summary_present(mock_bedrock, mock_store, client):
    response = client.post("/v1/recap", json={"chat_log": "```print('hi')```"})
    assert "What You Built" in response.get_json().get("summary", "")


@patch("api_recap.Path.read_text", side_effect=FileNotFoundError())
def test_missing_prompt_file_throws(mock_read):
    from api_recap import load_prompts

    with pytest.raises(RuntimeError):
        load_prompts()


@patch("api_recap.bedrock.invoke_model", side_effect=Exception("AWS error"))
def test_bedrock_failure_returns_500(mock_invoke, client):
    response = client.post("/v1/recap", json={"chat_log": "```print('oops')```"})
    assert response.status_code == 500
    assert "error" in response.get_json()
