# tests/test_api_recap.py

import pytest
from api_recap import app

@pytest.fixture
def client():
    app.testing = True
    with app.test_client() as client:
        yield client

def test_recap_with_valid_input(client):
    response = client.post('/v1/recap', json={
        "chat_log": "Here's code:\n```print('hello')```"
    })
    assert response.status_code == 200
    assert "final" in response.get_json()

def test_recap_with_missing_input(client):
    response = client.post('/v1/recap', json={})
    assert response.status_code == 400
    assert "error" in response.get_json()

def test_recap_with_wrong_content_type(client):
    response = client.post('/v1/recap', data="not json")
    assert response.status_code == 415
