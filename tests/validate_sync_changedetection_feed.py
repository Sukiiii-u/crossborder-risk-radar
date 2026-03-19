#!/usr/bin/env python3
import json
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "sync_changedetection_feed.py"
CHANGEDETECTION_TARGET = SKILL_ROOT / "monitoring" / "changedetection_feed.xml"


def run_cmd(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False)


def main() -> int:
    errors: list[str] = []
    xml = """
    <rss><channel><title>changedetection</title>
      <item>
        <title>ChangeDetection.io Notification - https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</title>
        <link>https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</link>
        <description>TikTok Shop seller policy update adds fulfillment compliance checks.</description>
      </item>
      <item>
        <title>Hacker News</title>
        <link>http://127.0.0.1:5002/diff/unrelated</link>
        <description>Unrelated item</description>
      </item>
    </channel></rss>
    """.strip() + "\n"
    original = CHANGEDETECTION_TARGET.read_text(encoding="utf-8") if CHANGEDETECTION_TARGET.exists() else None
    config_file = SKILL_ROOT / "configs" / "changedetection_source.json"
    original_config = config_file.read_text(encoding="utf-8")

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp = Path(tmpdir)
        source = tmp / "feed.xml"
        source.write_text(xml, encoding="utf-8")

        proc = run_cmd("--from-file", str(source))
        if proc.returncode != 0:
            errors.append(f"sync from file failed: {proc.stderr.strip() or proc.stdout.strip()}")
        else:
            payload = json.loads(proc.stdout)
            if payload.get("synced") != str(CHANGEDETECTION_TARGET):
                errors.append("sync command should report canonical target path")
            if not CHANGEDETECTION_TARGET.exists():
                errors.append("sync command should write canonical target file")
            else:
                target_text = CHANGEDETECTION_TARGET.read_text(encoding="utf-8")
                if "Hacker News" in target_text:
                    errors.append("sync command should filter unrelated changedetection items")
                if "seller-us.tiktok.com/university/essay" not in target_text:
                    errors.append("sync command should preserve watchlist-matching changedetection items")
                if payload.get("kept_items") != 1:
                    errors.append("sync command should report kept watchlist item count")

        bad = run_cmd("--from-file", str(source), "--from-url", "https://example.com/feed.xml")
        if bad.returncode == 0:
            errors.append("sync command should fail when both inputs are provided")

        config_file.write_text(f'{{"mode":"file","source":"{str(source)}"}}\n', encoding="utf-8")
        default_proc = run_cmd()
        if default_proc.returncode != 0:
            errors.append(f"sync from configured source failed: {default_proc.stderr.strip() or default_proc.stdout.strip()}")
        else:
            payload = json.loads(default_proc.stdout)
            if payload.get("synced") != str(CHANGEDETECTION_TARGET):
                errors.append("sync command should support default configured source")

    if original is None:
        CHANGEDETECTION_TARGET.unlink(missing_ok=True)
    else:
        CHANGEDETECTION_TARGET.write_text(original, encoding="utf-8")
    config_file.write_text(original_config, encoding="utf-8")

    if errors:
        print("FAIL validate_sync_changedetection_feed")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_sync_changedetection_feed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
