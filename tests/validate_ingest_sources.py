#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "ingest_sources.py"
STATUS_FILE = SKILL_ROOT / "runtime" / "data" / "ingest_status.json"
CHANGEDETECTION_TARGET = SKILL_ROOT / "monitoring" / "changedetection_feed.xml"


def run_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def main() -> int:
    errors: list[str] = []
    original_status = STATUS_FILE.read_text(encoding="utf-8") if STATUS_FILE.exists() else None
    original_feed = CHANGEDETECTION_TARGET.read_text(encoding="utf-8") if CHANGEDETECTION_TARGET.exists() else None

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        feed = tmp / "feed.xml"
        feed.write_text(
            "<rss><channel><item><title>ChangeDetection.io Notification - https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</title><link>https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</link><description>TikTok Shop seller policy update adds fulfillment compliance checks.</description><pubDate>Fri, 13 Mar 2026 00:00:00 GMT</pubDate></item></channel></rss>",
            encoding="utf-8",
        )
        proc = run_cmd("--changedetection-file", str(feed))
        if proc.returncode not in {0, 1}:
            errors.append(f"ingest command returned unexpected code: {proc.returncode}")

        stream = proc.stdout if proc.stdout.strip() else proc.stderr
        try:
            payload = json.loads(stream)
        except json.JSONDecodeError as exc:
            errors.append(f"ingest output invalid json: {exc}")
            payload = {}

        steps = payload.get("steps") or []
        labels = [step.get("step") for step in steps]
        if labels[:3] != ["sync_changedetection_feed", "fetch_real_events", "fetch_policy_watch"]:
            errors.append(f"unexpected ingest step order: {labels!r}")

        if not STATUS_FILE.exists():
            errors.append("ingest should persist runtime/data/ingest_status.json")
        else:
            status_payload = json.loads(STATUS_FILE.read_text(encoding="utf-8"))
            if not isinstance(status_payload.get("steps"), list):
                errors.append("ingest status should include serialized steps")

    if original_status is None:
        STATUS_FILE.unlink(missing_ok=True)
    else:
        STATUS_FILE.write_text(original_status, encoding="utf-8")

    if original_feed is None:
        CHANGEDETECTION_TARGET.unlink(missing_ok=True)
    else:
        CHANGEDETECTION_TARGET.write_text(original_feed, encoding="utf-8")

    if errors:
        print("FAIL validate_ingest_sources")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_ingest_sources")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
