# backend/tests/test_backend.py
from __future__ import annotations

from typing import Any, Dict, Generator, cast

import pytest
from flask.testing import FlaskClient
from backend.app import app


@pytest.fixture
def client() -> Generator[FlaskClient, None, None]:
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_recap_valid(client: FlaskClient) -> None:
    resp = client.post("/v1/recap", json={"chat_log": "hello world"})
    data: Any = resp.get_json()
    recap = cast(Dict[str, Any], data)
    assert resp.status_code == 200
    assert "human_readable" in recap
    assert "raw_json" in recap
    assert "summary" in recap["raw_json"]


def test_recap_size_limit(client: FlaskClient) -> None:
    big = "a" * 100_001
    resp = client.post("/v1/recap", json={"chat_log": big})
    assert resp.status_code == 413


def test_recap_deny_terms(client: FlaskClient) -> None:
    resp = client.post("/v1/recap", json={"chat_log": "this has a password"})
    assert resp.status_code == 400


def test_recap_code_blocks(client: FlaskClient) -> None:
    snippet = "```python\nprint('ok')\n```"
    resp = client.post("/v1/recap", json={"chat_log": snippet})
    data: Any = resp.get_json()
    recap = cast(Dict[str, Any], data)
    raw = recap["raw_json"]
    assert raw["final"] is not None
    assert raw["summary"] == "Dummy recap generated."
