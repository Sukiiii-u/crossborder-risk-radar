#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
TODAY_RADAR = SCRIPT_DIR / "today_radar.py"
REFRESH_UI = SCRIPT_DIR.parent / "ui" / "refresh_radar_data.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render radar output from the latest local snapshot without fetching external sources."
    )
    parser.add_argument("profile", nargs="?", help="Optional profile alias such as tiktok / amazon / independent-site")
    parser.add_argument("--seed-only", action="store_true", help="Force rendering from seed data only")
    return parser.parse_args()


def run_step(cmd: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=True, text=True, check=False)


def main() -> int:
    args = parse_args()
    steps: list[dict] = []

    radar_cmd = [sys.executable, str(TODAY_RADAR), "--json", "--publish"]
    if args.profile:
        radar_cmd.append(args.profile)
    if args.seed_only:
        radar_cmd.append("--seed-only")

    radar_proc = run_step(radar_cmd)
    steps.append(
        {
            "step": "today_radar",
            "returncode": radar_proc.returncode,
            "stdout": radar_proc.stdout.strip(),
            "stderr": radar_proc.stderr.strip(),
        }
    )
    if radar_proc.returncode != 0:
        print(json.dumps({"error": "today_radar failed", "steps": steps}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    ui_proc = run_step([sys.executable, str(REFRESH_UI)])
    steps.append(
        {
            "step": "refresh_ui",
            "returncode": ui_proc.returncode,
            "stdout": ui_proc.stdout.strip(),
            "stderr": ui_proc.stderr.strip(),
        }
    )
    if ui_proc.returncode != 0:
        print(json.dumps({"error": "ui refresh failed", "steps": steps}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1

    print(json.dumps({"ok": True, "steps": steps}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
