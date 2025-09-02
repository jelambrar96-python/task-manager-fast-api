import pytest
import importlib


def test_env_vars_loaded_and_not_none(monkeypatch):
    # Set environment variables for testing
    monkeypatch.setenv("POSTGRES_USER", "test_user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "test_pass")
    monkeypatch.setenv("POSTGRES_DB", "test_db")
    monkeypatch.setenv("POSTGRES_HOST", "localhost")
    monkeypatch.setenv("POSTGRES_PORT", "5432")
    monkeypatch.setenv("SECRET_KEY", "supersecret")

    # Reload config to pick up monkeypatched env vars
    config = importlib.reload(importlib.import_module("app.core.config"))

    env_vars = [
        config.POSTGRES_USER,
        config.POSTGRES_PASSWORD,
        config.POSTGRES_DB,
        config.POSTGRES_HOST,
        config.POSTGRES_PORT,
        config.SECRET_KEY,
        config.DATABASE_URL,
        config.HASH_ALGORITHM,
        config.ACCESS_TOKEN_EXPIRE_MINUTES
    ]

    for var in env_vars:
        assert var is not None
        assert var != ""


def test_database_url_format(monkeypatch):
    monkeypatch.setenv("POSTGRES_USER", "user")
    monkeypatch.setenv("POSTGRES_PASSWORD", "pass")
    monkeypatch.setenv("POSTGRES_DB", "db")
    monkeypatch.setenv("POSTGRES_HOST", "host")
    monkeypatch.setenv("POSTGRES_PORT", "1234")
    config = importlib.reload(importlib.import_module("app.core.config"))
    expected_url = "postgresql://user:pass@host:1234/db"
    assert config.DATABASE_URL == expected_url

