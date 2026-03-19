#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "audit_summary.py"
AUDIT_FILE = SKILL_ROOT / "runtime" / "data" / "real_events_audit.json"

FIXTURE = {
    "generated_at": "2026-03-12T03:00:00+00:00",
    "by_source": {
        "reuters": {
            "label": "Reuters",
            "topic": "policy",
            "trust_tier": "official",
            "seller_signal_bias": "high",
            "kept_count": 2,
            "drop_counts": {
                "noise": 1,
                "low_relevance": 2
            },
            "kept_samples": [
                {"title": "EU weighs low-value parcel fee for imported packages"},
                {"title": "EU customs update changes parcel declaration workflow"}
            ],
            "dropped_samples": {
                "noise": [
                    {"title": "Podcast: global policy roundtable"}
                ],
                "low_relevance": [
                    {"title": "Local culture feature"}
                ]
            }
        },
        "freightwaves": {
            "label": "FreightWaves",
            "topic": "logistics",
            "trust_tier": "industry",
            "seller_signal_bias": "medium",
            "kept_count": 1,
            "drop_counts": {
                "duplicate": 1
            },
            "kept_samples": [
                {"title": "Northern Europe congestion delays seller replenishment"}
            ],
            "dropped_samples": {
                "duplicate": [
                    {"title": "Northern Europe congestion delays seller replenishment"}
                ]
            }
        }
    }
}


def run_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def main() -> int:
    AUDIT_FILE.parent.mkdir(parents=True, exist_ok=True)
    original = AUDIT_FILE.read_text(encoding="utf-8") if AUDIT_FILE.exists() else None
    try:
        AUDIT_FILE.write_text(json.dumps(FIXTURE, ensure_ascii=False, indent=2), encoding="utf-8")
        human = run_cmd()
        raw = run_cmd("--json")
    finally:
        if original is None:
            AUDIT_FILE.unlink(missing_ok=True)
        else:
            AUDIT_FILE.write_text(original, encoding="utf-8")

    errors = []
    if human.returncode != 0:
        errors.append(f"human summary failed: {human.stderr.strip() or human.stdout.strip()}")
    else:
        output = human.stdout
        if "# 抓取审计摘要" not in output:
            errors.append("human summary missing title")
        if "主要丢弃原因" not in output:
            errors.append("human summary missing drop reason section")
        if "Reuters" not in output or "FreightWaves" not in output:
            errors.append("human summary missing source labels")
        if "noise: 1" not in output and "noise" not in output:
            errors.append("human summary missing noise drop reason")
        if "EU weighs low-value parcel fee for imported packages" not in output:
            errors.append("human summary missing kept sample title")
        if "Podcast: global policy roundtable" not in output:
            errors.append("human summary missing dropped sample title")

    if raw.returncode != 0:
        errors.append(f"json summary failed: {raw.stderr.strip() or raw.stdout.strip()}")
    else:
        payload = json.loads(raw.stdout)
        if payload.get("generated_at") != FIXTURE["generated_at"]:
            errors.append("json summary should echo raw audit payload")
        if "reuters" not in payload.get("by_source", {}):
            errors.append("json summary missing by_source payload")

    if errors:
        print("FAIL validate_audit_summary")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_audit_summary")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
