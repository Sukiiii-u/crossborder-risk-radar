#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
import uuid
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from feed_source_config import load_changedetection_source  # noqa: E402

WATCHLIST_FILE = SCRIPT_DIR.parent / "monitoring" / "platform_official_watchlist.json"
CHANGEDETECTION_DATA_DIR = SCRIPT_DIR.parent / "monitoring" / "changedetection-data"


def load_watchlist() -> list[dict]:
    return json.loads(WATCHLIST_FILE.read_text(encoding="utf-8"))


def existing_watches() -> dict[str, Path]:
    result: dict[str, Path] = {}
    for path in CHANGEDETECTION_DATA_DIR.glob("*/watch.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        url = str(payload.get("url") or "").strip()
        if url:
            result[url] = path
    return result


def build_watch(item: dict) -> dict:
    watch_uuid = str(uuid.uuid4())
    source = load_changedetection_source()
    return {
        "uuid": watch_uuid,
        "title": item.get("title"),
        "url": item["url"],
        "tag": "",
        "tags": [item["id"], item.get("priority", "P1"), "crossborder-risk-radar"],
        "method": "GET",
        "fetch_backend": "system",
        "processor": "text_json_diff",
        "headers": {},
        "body": None,
        "proxy": None,
        "paused": False,
        "include_filters": item.get("keywords", []),
        "ignore_text": [],
        "extract_text": [],
        "subtractive_selectors": [],
        "notification_urls": [source.get("source")] if source.get("mode") == "url" else [],
        "notification_title": item.get("title"),
        "notification_body": None,
        "notification_format": "System default",
        "notification_muted": False,
        "notification_screenshot": False,
        "filter_text_added": True,
        "filter_text_removed": True,
        "filter_text_replaced": True,
        "filter_failure_notification_send": True,
        "fetch_time": 0,
        "check_count": 0,
        "last_checked": 0,
        "last_viewed": 0,
        "last_error": False,
        "last_notification_error": None,
        "browser_steps": [],
        "browser_steps_last_error_step": None,
        "check_unique_lines": False,
        "conditions": [],
        "conditions_match_logic": "ALL",
        "consecutive_filter_failures": 0,
        "content-type": None,
        "date_created": 0,
        "follow_price_changes": True,
        "has_ldjson_price_data": None,
        "history_snapshot_max_length": None,
        "ignore_status_codes": None,
        "in_stock_only": True,
        "page_title": None,
        "previous_md5": False,
        "price_change_threshold_percent": None,
        "remote_server_reply": None,
        "remove_duplicate_lines": False,
        "sort_text_alphabetically": False,
        "strip_ignored_lines": None,
        "text_should_not_be_present": [],
        "time_between_check": {"weeks": None, "days": None, "hours": None, "minutes": None, "seconds": None},
        "time_between_check_use_default": True,
        "time_schedule_limit": None,
        "track_ldjson_price_data": False,
        "trigger_text": [],
        "trim_text_whitespace": False,
        "use_page_title_in_list": False,
        "webdriver_delay": None,
        "webdriver_js_execute_code": None,
    }


def main() -> int:
    CHANGEDETECTION_DATA_DIR.mkdir(parents=True, exist_ok=True)
    existing = existing_watches()
    created = []
    already_present = []
    for item in load_watchlist():
        url = item["url"]
        if url in existing:
            already_present.append(item["id"])
            continue
        watch = build_watch(item)
        target_dir = CHANGEDETECTION_DATA_DIR / watch["uuid"]
        target_dir.mkdir(parents=True, exist_ok=True)
        (target_dir / "watch.json").write_text(json.dumps(watch, ensure_ascii=False, indent=2), encoding="utf-8")
        created.append({"id": item["id"], "url": url, "dir": str(target_dir)})

    print(
        json.dumps(
            {
                "created_count": len(created),
                "created": created,
                "already_present_count": len(already_present),
                "already_present": already_present,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
