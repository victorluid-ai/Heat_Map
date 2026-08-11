import os
from pathlib import Path

import pytest

from src.utils.config import _deep_merge, load_config, resolve_config_path


def test_deep_merge_nested():
    base = {"storage": {"db_url": "sqlite:///a.db", "batch_max": 500}, "api": {"port": 8000}}
    override = {"storage": {"db_url": "sqlite:///b.db"}}
    merged = _deep_merge(base, override)
    assert merged["storage"]["db_url"] == "sqlite:///b.db"
    assert merged["storage"]["batch_max"] == 500
    assert merged["api"]["port"] == 8000


def test_load_config_db_url_env_override(monkeypatch):
    monkeypatch.setenv("DB_URL", "sqlite:///data/test_override.db")
    cfg = load_config()
    assert cfg["storage"]["db_url"] == "sqlite:///data/test_override.db"


def test_resolve_config_path_env_dev(monkeypatch):
    monkeypatch.delenv("HEAT_MAP_CONFIG_PATH", raising=False)
    monkeypatch.setenv("HEAT_MAP_ENV", "dev")
    assert resolve_config_path() == Path("config/settings.dev.yaml")
