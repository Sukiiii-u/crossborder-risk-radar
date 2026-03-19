#!/usr/bin/env python3
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
RUNTIME_DIR = Path(os.environ.get("CROSSBORDER_RADAR_RUNTIME_DIR", str(SKILL_ROOT / "runtime"))).expanduser()
RUNTIME_DATA_DIR = RUNTIME_DIR / "data"
CHANGEDETECTION_FEED_FILE = SKILL_ROOT / "monitoring" / "changedetection_feed.xml"
RUNS_DIR = RUNTIME_DIR / "runs"
LATEST_RUN_FILE = RUNTIME_DIR / "latest_run.json"
PUBLISHED_RUN_FILE = RUNTIME_DIR / "published_run.json"
LAST_RENDERED_FILE = RUNTIME_DIR / "latest_rendered.txt"

REAL_EVENTS_FILE = RUNTIME_DATA_DIR / "real_events.json"
REAL_EVENTS_AUDIT_FILE = RUNTIME_DATA_DIR / "real_events_audit.json"
INGEST_STATUS_FILE = RUNTIME_DATA_DIR / "ingest_status.json"
SOURCE_STATUS_FILE = RUNTIME_DATA_DIR / "source_status.json"
POLICY_WATCH_FILE = RUNTIME_DATA_DIR / "policy_watch.json"


def ensure_runtime_data_dir() -> None:
    RUNTIME_DATA_DIR.mkdir(parents=True, exist_ok=True)
