"""Unified configuration loading with YAML merge and environment overrides."""

from __future__ import annotations

import os
from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

DEFAULT_CONFIG = Path("config/settings.yaml")
DEV_CONFIG = Path("config/settings.dev.yaml")
PROD_CONFIG = Path("config/settings.prod.yaml")


def _deep_merge(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = _deep_merge(result[key], value)
        else:
            result[key] = value
    return result


def resolve_config_path(path: str | Path | None = None) -> Path:
    if path is not None:
        return Path(path)
    if env_path := os.environ.get("HEAT_MAP_CONFIG_PATH"):
        return Path(env_path)
    env = os.environ.get("HEAT_MAP_ENV", "").lower()
    if env in ("dev", "development"):
        return DEV_CONFIG
    if env in ("prod", "production"):
        return PROD_CONFIG
    return DEFAULT_CONFIG


def load_config(path: str | Path | None = None) -> dict[str, Any]:
    """Load settings.yaml, merge env-specific overrides, then apply env vars."""
    config_path = resolve_config_path(path)
    cfg: dict[str, Any] = {}
    if DEFAULT_CONFIG.exists():
        with open(DEFAULT_CONFIG, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}

    if config_path != DEFAULT_CONFIG and config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            override = yaml.safe_load(f) or {}
        cfg = _deep_merge(cfg, override)
    elif config_path != DEFAULT_CONFIG and not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    _apply_env_overrides(cfg)
    return cfg


def _apply_env_overrides(cfg: dict[str, Any]) -> None:
    if db_url := os.environ.get("DB_URL"):
        cfg.setdefault("storage", {})["db_url"] = db_url
    if secret := os.environ.get("AUTH_SECRET_KEY"):
        cfg.setdefault("auth", {})["secret_key"] = secret
    if api_url := os.environ.get("API_BASE_URL"):
        cfg.setdefault("dashboard", {})["api_base_url"] = api_url
    if camera_source := os.environ.get("HEAT_MAP_CAMERA_SOURCE"):
        cameras = cfg.get("cameras", [])
        if cameras:
            cameras[0]["source"] = camera_source
    if device := os.environ.get("DETECTION_DEVICE"):
        cfg.setdefault("detection", {})["device"] = device
