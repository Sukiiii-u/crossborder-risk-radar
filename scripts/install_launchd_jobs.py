#!/usr/bin/env python3
import json
import os
import plistlib
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
TEMPLATE_DIR = SKILL_ROOT / "automation" / "launchd"
USER_AGENTS_DIR = Path.home() / "Library" / "LaunchAgents"
INGEST_LABEL = "ai.crossborder-risk-radar.ingest"
RENDER_LABEL = "ai.crossborder-risk-radar.render"


def ensure_runtime_logs_dir() -> None:
    (SKILL_ROOT / "runtime" / "logs").mkdir(parents=True, exist_ok=True)


def install_plist(template_name: str) -> Path:
    template_path = TEMPLATE_DIR / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"missing launchd template: {template_path}")
    USER_AGENTS_DIR.mkdir(parents=True, exist_ok=True)
    target = USER_AGENTS_DIR / template_name
    shutil.copy2(template_path, target)
    with target.open("rb") as fh:
        plistlib.load(fh)
    return target


def run_launchctl(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(["launchctl", *args], capture_output=True, text=True, check=False)


def bootstrap_agent(label: str, plist_path: Path) -> dict:
    domain = f"gui/{os.getuid()}"
    bootout = run_launchctl("bootout", domain, str(plist_path))
    bootstrap = run_launchctl("bootstrap", domain, str(plist_path))
    enable = run_launchctl("enable", f"{domain}/{label}")
    kickstart = run_launchctl("kickstart", "-k", f"{domain}/{label}")
    print_proc = run_launchctl("print", f"{domain}/{label}")
    return {
        "label": label,
        "plist": str(plist_path),
        "bootout": {"returncode": bootout.returncode, "stderr": bootout.stderr.strip()},
        "bootstrap": {"returncode": bootstrap.returncode, "stderr": bootstrap.stderr.strip()},
        "enable": {"returncode": enable.returncode, "stderr": enable.stderr.strip()},
        "kickstart": {"returncode": kickstart.returncode, "stderr": kickstart.stderr.strip()},
        "print": {"returncode": print_proc.returncode, "stdout": print_proc.stdout.strip(), "stderr": print_proc.stderr.strip()},
    }


def main() -> int:
    ensure_runtime_logs_dir()
    ingest_plist = install_plist("ai.crossborder-risk-radar.ingest.plist")
    render_plist = install_plist("ai.crossborder-risk-radar.render.plist")

    result = {
        "ingest": bootstrap_agent(INGEST_LABEL, ingest_plist),
        "render": bootstrap_agent(RENDER_LABEL, render_plist),
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
