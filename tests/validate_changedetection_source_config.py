#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "feed_source_config.py"

spec = importlib.util.spec_from_file_location("feed_source_config", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def main() -> int:
    errors: list[str] = []
    payload = module.load_changedetection_source()
    if payload.get("mode") not in {"url", "file"}:
        errors.append("changedetection source mode must be url or file")
    if not str(payload.get("source") or "").strip():
        errors.append("changedetection source must not be empty")

    if errors:
        print("FAIL validate_changedetection_source_config")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_changedetection_source_config")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
