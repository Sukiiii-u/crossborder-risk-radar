#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"


def run_brief(profile=None, human: bool = False, env: dict | None = None):
    cmd = [sys.executable, str(SCRIPT)]
    if profile is not None:
        if isinstance(profile, str):
            cmd.append(profile)
        else:
            cmd.append(json.dumps(profile, ensure_ascii=False))
    if human:
        cmd.append("--human")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout if human else json.loads(proc.stdout)


def main() -> int:
    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        real_events = runtime_root / "data" / "real_events.json"
        real_events.parent.mkdir(parents=True, exist_ok=True)
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))
        real_events.write_text(
            json.dumps({"generated_at": "test", "event_count": 0, "events": [], "failures": []}, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        result = run_brief("tiktok direct-mail", env=env)
        human_output = run_brief("tiktok direct-mail", human=True, env=env)
        generic_default = run_brief(env=env)
        generic_default_human = run_brief(human=True, env=env)
        amazon_fba = run_brief("amazon-fba", env=env)
        independent_site = run_brief("independent-site-direct-mail", env=env)

    errors = []

    if generic_default.get("brief_type") != "morning_radar_general":
        errors.append("default brief_type should be morning_radar_general")
    if generic_default.get("radar_mode") != "general_event_view":
        errors.append("default radar_mode should be general_event_view")
    if not generic_default.get("dashboard"):
        errors.append("default brief should expose dashboard summary data")
    if generic_default.get("profile_preset") is not None:
        errors.append("default brief should not silently resolve to amazon-fba preset")
    if "Amazon FBA" in generic_default.get("profile_label", "") or generic_default.get("seller_profile", {}).get("fulfillment_model") == "fba":
        errors.append("default brief should not render as amazon fba default profile")
    if "默认首页" not in generic_default.get("overall_takeaway", ""):
        errors.append("default brief takeaway should describe general homepage mode")
    if "首页模式：Dashboard 首页" not in generic_default_human:
        errors.append("default human output should render dashboard homepage header")
    if "## Dashboard 总览" not in generic_default_human or "## 事件卡片" not in generic_default_human:
        errors.append("default human output should render dashboard summary + event cards")

    if result.get("brief_type") != "morning_radar_demo":
        errors.append("brief_type mismatch")
    if result.get("profile_preset") != "tiktok-direct-mail":
        errors.append("profile preset alias did not resolve to tiktok-direct-mail")
    if result.get("event_count", 0) < 3:
        errors.append("expected at least 3 events")
    if not result.get("overall_takeaway"):
        errors.append("overall_takeaway missing")
    if not result.get("overview"):
        errors.append("overview missing")
    if not result.get("fulfillment_actions"):
        errors.append("fulfillment_actions missing")
    if not result.get("today_actions"):
        errors.append("today_actions missing")
    if not result.get("key_signal"):
        errors.append("key_signal missing")
    if not result.get("priority_lens"):
        errors.append("priority_lens missing")

    overview = result.get("overview", {})
    if "今天先盯" not in overview.get("headline", ""):
        errors.append("overview headline missing layered summary phrasing")
    if "platform=" not in overview.get("why_it_matters", ""):
        errors.append("overview should explain platform as modifier, not first layer")
    if result.get("profile_label", "").startswith(("Amazon", "TikTok", "独立站")):
        errors.append("profile label should be fulfillment-first instead of platform-first")

    if generic_default.get("profile_preset") is not None:
        errors.append("default no-profile entry should not resolve to a preset")
    if generic_default.get("profile_label") != "通用雷达首页（事件驱动 / 不绑定默认画像）":
        errors.append("default no-profile entry should render generic homepage label")
    if generic_default.get("seller_profile", {}).get("platform") != "general":
        errors.append("default no-profile entry should stay generic instead of falling back to amazon")
    if "Amazon / 市场：德国站" in generic_default.get("overall_takeaway", ""):
        errors.append("default no-profile takeaway should not leak amazon-fba wording")
    if "展示标签：通用雷达首页（事件驱动 / 不绑定默认画像）" not in generic_default_human:
        errors.append("default no-profile human output should show generic homepage label")
    if "平台范围：全平台扫描" not in generic_default_human:
        errors.append("default no-profile human output should show generic platform range")
    if "## 事件卡片" not in generic_default_human or "### 卡片 1｜" not in generic_default_human:
        errors.append("default no-profile human output should show dashboard card layout")
    if "本地履约-平台主导（平台修正：Amazon / 市场：德国站）" in generic_default_human:
        errors.append("default no-profile human output should not show amazon-fba as the default angle")

    fulfillment_actions = result.get("fulfillment_actions", [])
    expected_paths = ["跨境直发", "本地履约-平台主导", "本地履约-3PL/商家主导"]
    path_labels = [item.get("path_label") for item in fulfillment_actions]
    for label in expected_paths:
        if label not in path_labels:
            errors.append(f"missing fulfillment path section: {label}")
    if len({tuple(item.get("actions", [])) for item in fulfillment_actions}) != len(fulfillment_actions):
        errors.append("each fulfillment path should have distinct action sets")

    events = result.get("events", [])
    if not any(event.get("event_type") == "tariff" for event in events):
        errors.append("missing tariff event")
    if not any(event.get("event_type") == "environment" for event in events):
        errors.append("missing environment event")
    if not any(event.get("event_type") == "logistics" for event in events):
        errors.append("missing logistics event")
    if len({event.get("primary_topic") for event in events}) != len(events):
        errors.append("top events should prefer topic diversity")
    scores = [event.get("ranking_score", 0) for event in events]
    if scores != sorted(scores, reverse=True):
        errors.append("events are not sorted by ranking_score descending")
    tariff_event = next((event for event in events if event.get("event_type") == "tariff"), None)
    if not tariff_event:
        errors.append("expected tariff event for applicability layering checks")
    else:
        applicability = tariff_event.get("applicability_layers", {})
        if applicability.get("current_view", {}).get("label") != "高相关":
            errors.append("tiktok direct-mail tariff event should render current view as 高相关")
        if not applicability.get("high_relevance") or not applicability.get("medium_relevance") or not applicability.get("low_relevance_or_watch"):
            errors.append("event applicability layers should include high/medium/low buckets")

    if "# 今日跨境风险晨报" not in human_output:
        errors.append("human output missing morning brief title")
    if "履约主视角：跨境直发" not in human_output:
        errors.append("human output should start from fulfillment-first main label")
    if "平台修正：TikTok Shop" not in human_output:
        errors.append("human output should keep platform only as modifier")
    if "- 适用性分层：" not in human_output or "  - 高相关是谁：" not in human_output or "  - 中相关是谁：" not in human_output or "  - 低相关/观察是谁：" not in human_output:
        errors.append("human output should render applicability layering inside each event")
    if "- 各层该做什么：" not in human_output or "  - 高相关：" not in human_output or "  - 中相关：" not in human_output or "  - 低相关/观察：" not in human_output:
        errors.append("human output should render layered actions inside each event")
    expected_sections = [
        "## 总览判断",
        "## 分履约动作",
        "## 重点事件",
        "## 优先级解释",
        "## 今日先做",
        "## 继续观察",
        "## 暂缓动作",
        "## 一句话结论",
    ]
    for section in expected_sections:
        if section not in human_output:
            errors.append(f"human output missing section: {section}")
    if "### 履约路径｜跨境直发" not in human_output or "### 履约路径｜本地履约-平台主导" not in human_output or "### 履约路径｜本地履约-3PL/商家主导" not in human_output:
        errors.append("human output missing required fulfillment path headings")

    ordered_markers = [
        "## 总览判断",
        "## 分履约动作",
        "## 重点事件",
        "## 优先级解释",
        "## 今日先做",
        "## 继续观察",
        "## 暂缓动作",
        "## 一句话结论",
    ]
    positions = [human_output.find(marker) for marker in ordered_markers]
    if any(position == -1 for position in positions) or positions != sorted(positions):
        errors.append("human output sections are out of order")

    if amazon_fba.get("overall_takeaway") == independent_site.get("overall_takeaway"):
        errors.append("different profiles should produce different overall takeaway")
    if amazon_fba.get("today_actions", [None])[0] == independent_site.get("today_actions", [None])[0]:
        errors.append("different profiles should produce different priority actions")

    if errors:
        print("FAIL validate_morning_brief")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_morning_brief")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
