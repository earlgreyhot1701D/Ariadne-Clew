import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_recap_valid(client):
    resp = client.post('/v1/recap', json={"chat_log": "hello world"})
    data = resp.get_json()
    assert resp.status_code == 200
    assert "human_readable" in data
    assert "raw_json" in data
    assert "summary" in data["raw_json"]

def test_recap_size_limit(client):
    big = "a" * 100_001
    resp = client.post('/v1/recap', json={"chat_log": big})
    assert resp.status_code == 413

def test_recap_deny_terms(client):
    resp = client.post('/v1/recap', json={"chat_log": "this has a password"})
    assert resp.status_code == 400

def test_recap_code_blocks(client):
    snippet = "```python\nprint('ok')\n```"
    resp = client.post('/v1/recap', json={"chat_log": snippet})
    data = resp.get_json()
    raw = data["raw_json"]
    assert raw["final"] is not None
    assert raw["summary"] == "Dummy recap generated."
