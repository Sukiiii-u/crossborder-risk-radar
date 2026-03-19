#!/usr/bin/env python3
import argparse
import json
import plistlib
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
AUTOMATION_DIR = SKILL_ROOT / "automation" / "launchd"
INGEST_SCRIPT = SCRIPT_DIR / "ingest_sources.py"
RENDER_SCRIPT = SCRIPT_DIR / "render_radar_snapshot.py"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate launchd plist templates for scheduled ingest and render jobs."
    )
    parser.add_argument("--python", default=sys.executable, help="Python interpreter path to embed in plist files")
    parser.add_argument("--ingest-interval", type=int, default=30, help="Ingest interval in minutes")
    parser.add_argument("--render-interval", type=int, default=30, help="Render interval in minutes")
    return parser.parse_args()


def write_plist(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as fh:
        plistlib.dump(payload, fh, sort_keys=False)


def build_job(label: str, interval_minutes: int, program_args: list[str], stdout_path: Path, stderr_path: Path) -> dict:
    return {
        "Label": label,
        "ProgramArguments": program_args,
        "WorkingDirectory": str(SKILL_ROOT),
        "StartInterval": max(60, interval_minutes * 60),
        "RunAtLoad": True,
        "StandardOutPath": str(stdout_path),
        "StandardErrorPath": str(stderr_path),
    }


def main() -> int:
    args = parse_args()
    ingest_stdout = SKILL_ROOT / "runtime" / "logs" / "ingest.out.log"
    ingest_stderr = SKILL_ROOT / "runtime" / "logs" / "ingest.err.log"
    render_stdout = SKILL_ROOT / "runtime" / "logs" / "render.out.log"
    render_stderr = SKILL_ROOT / "runtime" / "logs" / "render.err.log"

    ingest_job = build_job(
        label="ai.crossborder-risk-radar.ingest",
        interval_minutes=args.ingest_interval,
        program_args=[args.python, str(INGEST_SCRIPT)],
        stdout_path=ingest_stdout,
        stderr_path=ingest_stderr,
    )
    render_job = build_job(
        label="ai.crossborder-risk-radar.render",
        interval_minutes=args.render_interval,
        program_args=[args.python, str(RENDER_SCRIPT)],
        stdout_path=render_stdout,
        stderr_path=render_stderr,
    )

    ingest_plist = AUTOMATION_DIR / "ai.crossborder-risk-radar.ingest.plist"
    render_plist = AUTOMATION_DIR / "ai.crossborder-risk-radar.render.plist"
    write_plist(ingest_plist, ingest_job)
    write_plist(render_plist, render_job)

    print(json.dumps({"ingest_plist": str(ingest_plist), "render_plist": str(render_plist)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
