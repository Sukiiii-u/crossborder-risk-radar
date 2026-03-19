#!/usr/bin/env python3
import json
import plistlib
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "generate_launchd_templates.py"
INGEST_PLIST = SKILL_ROOT / "automation" / "launchd" / "ai.crossborder-risk-radar.ingest.plist"
RENDER_PLIST = SKILL_ROOT / "automation" / "launchd" / "ai.crossborder-risk-radar.render.plist"


def run_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def read_plist(path: Path) -> dict:
    with path.open("rb") as fh:
        return plistlib.load(fh)


def main() -> int:
    errors: list[str] = []
    proc = run_cmd("--ingest-interval", "15", "--render-interval", "20")
    if proc.returncode != 0:
        errors.append(proc.stderr.strip() or proc.stdout.strip())
    else:
        payload = json.loads(proc.stdout)
        if payload.get("ingest_plist") != str(INGEST_PLIST):
            errors.append("ingest plist path mismatch")
        if payload.get("render_plist") != str(RENDER_PLIST):
            errors.append("render plist path mismatch")

    if not INGEST_PLIST.exists() or not RENDER_PLIST.exists():
        errors.append("launchd plist files should be generated")
    else:
        ingest = read_plist(INGEST_PLIST)
        render = read_plist(RENDER_PLIST)
        if ingest.get("Label") != "ai.crossborder-risk-radar.ingest":
            errors.append("ingest plist label mismatch")
        if render.get("Label") != "ai.crossborder-risk-radar.render":
            errors.append("render plist label mismatch")
        if ingest.get("StartInterval") != 900:
            errors.append("ingest StartInterval should match requested minutes")
        if render.get("StartInterval") != 1200:
            errors.append("render StartInterval should match requested minutes")
        if "ingest_sources.py" not in " ".join(ingest.get("ProgramArguments") or []):
            errors.append("ingest plist should call ingest_sources.py")
        if "render_radar_snapshot.py" not in " ".join(render.get("ProgramArguments") or []):
            errors.append("render plist should call render_radar_snapshot.py")

    if errors:
        print("FAIL validate_generate_launchd_templates")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_generate_launchd_templates")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
