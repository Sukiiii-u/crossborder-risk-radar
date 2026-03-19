#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"


REAL_PAYLOAD = {
    "generated_at": "2026-03-10T00:00:00+00:00",
    "event_count": 2,
    "events": [
        {
            "source_id": "test-reuters",
            "source_label": "Reuters",
            "source_topic": "tariff",
            "title": "EU considers new low-value parcel fee",
            "content": "EU officials are considering a new tariff and low-value parcel fee that would raise costs for direct-mail sellers shipping low-value packages into the European Union.",
            "url": "https://example.com/eu-parcel-fee",
            "published_at": "Tue, 10 Mar 2026 00:00:00 +0000",
            "fetched_at": "2026-03-10T00:00:01+00:00"
        },
        {
            "source_id": "test-freightwaves",
            "source_label": "FreightWaves",
            "source_topic": "logistics",
            "title": "Port delays worsen across Northern Europe",
            "zh_title": "北欧港口延误加剧",
            "zh_summary": "北欧港口拥堵恶化后，补货和履约时效的不确定性正在上升。",
            "content": "Shipping delays and port congestion across Northern Europe are disrupting inventory replenishment and fulfillment timelines for cross-border sellers.",
            "url": "https://example.com/port-delays",
            "published_at": "Tue, 10 Mar 2026 01:00:00 +0000",
            "fetched_at": "2026-03-10T01:00:01+00:00"
        }
    ],
    "failures": []
}


def run_brief(profile: dict | None = None, env: dict | None = None) -> dict:
    cmd = [sys.executable, str(SCRIPT)]
    if profile:
        cmd.append(json.dumps(profile, ensure_ascii=False))
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return json.loads(proc.stdout)


def main() -> int:
    profile = {
        "platform": "tiktok-shop",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "risk_profile": "margin-sensitive",
    }

    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        real_events = runtime_root / "data" / "real_events.json"
        real_events.parent.mkdir(parents=True, exist_ok=True)
        real_events.write_text(json.dumps(REAL_PAYLOAD, ensure_ascii=False, indent=2), encoding="utf-8")
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))
        result = run_brief(profile, env=env)

    errors = []
    if result.get("event_count") != 2:
        errors.append("expected 2 real events")
    if "最新抓取快照" not in result.get("overall_takeaway", ""):
        errors.append("overall_takeaway should mention latest snapshot")
    if not result.get("key_signal"):
        errors.append("missing key_signal")
    if not result.get("overview") or not result.get("fulfillment_actions"):
        errors.append("real event brief missing layered structure")

    events = result.get("events", [])
    if not any(event.get("source_label") == "Reuters" for event in events):
        errors.append("missing Reuters source label")
    if not any(event.get("event_title") == "低货值包裹税费与附加费风险上升" for event in events):
        errors.append("missing localized real event title fallback")
    if not any(event.get("sources") and event["sources"][0].get("url") == "https://example.com/eu-parcel-fee" for event in events):
        errors.append("missing real event source url")
    if not any(event.get("event_type") == "tariff" for event in events):
        errors.append("missing tariff classification from real event")
    if not any(event.get("event_type") == "logistics" for event in events):
        errors.append("missing logistics classification from real event")
    if events and events[0].get("event_type") != "tariff":
        errors.append("tariff event should outrank logistics for margin-sensitive direct-mail profile")
    if events:
        applicability = events[0].get("applicability_layers", {})
        if applicability.get("current_view", {}).get("label") != "高相关":
            errors.append("top tariff event should show 高相关 for direct-mail current view")
        if not applicability.get("medium_relevance"):
            errors.append("top tariff event should still expose medium relevance operating situations")
        if not applicability.get("low_relevance_or_watch"):
            errors.append("top tariff event should still expose low relevance / watch operating situations")

    if errors:
        print("FAIL validate_real_event_morning_brief")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_real_event_morning_brief")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
