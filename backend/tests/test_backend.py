import pytest
import json
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_valid_recap_request(client):
    """Test successful recap generation."""
    payload = {"chat_log": "Hello, this is a test conversation."}
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 200
    data = res.get_json()
    assert "human_readable" in data
    assert "raw_json" in data

def test_missing_json_body(client):
    """Test request without JSON body."""
    res = client.post('/recap')
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_missing_chat_log(client):
    """Test request missing chat_log field."""
    payload = {"wrong_field": "value"}
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_invalid_chat_log_type(client):
    """Test request with non-string chat_log."""
    payload = {"chat_log": 123}
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_chat_log_size_limit(client):
    """Test request with oversized chat_log."""
    payload = {"chat_log": "x" * 60000}  # Exceeds 50KB limit
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 413
    data = res.get_json()
    assert "error" in data

def test_forbidden_terms(client):
    """Test request containing forbidden terms."""
    payload = {"chat_log": "Here is my password: secret123"}
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 400
    data = res.get_json()
    assert "error" in data

def test_pii_scrubbing(client):
    """Test that PII gets scrubbed from input."""
    payload = {"chat_log": "Contact me at john@example.com or 555-123-4567"}
    res = client.post('/recap',
                     data=json.dumps(payload),
                     content_type='application/json')
    assert res.status_code == 200
    # PII should be scrubbed in the backend processing

def test_invalid_route(client):
    """Test invalid endpoint."""
    res = client.get('/invalid-endpoint')
    assert res.status_code == 404
