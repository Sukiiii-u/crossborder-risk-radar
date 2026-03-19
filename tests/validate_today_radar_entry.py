#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "today_radar.py"


def run_cmd(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(SCRIPT), *args], capture_output=True, text=True, check=False, env=env)


def main() -> int:
    with tempfile.TemporaryDirectory() as runtime_tmp:
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=runtime_tmp)
        default_human = run_cmd("--seed-only", env=env)
        default_payload = run_cmd("--seed-only", "--json", env=env)
        human = run_cmd("tiktok", "--seed-only", env=env)
        payload = run_cmd("--preset", "independent-site", "--market", "FR", "--seed-only", "--json", env=env)
        published = run_cmd("--seed-only", "--publish", "--json", env=env)
        published_run_file = Path(runtime_tmp) / "published_run.json"
        published_run = json.loads(published_run_file.read_text(encoding="utf-8")) if published_run_file.exists() else {}

    errors = []
    if default_human.returncode != 0:
        errors.append(f"default human command failed: {default_human.stderr.strip() or default_human.stdout.strip()}")
    else:
        if "通用雷达首页（事件驱动 / 不绑定默认画像）" not in default_human.stdout:
            errors.append("today_radar default entry should render generic homepage label")
        if "平台范围：全平台扫描" not in default_human.stdout:
            errors.append("today_radar default entry should use generic platform range")
        if "本地履约-平台主导（平台修正：Amazon / 市场：德国站）" in default_human.stdout:
            errors.append("today_radar default entry should not render amazon-fba as the default view")

    if default_human.returncode != 0:
        errors.append(f"default human command failed: {default_human.stderr.strip() or default_human.stdout.strip()}")
    else:
        if "# 今日跨境风险晨报" not in default_human.stdout:
            errors.append("default human output missing title")
        if "首页模式：Dashboard 首页" not in default_human.stdout:
            errors.append("default human output should render dashboard homepage")
        if "## Dashboard 总览" not in default_human.stdout or "## 事件卡片" not in default_human.stdout:
            errors.append("default human output should render dashboard sections")
        if "展示标签：本地履约-平台主导（平台修正：Amazon / 市场：德国站）" in default_human.stdout or "履约主视角：本地履约-平台主导" in default_human.stdout:
            errors.append("default human output should not fall back to Amazon homepage layout")

    if default_payload.returncode != 0:
        errors.append(f"default json command failed: {default_payload.stderr.strip() or default_payload.stdout.strip()}")
    else:
        try:
            default_data = json.loads(default_payload.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"default json output invalid: {exc}")
            default_data = {}

        if default_data.get("brief_type") != "morning_radar_general":
            errors.append("default json should return morning_radar_general")
        if default_data.get("radar_mode") != "general_event_view":
            errors.append("default json should return general_event_view")
        if not default_data.get("dashboard"):
            errors.append("default json should expose dashboard summary data")
        if default_data.get("profile_preset") is not None:
            errors.append("default json should not silently resolve to amazon-fba")
        if default_data.get("seller_profile", {}).get("platform") != "general":
            errors.append("default json should use general radar profile")

    if human.returncode != 0:
        errors.append(f"human command failed: {human.stderr.strip() or human.stdout.strip()}")
    else:
        if "# 今日跨境风险晨报" not in human.stdout:
            errors.append("human output missing title")
        if "履约主视角：跨境直发" not in human.stdout:
            errors.append("tiktok shortcut should render fulfillment-first main heading")
        if "平台修正：TikTok Shop" not in human.stdout:
            errors.append("tiktok shortcut should demote platform to modifier label")
        if "## 总览判断" not in human.stdout or "## 分履约动作" not in human.stdout:
            errors.append("today_radar human output missing layered sections")

    if payload.returncode != 0:
        errors.append(f"json command failed: {payload.stderr.strip() or payload.stdout.strip()}")
    else:
        try:
            data = json.loads(payload.stdout)
        except json.JSONDecodeError as exc:
            errors.append(f"json output invalid: {exc}")
            data = {}

        if data.get("profile_preset") != "independent-site-direct-mail":
            errors.append("independent-site preset alias did not resolve")
        if data.get("seller_profile", {}).get("market") != "FR":
            errors.append("market override did not apply")
        if data.get("brief_type") != "morning_radar_demo":
            errors.append("brief_type mismatch")
        if data.get("event_count", 0) < 3:
            errors.append("expected seed-mode radar to include at least 3 events")
        delivery = data.get("delivery_metadata", {})
        if delivery.get("mode") != "morning":
            errors.append("today_radar delivery mode mismatch")
        if delivery.get("trigger") != "manual":
            errors.append("today_radar trigger mismatch")
        if delivery.get("source") != "seed":
            errors.append("today_radar source mode mismatch")
        if delivery.get("delivery_status") != "prepared":
            errors.append("today_radar delivery_status mismatch")
        if not delivery.get("delivery_key", "").startswith("manual:morning:independent-site-direct-mail:"):
            errors.append("today_radar delivery_key mismatch")
        if not delivery.get("state_files", {}).get("runs_dir"):
            errors.append("today_radar state_files.runs_dir missing")

    if published.returncode != 0:
        errors.append(f"publish command failed: {published.stderr.strip() or published.stdout.strip()}")
    else:
        publish_payload = published_run.get("publish_payload")
        if not isinstance(publish_payload, dict):
            errors.append("today_radar --publish should write unified publish_payload into published_run.json")
        else:
            if not isinstance(publish_payload.get("macro_events"), list):
                errors.append("publish_payload should include macro_events list")
            if not isinstance(publish_payload.get("urgent_events"), list):
                errors.append("publish_payload should include urgent_events list")
            if not isinstance(publish_payload.get("daily_events"), list):
                errors.append("publish_payload should include daily_events list")
            if not isinstance(publish_payload.get("events"), list):
                errors.append("publish_payload should include flattened events list")

    if errors:
        print("FAIL validate_today_radar_entry")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_today_radar_entry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
