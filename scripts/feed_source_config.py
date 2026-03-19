#!/usr/bin/env python3
import json
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
CHANGEDETECTION_SOURCE_FILE = SKILL_ROOT / "configs" / "changedetection_source.json"


def load_changedetection_source() -> dict:
    if not CHANGEDETECTION_SOURCE_FILE.exists():
        raise FileNotFoundError("missing configs/changedetection_source.json")
    payload = json.loads(CHANGEDETECTION_SOURCE_FILE.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("changedetection_source.json must be a JSON object")

    mode = str(payload.get("mode") or "").strip().lower()
    source = str(payload.get("source") or "").strip()
    if mode not in {"url", "file"}:
        raise ValueError("changedetection_source.json mode must be 'url' or 'file'")
    if not source:
        raise ValueError("changedetection_source.json source must not be empty")
    return {"mode": mode, "source": source}
