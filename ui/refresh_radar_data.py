#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

UI_DIR = Path(__file__).resolve().parent
SKILL_DIR = UI_DIR.parent
SCRIPTS_DIR = SKILL_DIR / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from runtime_paths import PUBLISHED_RUN_FILE  # noqa: E402
from published_snapshot import build_publish_payload  # noqa: E402

SOURCE = PUBLISHED_RUN_FILE
TARGET = Path(
    os.environ.get(
        "CROSSBORDER_RADAR_UI_DATA_FILE",
        str(UI_DIR / "radar-data.js"),
    )
).expanduser()

def is_usable_python_run(data: dict) -> bool:
    brief = data.get("brief", {})
    run = data.get("run", {})
    if not isinstance(brief, dict):
        return False
    if not isinstance(run, dict):
        return False
    if run.get("runner") not in {"run_radar.py", "today_radar.py"}:
        return False
    return isinstance(brief.get("events"), list) and bool(brief.get("event_count"))


def main() -> None:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    if not is_usable_python_run(data):
        raise SystemExit(
            "latest_run.json is not a usable Python run; preserving existing ui/radar-data.js"
        )
    # 总是重新构建 payload，确保翻译/去重等更新都能反映到 UI
    ui_payload = build_publish_payload(data)
    TARGET.write_text(
        "window.RADAR_UI_DATA = " + json.dumps(ui_payload, ensure_ascii=False, indent=2) + ";\n",
        encoding="utf-8",
    )
    print(f"synced {TARGET}")


if __name__ == "__main__":
    main()
