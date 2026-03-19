#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "refresh_radar_pipeline.py"
CHANGEDETECTION_TARGET = SKILL_ROOT / "monitoring" / "changedetection_feed.xml"


def run_cmd(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False, env=env)


def main() -> int:
    errors: list[str] = []
    original_feed = CHANGEDETECTION_TARGET.read_text(encoding="utf-8") if CHANGEDETECTION_TARGET.exists() else None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        runtime_root = tmp / "runtime"
        feed = tmp / "feed.xml"
        policy_config = tmp / "policy_watch_sources.json"
        eu = tmp / "eu.html"
        cbp = tmp / "cbp.html"
        ui_target = tmp / "radar-data.js"
        feed.write_text("<rss><channel><item><title>ChangeDetection.io Notification - https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</title><link>https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</link><description>TikTok Shop seller policy update adds fulfillment compliance checks.</description><pubDate>Fri, 13 Mar 2026 00:00:00 GMT</pubDate></item></channel></rss>", encoding="utf-8")
        eu.write_text("<html><head><title>EU policy</title><meta name=\"description\" content=\"150 EUR customs duty exemption for e-commerce parcels.\" /></head><body>150 EUR customs duty e-commerce parcels</body></html>", encoding="utf-8")
        cbp.write_text("<html><head><title>CBP policy</title><meta name=\"description\" content=\"Section 321 Entry Type 86 low-value shipments.\" /></head><body>section 321 entry type 86 low-value shipments</body></html>", encoding="utf-8")
        policy_config.write_text(json.dumps([
            {
                "id": "eu-test",
                "title": "EU policy",
                "url": eu.resolve().as_uri(),
                "source_name": "European Commission",
                "source_type": "regulator-official",
                "platforms": ["TikTok"],
                "regions": ["EU"],
                "event_type": "tariff",
                "risk_level": "high",
                "match_any_keywords": ["150 eur", "customs duty"],
                "action": "复核欧盟税费"
            },
            {
                "id": "cbp-test",
                "title": "CBP policy",
                "url": cbp.resolve().as_uri(),
                "source_name": "CBP",
                "source_type": "regulator-official",
                "platforms": ["TikTok"],
                "regions": ["US"],
                "event_type": "customs",
                "risk_level": "high",
                "match_any_keywords": ["section 321", "entry type 86"],
                "action": "复核美国清关资料"
            }
        ], ensure_ascii=False, indent=2), encoding="utf-8")
        env = dict(
            os.environ,
            POLICY_WATCH_CONFIG_FILE=str(policy_config),
            CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root),
            CROSSBORDER_RADAR_UI_DATA_FILE=str(ui_target),
        )

        proc = run_cmd("--changedetection-file", str(feed), "--profile", "tiktok", "--json", env=env)
        if proc.returncode != 0:
            errors.append(f"pipeline command failed: {proc.stderr.strip() or proc.stdout.strip()}")
        else:
            payload = json.loads(proc.stdout)
            if payload.get("ok") is not True:
                errors.append("pipeline should report ok=true")
            steps = payload.get("steps") or []
            labels = [step.get("step") for step in steps]
            if labels != ["sync_changedetection_feed", "fetch_real_events", "fetch_policy_watch", "today_radar", "refresh_ui"]:
                errors.append(f"unexpected step order: {labels!r}")
            if any(step.get("returncode") != 0 for step in steps):
                errors.append("all pipeline steps should succeed")
            sync_step = next((step for step in steps if step.get("step") == "sync_changedetection_feed"), {})
            try:
                sync_payload = json.loads(sync_step.get("stdout") or "{}")
            except json.JSONDecodeError:
                sync_payload = {}
            if sync_payload.get("synced") != str(CHANGEDETECTION_TARGET):
                errors.append("pipeline should report canonical changedetection target path")
            if CHANGEDETECTION_TARGET.exists():
                if "<rss" not in CHANGEDETECTION_TARGET.read_text(encoding="utf-8"):
                    errors.append("canonical changedetection target should remain a valid rss file")
            if not ui_target.exists():
                errors.append("pipeline should render ui payload into configured target")

    if original_feed is None:
        CHANGEDETECTION_TARGET.unlink(missing_ok=True)
    else:
        CHANGEDETECTION_TARGET.write_text(original_feed, encoding="utf-8")

    if errors:
        print("FAIL validate_refresh_radar_pipeline")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_refresh_radar_pipeline")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
