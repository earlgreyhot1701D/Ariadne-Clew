import pytest
from backend import memory_handler as mh


def test_store_and_load_recap(tmp_path, monkeypatch):
    """Store a recap and read it back; assert file exists and content matches."""
    key = "test_session"
    recap_data = {"summary": "unit test"}

    # Override cache directory for test isolation
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)

    mh.store_recap(key, recap_data)
    path = mh._key_to_path(key)

    # File should exist and contain JSON
    assert path.exists() and path.is_file()

    loaded = mh.load_cached_recap(key)
    assert isinstance(loaded, dict)
    assert loaded == recap_data


def test_load_nonexistent_returns_none(tmp_path, monkeypatch):
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)
    assert mh.load_cached_recap("no-such-key") is None


def test_invalid_json_returns_none(tmp_path, monkeypatch):
    """If file exists but contains invalid JSON, loader should return None."""
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)
    path = mh._key_to_path("badjson")
    path.write_text("this is not json", encoding="utf-8")

    assert mh.load_cached_recap("badjson") is None


def test_key_sanitization_and_unicode(tmp_path, monkeypatch):
    """Keys with unsafe chars should be sanitized; Unicode must persist through roundtrip."""
    monkeypatch.setattr(mh, "_CACHE_DIR", tmp_path)

    key = "weird/key: name*?"
    recap = {"msg": "café ☕️"}

    mh.store_recap(key, recap)
    path = mh._key_to_path(key)

    # Ensure sanitized filename produced
    assert path.name == "weird_key__name__.json"
    assert path.exists()

    loaded = mh.load_cached_recap(key)
    assert loaded == recap

