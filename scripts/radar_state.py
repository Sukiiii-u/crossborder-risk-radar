#!/usr/bin/env python3
import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from runtime_paths import LAST_RENDERED_FILE, LATEST_RUN_FILE, PUBLISHED_RUN_FILE, RUNS_DIR, RUNTIME_DIR  # noqa: E402
from published_snapshot import build_publish_payload  # noqa: E402

STATE_DIR = RUNTIME_DIR
STATE_VERSION = 2


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def ensure_state_dir() -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)


def load_latest_run() -> dict[str, Any] | None:
    if not LATEST_RUN_FILE.exists():
        return None
    try:
        payload = json.loads(LATEST_RUN_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return payload if isinstance(payload, dict) else None


def build_fingerprint(*, mode: str, source: str, output_format: str, brief: dict[str, Any], trigger: str) -> str:
    stable_payload = {
        "mode": mode,
        "source": source,
        "format": output_format,
        "trigger": trigger,
        "profile_preset": brief.get("profile_preset"),
        "seller_profile": brief.get("seller_profile"),
        "event_keys": [
            {
                "title": event.get("event_title"),
                "topic": event.get("primary_topic") or event.get("event_type"),
                "score": event.get("ranking_score"),
            }
            for event in brief.get("events", [])
            if isinstance(event, dict)
        ],
    }
    raw = json.dumps(stable_payload, ensure_ascii=False, sort_keys=True)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def build_delivery_key(*, mode: str, trigger: str, brief: dict[str, Any], fingerprint: str) -> str:
    profile_key = brief.get("profile_preset") or brief.get("profile_label") or "default"
    slug = "".join(char.lower() if char.isalnum() else "-" for char in str(profile_key)).strip("-") or "default"
    return f"{trigger}:{mode}:{slug}:{fingerprint[:12]}"


def find_previous_run_by_fingerprint(fingerprint: str) -> dict[str, Any] | None:
    ensure_state_dir()
    candidates = sorted(RUNS_DIR.glob("*.json"), key=lambda path: path.stat().st_mtime, reverse=True)
    for path in candidates:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        run_meta = payload.get("run") if isinstance(payload, dict) else None
        if isinstance(run_meta, dict) and run_meta.get("fingerprint") == fingerprint:
            return run_meta
    return None


def persist_run(
    *,
    mode: str,
    source: str,
    output_format: str,
    trigger: str,
    runner: str,
    brief: dict[str, Any],
    rendered: str,
    output_path: str | None = None,
    publish: bool = False,
) -> dict[str, Any]:
    ensure_state_dir()
    generated_at = utc_now_iso()
    run_id = f"radar-{generated_at.replace(':', '').replace('-', '').replace('T', '-').replace('Z', '')}-{uuid.uuid4().hex[:8]}"
    fingerprint = build_fingerprint(mode=mode, source=source, output_format=output_format, brief=brief, trigger=trigger)
    previous = load_latest_run() or {}
    previous_meta = previous.get("run") if isinstance(previous.get("run"), dict) else {}
    latest_previous_fp = previous_meta.get("fingerprint")
    matching_previous = find_previous_run_by_fingerprint(fingerprint)

    duplicate_of_last = bool((latest_previous_fp and latest_previous_fp == fingerprint) or matching_previous)
    duplicate_reference = matching_previous or previous_meta
    delivery_key = build_delivery_key(mode=mode, trigger=trigger, brief=brief, fingerprint=fingerprint)
    state_files = {
        "state_root": str(STATE_DIR),
        "runs_dir": str(RUNS_DIR),
        "latest_run": str(LATEST_RUN_FILE),
        "published_run": str(PUBLISHED_RUN_FILE),
        "latest_rendered": str(LAST_RENDERED_FILE),
    }

    run_meta = {
        "state_version": STATE_VERSION,
        "run_id": run_id,
        "generated_at": generated_at,
        "trigger": trigger,
        "runner": runner,
        "mode": mode,
        "source": source,
        "format": output_format,
        "output_path": output_path,
        "profile_preset": brief.get("profile_preset"),
        "profile_label": brief.get("profile_label"),
        "event_count": brief.get("event_count", 0),
        "fingerprint": fingerprint,
        "delivery_key": delivery_key,
        "delivery_status": "prepared",
        "delivery_targets": [],
        "is_duplicate_of_last": duplicate_of_last,
        "duplicate_of_run_id": duplicate_reference.get("run_id") if duplicate_of_last else None,
        "previous_run_id": duplicate_reference.get("run_id"),
        "state_files": state_files,
    }

    snapshot = {
        "run": run_meta,
        "brief": brief,
        "rendered": rendered,
    }

    run_file = RUNS_DIR / f"{run_id}.json"
    state_files["run_snapshot"] = str(run_file)
    run_meta["state_files"] = state_files

    run_file.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LATEST_RUN_FILE.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if publish:
        published_snapshot = {
            **snapshot,
            "publish_payload": build_publish_payload(snapshot),
        }
        PUBLISHED_RUN_FILE.write_text(json.dumps(published_snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    LAST_RENDERED_FILE.write_text(rendered + ("" if rendered.endswith("\n") else "\n"), encoding="utf-8")
    return run_meta
