#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "ui" / "refresh_radar_data.py"


def run_refresh(env: dict[str, str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT)], capture_output=True, text=True, check=False, env=env)


def main() -> int:
    errors = []
    with tempfile.TemporaryDirectory() as runtime_tmp, tempfile.TemporaryDirectory() as ui_tmp:
        runtime_root = Path(runtime_tmp)
        published_run = runtime_root / "published_run.json"
        target = Path(ui_tmp) / "radar-data.js"
        env = dict(
            os.environ,
            CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root),
            CROSSBORDER_RADAR_UI_DATA_FILE=str(target),
        )
        target.write_text("window.RADAR_UI_DATA = {\"sentinel\": true};\n", encoding="utf-8")

        seed_payload = {
            "run": {"run_id": "seed-test", "runner": "today_radar.py"},
            "brief": {
                "event_count": 3,
                "overview": {"source_mode": "seed"},
                "real_event_snapshot": {"usable": False, "reason": "stale"},
                "events": [
                    {
                        "event_title": "Seed fallback card",
                        "event_summary": "seed summary",
                        "event_type": "policy",
                        "risk_level": "medium",
                    }
                ],
            },
            "publish_payload": {
                "meta": {"run_id": "seed-test", "source_mode": "seed", "event_count": 1},
                "overview": {"source_mode": "seed"},
                "dashboard": {},
                "today_actions": [],
                "watch_items": [],
                "hold_line": "",
                "fulfillment_actions": [],
                "events": [
                    {
                        "id": "seed-event",
                        "category": "daily",
                        "title": "Seed fallback card",
                        "raw_title": "Seed fallback card",
                        "summary": "seed summary",
                        "level": "medium",
                        "type": "policy",
                        "typeLabel": "平台政策",
                        "platforms": ["多平台波及"],
                        "regions": ["全球"],
                        "impact": "seed summary",
                        "subject": "",
                        "action": "继续观察更多细则",
                        "source": {"name": "系统监测", "url": "#"},
                    }
                ],
                "macro_events": [],
                "urgent_events": [],
                "daily_events": [],
            },
            "rendered": "seed",
        }
        published_run.write_text(json.dumps(seed_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        seed_run = run_refresh(env)
        if seed_run.returncode != 0:
            errors.append(f"seed latest_run should still sync successfully: {seed_run.stderr.strip() or seed_run.stdout.strip()}")
        seed_text = target.read_text(encoding="utf-8")
        if '"source_mode": "seed"' not in seed_text:
            errors.append("seed latest_run should emit a seed-mode ui payload")
        if '"run_id": "seed-test"' not in seed_text:
            errors.append("seed latest_run should preserve seed run metadata")

        real_payload = {
            "run": {"run_id": "real-test", "runner": "run_radar.py"},
            "brief": {
                "event_count": 2,
                "brief_type": "morning_radar_demo",
                "overview": {"source_mode": "real"},
                "real_event_snapshot": {"usable": True, "reason": None},
                "fulfillment_actions": [],
                "events": [
                    {
                        "event_title": "EU parcel fee shock",
                        "raw_event_title": "EU parcel fee shock",
                        "event_summary": "EU officials are evaluating a parcel fee for low-value imports.",
                        "event_type": "tariff",
                        "risk_level": "high",
                        "region": "EU",
                        "source_platforms": ["TikTok", "Amazon"],
                        "seller_angle": "impact text",
                        "affected_sellers": ["low-ticket direct mail sellers"],
                        "suggested_actions": ["reprice skus"],
                        "sources": [{"name": "Reuters", "url": "https://example.com/reuters"}],
                        "brief_rank": 1,
                    }
                ],
            },
            "publish_payload": {
                "meta": {"run_id": "real-test", "source_mode": "real", "event_count": 1},
                "overview": {"source_mode": "real"},
                "dashboard": {},
                "today_actions": [],
                "watch_items": [],
                "hold_line": "",
                "fulfillment_actions": [],
                "events": [
                    {
                        "id": "real-event",
                        "category": "urgent",
                        "title": "低货值包裹税费与附加费风险上升",
                        "raw_title": "EU parcel fee shock",
                        "summary": "欧盟正在评估针对低货值进口包裹的附加费用。",
                        "level": "high",
                        "type": "tariff",
                        "typeLabel": "关税与税务",
                        "platforms": ["TikTok", "Amazon"],
                        "regions": ["EU"],
                        "impact": "impact text",
                        "subject": "low-ticket direct mail sellers",
                        "action": "reprice skus",
                        "source": {"name": "Reuters", "url": "https://example.com/reuters"},
                    }
                ],
                "macro_events": [],
                "urgent_events": [{"id": "real-event"}],
                "daily_events": [],
            },
            "rendered": "real",
        }
        published_run.write_text(json.dumps(real_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        real_run = run_refresh(env)
        if real_run.returncode != 0:
            errors.append(f"real latest_run should sync successfully: {real_run.stderr.strip() or real_run.stdout.strip()}")
        target_text = target.read_text(encoding="utf-8")
        if "window.RADAR_UI_DATA =" not in target_text:
            errors.append("real latest_run should emit RADAR_UI_DATA payload")
        if '"run_id": "real-test"' not in target_text:
            errors.append("real latest_run should preserve run metadata in ui payload")
        if '"title": "低货值包裹税费与附加费风险上升"' not in target_text:
            errors.append("real latest_run should localize english event titles before ui display")
        if '"raw_title": "EU parcel fee shock"' not in target_text:
            errors.append("real latest_run should preserve raw english title for traceability")
        if '"category": "urgent"' not in target_text:
            errors.append("high-risk brief events should become urgent cards in ui payload")

        official_payload = {
            "run": {"run_id": "official-p0-test", "runner": "run_radar.py"},
            "brief": {
                "event_count": 1,
                "overview": {"source_mode": "real"},
                "real_event_snapshot": {"usable": True, "reason": "fresh"},
                "events": [
                    {
                        "event_title": "Amazon policy update",
                        "raw_event_title": "Amazon policy update",
                        "event_summary": "summary",
                        "event_type": "policy",
                        "risk_level": "medium",
                        "source_layer": "official-content",
                        "source_type": "platform-official",
                        "source_priority": "P0",
                        "sources": [{"name": "Amazon", "url": "https://example.com/amazon"}],
                    }
                ],
            },
            "publish_payload": {
                "meta": {"run_id": "official-p0-test", "source_mode": "real", "event_count": 1},
                "overview": {"source_mode": "real"},
                "dashboard": {},
                "today_actions": [],
                "watch_items": [],
                "hold_line": "",
                "fulfillment_actions": [],
                "events": [
                    {
                        "id": "official-event",
                        "category": "urgent",
                        "title": "Amazon 平台规则更新",
                        "raw_title": "Amazon policy update",
                        "summary": "summary",
                        "level": "medium",
                        "type": "policy",
                        "typeLabel": "平台政策",
                        "platforms": ["多平台波及"],
                        "regions": ["全球"],
                        "impact": "summary",
                        "subject": "",
                        "action": "继续观察更多细则",
                        "source": {"name": "Amazon", "url": "https://example.com/amazon"},
                    }
                ],
                "macro_events": [],
                "urgent_events": [{"id": "official-event"}],
                "daily_events": [],
            },
            "rendered": "official",
        }
        published_run.write_text(json.dumps(official_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        official_run = run_refresh(env)
        if official_run.returncode != 0:
            errors.append(f"official latest_run should sync successfully: {official_run.stderr.strip() or official_run.stdout.strip()}")
        official_text = target.read_text(encoding="utf-8")
        if '"category": "urgent"' not in official_text:
            errors.append("official P0 events should become urgent cards even when risk_level is medium")

        no_payload = {
            "run": {"run_id": "legacy-run", "runner": "run_radar.py", "generated_at": "2026-03-14T00:00:00Z"},
            "brief": {
                "event_count": 1,
                "overview": {"source_mode": "real"},
                "real_event_snapshot": {"usable": True, "reason": "fresh"},
                "events": [
                    {
                        "event_title": "EU parcel fee shock",
                        "raw_event_title": "EU parcel fee shock",
                        "event_summary": "EU officials are evaluating a parcel fee for low-value imports.",
                        "event_type": "tariff",
                        "risk_level": "high",
                        "region": "EU",
                        "sources": [{"name": "Reuters", "url": "https://example.com/reuters"}],
                        "brief_rank": 1,
                    }
                ],
            },
            "rendered": "legacy",
        }
        published_run.write_text(json.dumps(no_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        legacy_run = run_refresh(env)
        if legacy_run.returncode != 0:
            errors.append(f"legacy published run should still sync successfully: {legacy_run.stderr.strip() or legacy_run.stdout.strip()}")
        legacy_text = target.read_text(encoding="utf-8")
        if '"title": "低货值包裹税费与附加费风险上升"' not in legacy_text:
            errors.append("legacy published run should fallback to backend publish payload builder")

    if errors:
        print("FAIL validate_refresh_radar_data")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_refresh_radar_data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
