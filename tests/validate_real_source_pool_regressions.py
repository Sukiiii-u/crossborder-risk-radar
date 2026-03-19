#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"
REAL_EVENTS = SKILL_ROOT / "runtime" / "data" / "real_events.json"
FIXTURE = ROOT / "fixtures" / "real_events_source_pool_boundary.json"


def main() -> int:
    REAL_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    original = REAL_EVENTS.read_text(encoding="utf-8") if REAL_EVENTS.exists() else None
    try:
        REAL_EVENTS.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "tiktok-direct-mail"],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        if original is None:
            REAL_EVENTS.unlink(missing_ok=True)
        else:
            REAL_EVENTS.write_text(original, encoding="utf-8")

    errors: list[str] = []
    if proc.returncode != 0:
        errors.append(proc.stderr.strip() or proc.stdout.strip() or "morning_brief failed")
    else:
        payload = json.loads(proc.stdout)
        titles = [item.get("event_title") for item in payload.get("events", [])]
        ids = [item.get("source_id") for item in payload.get("events", [])]

        expected_top3_set = {
            "reuters",
            "independent-site-regulators-cbp-ecommerce",
            "independent-site-regulators-eu-customs",
        }
        if set(ids[:3]) != expected_top3_set:
            errors.append(f"top 3 set mismatch: expected {sorted(expected_top3_set)!r}, got {ids[:3]!r}")
        if ids[:1] != ["reuters"]:
            errors.append("EU parcel fee tariff event should remain the top ranked event")

        if "Norfolk Southern to upgrade dozens of locomotives" in titles[:3]:
            errors.append("locomotive infrastructure story should not enter top 3")
        if "How Costco and B2B importers are rethinking oil-driven delivery costs" in titles[:3]:
            errors.append("macro B2B oil story should not enter top 3")
        if payload.get("overall_takeaway", "").count("最新抓取快照") != 1:
            errors.append("overall_takeaway should still describe latest-snapshot mode once")

    if errors:
        print("FAIL validate_real_source_pool_regressions")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_real_source_pool_regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
