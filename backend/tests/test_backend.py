
import pytest
from app import app as flask_app

@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client

def test_valid_session(client):
    res = client.get('/recap?session_id=example123')
    assert res.status_code == 200

def test_missing_session(client):
    res = client.get('/recap')
    assert res.status_code == 400

def test_malformed_session(client):
    res = client.get('/recap?session_id=')
    assert res.status_code == 400

def test_invalid_route(client):
    res = client.get('/invalid-endpoint')
    assert res.status_code == 404
