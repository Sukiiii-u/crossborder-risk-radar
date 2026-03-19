#!/usr/bin/env python3
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
NETWORK_CONFIG_FILE = SKILL_ROOT / "configs" / "fetch_network.json"

ALLOWED_KEYS = {"http_proxy", "https_proxy", "no_proxy"}


def load_network_config() -> dict:
    if not NETWORK_CONFIG_FILE.exists():
        return {}
    payload = json.loads(NETWORK_CONFIG_FILE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("fetch_network.json must be a JSON object")
    unknown = sorted(set(payload) - ALLOWED_KEYS)
    if unknown:
        raise ValueError(f"unsupported fetch_network.json keys: {', '.join(unknown)}")
    config: dict[str, str] = {}
    for key in ALLOWED_KEYS:
        value = payload.get(key)
        if value is None:
            continue
        normalized = str(value).strip()
        if normalized:
            config[key] = normalized
    return config


def proxy_mapping(config: dict | None = None) -> dict:
    config = config or load_network_config()
    proxies: dict[str, str] = {}
    if config.get("http_proxy"):
        proxies["http"] = config["http_proxy"]
    if config.get("https_proxy"):
        proxies["https"] = config["https_proxy"]
    return proxies
