#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
INGEST_SOURCES = SCRIPT_DIR / "ingest_sources.py"
TODAY_RADAR = SCRIPT_DIR / "today_radar.py"
REFRESH_UI = SCRIPT_DIR.parent / "ui" / "refresh_radar_data.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync optional changedetection feed, fetch real events, build latest radar run, and refresh UI data."
    )
    parser.add_argument("--changedetection-file", help="Sync changedetection RSS XML from a local file before refresh")
    parser.add_argument("--changedetection-url", help="Sync changedetection RSS XML from a URL before refresh")
    parser.add_argument("--profile", help="Optional today_radar profile alias, such as tiktok / amazon / independent-site")
    parser.add_argument("--json", action="store_true", help="Build the latest run in JSON mode")
    return parser.parse_args()


def run_step(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def main() -> int:
    args = parse_args()
    steps: list[dict] = []

    ingest_cmd = [sys.executable, str(INGEST_SOURCES)]
    if args.changedetection_file and args.changedetection_url:
        print(json.dumps({"error": "provide only one changedetection input"}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1
    if args.changedetection_file:
        ingest_cmd.extend(["--changedetection-file", args.changedetection_file])
    if args.changedetection_url:
        ingest_cmd.extend(["--changedetection-url", args.changedetection_url])
    ingest_proc = run_step(ingest_cmd)
    try:
        ingest_payload = json.loads(ingest_proc.stdout or ingest_proc.stderr or "{}")
    except json.JSONDecodeError:
        ingest_payload = {}
    ingest_steps = ingest_payload.get("steps") or []
    if ingest_steps:
        steps.extend(ingest_steps)
    else:
        steps.append({"step": "ingest_sources", "returncode": ingest_proc.returncode, "stdout": ingest_proc.stdout.strip(), "stderr": ingest_proc.stderr.strip()})

    radar_cmd = [sys.executable, str(TODAY_RADAR)]
    if args.profile:
        radar_cmd.append(args.profile)
    if args.json:
        radar_cmd.append("--json")
    radar_cmd.append("--publish")
    radar_proc = run_step(radar_cmd)
    steps.append({"step": "today_radar", "returncode": radar_proc.returncode, "stdout": radar_proc.stdout.strip(), "stderr": radar_proc.stderr.strip()})
    if radar_proc.returncode != 0:
        print(json.dumps({"error": "today_radar failed", "steps": steps}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    ui_proc = run_step([sys.executable, str(REFRESH_UI)])
    steps.append({"step": "refresh_ui", "returncode": ui_proc.returncode, "stdout": ui_proc.stdout.strip(), "stderr": ui_proc.stderr.strip()})
    if ui_proc.returncode != 0:
        print(json.dumps({"error": "ui refresh failed", "steps": steps}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(
        json.dumps(
            {
                "ok": True,
                "steps": steps,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
