#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "run_radar.py"


def run_cmd(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False, env=env)


def main() -> int:
    errors = []
    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        data_dir = runtime_root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        audit_file = data_dir / "real_events_audit.json"
        real_events_file = data_dir / "real_events.json"
        latest_run = runtime_root / "latest_run.json"
        latest_rendered = runtime_root / "latest_rendered.txt"
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))

        audit_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-03-12T04:00:00+00:00",
                    "by_source": {
                        "reuters": {
                            "label": "Reuters",
                            "topic": "policy",
                            "trust_tier": "official",
                            "seller_signal_bias": "high",
                            "kept_count": 2,
                            "drop_counts": {"noise": 1},
                            "kept_samples": [{"title": "EU weighs low-value parcel fee for imported packages"}],
                            "dropped_samples": {"noise": [{"title": "Podcast: global policy roundtable"}]},
                        }
                    },
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )

        json_run = run_cmd("--mode", "evening", "--source", "seed", "--format", "json", "tiktok", env=env)
        if json_run.returncode != 0:
            errors.append(f"json run failed: {json_run.stderr.strip() or json_run.stdout.strip()}")
        else:
            try:
                payload = json.loads(json_run.stdout)
            except json.JSONDecodeError as exc:
                errors.append(f"json output invalid: {exc}")
                payload = {}

            if payload.get("delivery_mode") != "evening":
                errors.append("delivery_mode mismatch for evening run")
            if payload.get("requested_source_mode") != "seed":
                errors.append("requested_source_mode mismatch")
            if payload.get("profile_preset") != "tiktok-direct-mail":
                errors.append("profile alias did not resolve in scheduled runner")
            if payload.get("brief_type") != "morning_radar_demo":
                errors.append("brief_type mismatch in scheduled runner")
            delivery = payload.get("delivery_metadata", {})
            if delivery.get("mode") != "evening":
                errors.append("delivery_metadata.mode mismatch")
            if delivery.get("trigger") != "scheduled":
                errors.append("delivery_metadata.trigger mismatch")
            if not delivery.get("generated_at"):
                errors.append("delivery_metadata.generated_at missing")
            if delivery.get("delivery_status") != "prepared":
                errors.append("delivery_metadata.delivery_status mismatch")
            if not delivery.get("delivery_key", "").startswith("scheduled:evening:tiktok-direct-mail:"):
                errors.append("delivery_metadata.delivery_key mismatch")
            if delivery.get("delivery_targets") != []:
                errors.append("delivery_metadata.delivery_targets should default to empty list")
            state_files = delivery.get("state_files", {})
            if not state_files.get("latest_run"):
                errors.append("delivery_metadata.state_files.latest_run missing")
            if not state_files.get("run_snapshot"):
                errors.append("delivery_metadata.state_files.run_snapshot missing")
            if not state_files.get("runs_dir"):
                errors.append("delivery_metadata.state_files.runs_dir missing")

        duplicate_run = run_cmd("--mode", "evening", "--source", "seed", "--format", "json", "tiktok", env=env)
        if duplicate_run.returncode != 0:
            errors.append(f"duplicate run failed: {duplicate_run.stderr.strip() or duplicate_run.stdout.strip()}")
        else:
            duplicate_payload = json.loads(duplicate_run.stdout)
            duplicate_delivery = duplicate_payload.get("delivery_metadata", {})
            if duplicate_delivery.get("is_duplicate_of_last") is not True:
                errors.append("duplicate run should be marked as duplicate_of_last")
            if not duplicate_delivery.get("duplicate_of_run_id"):
                errors.append("duplicate run should point to duplicate_of_run_id")
            if duplicate_delivery.get("previous_run_id") != duplicate_delivery.get("duplicate_of_run_id"):
                errors.append("duplicate previous_run_id should match duplicate_of_run_id")

        alias_run = run_cmd("--mode", "pm", "--source", "seed", "--format", "json", "tiktok", env=env)
        if alias_run.returncode != 0:
            errors.append(f"alias mode run failed: {alias_run.stderr.strip() or alias_run.stdout.strip()}")
        else:
            alias_payload = json.loads(alias_run.stdout)
            alias_delivery = alias_payload.get("delivery_metadata", {})
            if alias_payload.get("delivery_mode") != "evening":
                errors.append("pm alias should canonicalize to evening delivery_mode")
            if alias_delivery.get("mode") != "evening":
                errors.append("pm alias should canonicalize to evening delivery_metadata.mode")

        human_run = run_cmd("--source", "seed", "--format", "human", "--preset", "independent-site", "--market", "FR", env=env)
        if human_run.returncode != 0:
            errors.append(f"human run failed: {human_run.stderr.strip() or human_run.stdout.strip()}")
        else:
            if "# 今日跨境风险晨报" not in human_run.stdout:
                errors.append("human output missing title")
            if "履约主视角：跨境直发" not in human_run.stdout or "平台修正：独立站" not in human_run.stdout:
                errors.append("human output should present independent-site view as fulfillment-first with platform modifier")

        audit_json_run = run_cmd("--source", "seed", "--format", "json", "--audit-summary", "tiktok", env=env)
        if audit_json_run.returncode != 0:
            errors.append(f"audit json run failed: {audit_json_run.stderr.strip() or audit_json_run.stdout.strip()}")
        else:
            audit_payload = json.loads(audit_json_run.stdout)
            if not audit_payload.get("audit_summary"):
                errors.append("audit summary should be attached in json mode when requested")
            elif "reuters" not in audit_payload.get("audit_summary", {}).get("by_source", {}):
                errors.append("audit summary should preserve raw audit payload in json mode")

        audit_human_run = run_cmd("--source", "seed", "--format", "human", "--audit-summary", "tiktok", env=env)
        if audit_human_run.returncode != 0:
            errors.append(f"audit human run failed: {audit_human_run.stderr.strip() or audit_human_run.stdout.strip()}")
        else:
            if "# 抓取审计摘要" not in audit_human_run.stdout:
                errors.append("human output should append audit summary when requested")
            if "Podcast: global policy roundtable" not in audit_human_run.stdout:
                errors.append("human audit summary should include dropped sample titles")

        real_events_file.write_text(
            json.dumps(
                {
                    "generated_at": "2026-03-01T00:00:00+00:00",
                    "event_count": 1,
                    "events": [
                        {
                            "source_id": "test-reuters",
                            "source_label": "Reuters",
                            "source_topic": "tariff",
                            "title": "Old tariff snapshot should not be treated as fresh",
                            "content": "Tariff and parcel fee changes raise costs for direct-mail sellers in the European Union.",
                            "url": "https://example.com/stale",
                            "published_at": "2026-03-01T00:00:00+00:00",
                            "fetched_at": "2026-03-01T00:00:00+00:00",
                        }
                    ],
                    "failures": [],
                },
                ensure_ascii=False,
                indent=2,
            ),
            encoding="utf-8",
        )
        stale_auto_run = run_cmd("--source", "auto", "--format", "json", "tiktok", env=env)
        if stale_auto_run.returncode != 0:
            errors.append(f"stale auto run failed: {stale_auto_run.stderr.strip() or stale_auto_run.stdout.strip()}")
        else:
            stale_payload = json.loads(stale_auto_run.stdout)
            snapshot = stale_payload.get("real_event_snapshot", {})
            if snapshot.get("usable") is not False or snapshot.get("reason") != "stale":
                errors.append("stale auto run should mark real snapshot as stale and unusable")
            if stale_payload.get("overview", {}).get("source_mode") != "seed":
                errors.append("stale auto run should fall back to seed output instead of stale real events")

        with tempfile.TemporaryDirectory() as tmpdir:
            out_path = Path(tmpdir) / "scheduled" / "radar.txt"
            file_run = run_cmd("amazon", "--source", "seed", "--output", str(out_path), env=env)
            if file_run.returncode != 0:
                errors.append(f"file output run failed: {file_run.stderr.strip() or file_run.stdout.strip()}")
            elif not out_path.exists():
                errors.append("scheduled output file was not created")
            else:
                content = out_path.read_text(encoding="utf-8")
                if "# 今日跨境风险晨报" not in content:
                    errors.append("scheduled output file missing rendered radar")

                if not latest_run.exists():
                    errors.append("latest_run.json was not created")
                else:
                    latest_payload = json.loads(latest_run.read_text(encoding="utf-8"))
                    run_meta = latest_payload.get("run", {})
                    if run_meta.get("runner") != "run_radar.py":
                        errors.append("latest_run.json runner mismatch")
                    if not run_meta.get("run_id"):
                        errors.append("latest_run.json missing run_id")
                    if run_meta.get("output_path") != str(out_path):
                        errors.append("latest_run.json output_path mismatch")
                    if not latest_payload.get("brief", {}).get("profile_label"):
                        errors.append("latest_run.json missing brief snapshot")

                if not latest_rendered.exists():
                    errors.append("latest_rendered.txt was not created")

        bad_mode = run_cmd("--mode", "lunch", env=env)
        if bad_mode.returncode == 0:
            errors.append("invalid mode should fail")
    if errors:
        print("FAIL validate_run_radar")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_run_radar")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
