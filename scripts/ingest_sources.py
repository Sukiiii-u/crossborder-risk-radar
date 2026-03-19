#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from runtime_paths import INGEST_STATUS_FILE, ensure_runtime_data_dir  # noqa: E402

SYNC_CHANGEDETECTION = SCRIPT_DIR / "sync_changedetection_feed.py"
FETCH_REAL_EVENTS = SCRIPT_DIR / "fetch_real_events.py"
FETCH_POLICY_WATCH = SCRIPT_DIR / "fetch_policy_watch.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Ingest external source snapshots into runtime/data without rendering radar output."
    )
    parser.add_argument("--changedetection-file", help="Sync changedetection RSS XML from a local file before ingest")
    parser.add_argument("--changedetection-url", help="Sync changedetection RSS XML from a URL before ingest")
    return parser.parse_args()


def run_step(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def write_status(payload: dict) -> None:
    ensure_runtime_data_dir()
    INGEST_STATUS_FILE.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    steps: list[dict] = []

    if args.changedetection_file and args.changedetection_url:
        error_payload = {"ok": False, "error": "provide only one changedetection input", "steps": []}
        write_status(error_payload)
        print(json.dumps(error_payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    sync_cmd = [sys.executable, str(SYNC_CHANGEDETECTION)]
    if args.changedetection_file:
        sync_cmd.extend(["--from-file", args.changedetection_file])
    if args.changedetection_url:
        sync_cmd.extend(["--from-url", args.changedetection_url])
    proc = run_step(sync_cmd)
    steps.append(
        {
            "step": "sync_changedetection_feed",
            "returncode": proc.returncode,
            "stdout": proc.stdout.strip(),
            "stderr": proc.stderr.strip(),
        }
    )
    if proc.returncode != 0:
        payload = {"ok": False, "error": "changedetection sync failed", "steps": steps}
        write_status(payload)
        print(json.dumps(payload, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    fetch_proc = run_step([sys.executable, str(FETCH_REAL_EVENTS)])
    steps.append(
        {
            "step": "fetch_real_events",
            "returncode": fetch_proc.returncode,
            "stdout": fetch_proc.stdout.strip(),
            "stderr": fetch_proc.stderr.strip(),
        }
    )

    policy_proc = run_step([sys.executable, str(FETCH_POLICY_WATCH)])
    steps.append(
        {
            "step": "fetch_policy_watch",
            "returncode": policy_proc.returncode,
            "stdout": policy_proc.stdout.strip(),
            "stderr": policy_proc.stderr.strip(),
        }
    )

    payload = {
        "ok": fetch_proc.returncode == 0 and policy_proc.returncode == 0,
        "steps": steps,
    }
    if fetch_proc.returncode != 0 or policy_proc.returncode != 0:
        payload["warning"] = "ingest completed with source failures"
    write_status(payload)

    stream = sys.stdout if payload["ok"] else sys.stderr
    print(json.dumps(payload, ensure_ascii=False, indent=2), file=stream)
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
