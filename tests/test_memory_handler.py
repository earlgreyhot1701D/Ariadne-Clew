import pytest
import json
from backend import memory_handler as mh


def test_store_and_load_recap(tmp_path, monkeypatch):
    """Round-trip recap store/load works."""
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)

    key = "test_session"
    recap_data = {"summary": "unit test"}

    mh.store_recap(key, recap_data)
    path = mh._key_to_path(key)

    assert path.exists()
    loaded = mh.load_cached_recap(key)
    assert loaded == recap_data


def test_load_nonexistent_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)
    with pytest.raises(FileNotFoundError):
        mh.load_cached_recap("no-such-key")


def test_invalid_json_raises(tmp_path, monkeypatch):
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)
    path = mh._key_to_path("badjson")
    path.write_text("this is not json", encoding="utf-8")

    with pytest.raises(json.JSONDecodeError):
        mh.load_cached_recap("badjson")


def test_key_sanitization_and_unicode(tmp_path, monkeypatch):
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)
    key = "weird/key: name*?"
    recap = {"msg": "café ☕️"}

    mh.store_recap(key, recap)
    path = mh._key_to_path(key)

    assert path.exists()
    loaded = mh.load_cached_recap(key)
    assert loaded == recap
