#!/usr/bin/env python3
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
ANALYZE_SCRIPT = SKILL_ROOT / "scripts" / "analyze_event.py"
BRIEF_SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"

PROFILE_PRESETS = [
    "amazon-fba",
    "overseas-warehouse",
    "tiktok-direct-mail",
    "independent-site-direct-mail",
]

PROFILE_INPUTS = {
    "amazon-fba": {
        "platform": "amazon",
        "fulfillment_model": "fba",
        "market": "DE",
        "price_band": "medium",
        "category": "general",
        "risk_profile": "general",
    },
    "overseas-warehouse": {
        "platform": "amazon",
        "fulfillment_model": "overseas-warehouse",
        "market": "DE",
        "price_band": "medium",
        "category": "home",
        "risk_profile": "general",
    },
    "tiktok-direct-mail": {
        "platform": "tiktok-shop",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    },
    "independent-site-direct-mail": {
        "platform": "independent-site",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    },
}

TARIFF_EVENT = {
    "content": "欧盟正在讨论取消低价值包裹免税，并对直邮小包加征税费，这会直接抬高跨境卖家的成本和定价压力。",
    "url": "https://example.com/tariff",
}


def run_json_script(script: Path, payload=None, human: bool = False, env: dict | None = None):
    cmd = [sys.executable, str(script)]
    if payload is not None:
        if isinstance(payload, str):
            cmd.append(payload)
        else:
            cmd.append(json.dumps(payload, ensure_ascii=False))
    if human:
        cmd.append("--human")
    proc = subprocess.run(cmd, capture_output=True, text=True, check=False, env=env)
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    return proc.stdout if human else json.loads(proc.stdout)


def run_analyze(profile_preset: str) -> dict:
    payload = dict(TARIFF_EVENT)
    payload["seller_profile"] = dict(PROFILE_INPUTS[profile_preset])
    return run_json_script(ANALYZE_SCRIPT, payload)


def run_brief(profile_preset: str, env: dict[str, str]):
    return run_json_script(BRIEF_SCRIPT, profile_preset, env=env), run_json_script(BRIEF_SCRIPT, profile_preset, human=True, env=env)


def validate_analyze_event() -> list[str]:
    errors: list[str] = []
    results = {preset: run_analyze(preset) for preset in PROFILE_PRESETS}

    expected_actions = {
        "amazon-fba": "今天先把 EU 站内主力 SKU 的到手价和 FBA 成本重算一遍，确认还有没有安全垫",
        "overseas-warehouse": "今天先把海外仓现货和在途补货拆开看，确认哪批货还能继续扛住税费波动",
        "tiktok-direct-mail": "今天先复核低客单 SKU 的税后毛利率和到手利润",
        "independent-site-direct-mail": "今天先盘点 EU 直邮订单占比和最脆弱的低毛利 SKU",
    }

    for preset, result in results.items():
        if result.get("event_type") != "tariff":
            errors.append(f"{preset}: expected tariff event_type")
        if result.get("region") != "EU":
            errors.append(f"{preset}: expected EU region")
        if not result.get("is_relevant"):
            errors.append(f"{preset}: expected relevant tariff event")
        if expected_actions[preset] not in result.get("suggested_actions", []):
            errors.append(f"{preset}: missing profile-specific action")

    if results["amazon-fba"].get("risk_level") == results["tiktok-direct-mail"].get("risk_level"):
        errors.append("analyze_event: amazon-fba and tiktok-direct-mail should not share the same tariff risk level")

    if results["tiktok-direct-mail"].get("suggested_actions") == results["independent-site-direct-mail"].get("suggested_actions"):
        errors.append("analyze_event: tiktok-direct-mail and independent-site-direct-mail should not have identical tariff actions")

    if results["amazon-fba"].get("affected_sellers") == results["overseas-warehouse"].get("affected_sellers"):
        errors.append("analyze_event: amazon-fba and overseas-warehouse should identify different affected sellers")
    if results["amazon-fba"].get("suggested_actions", [None])[0] == results["overseas-warehouse"].get("suggested_actions", [None])[0]:
        errors.append("analyze_event: amazon-fba and overseas-warehouse should not share the same tariff first action")

    us_profile_payload = {
        "content": TARIFF_EVENT["content"],
        "url": "https://example.com/tariff-us-market",
        "seller_profile": {
            "platform": "amazon",
            "fulfillment_model": "direct-mail",
            "market": "US",
            "price_band": "low",
            "category": "general",
            "risk_profile": "margin-sensitive",
        },
    }
    us_profile_result = run_json_script(ANALYZE_SCRIPT, us_profile_payload)
    if us_profile_result.get("risk_level") != "low":
        errors.append("analyze_event: EU small-parcel tariff should not stay high priority for non-Europe market profiles")
    if not any("区域性风险信号" in action for action in us_profile_result.get("suggested_actions", [])):
        errors.append("analyze_event: non-Europe market profile should receive downgraded regional watch actions")

    if results["tiktok-direct-mail"].get("risk_level") != "high":
        errors.append("analyze_event: EU direct-mail profile should remain high priority for EU small-parcel tariff")
    if results["amazon-fba"].get("risk_level") != "medium":
        errors.append("analyze_event: EU FBA profile should be downgraded below direct-mail for EU small-parcel tariff")

    return errors


def validate_morning_brief(env: dict[str, str], real_events: Path) -> list[str]:
    errors: list[str] = []
    real_events.parent.mkdir(parents=True, exist_ok=True)
    real_events.write_text(
        json.dumps({"generated_at": "test", "event_count": 0, "events": [], "failures": []}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    briefs = {}
    human_outputs = {}
    for preset in PROFILE_PRESETS:
        brief, human_output = run_brief(preset, env)
        briefs[preset] = brief
        human_outputs[preset] = human_output

    expected_takeaway_snippets = {
        "amazon-fba": "FBA 定价、补货和尾程成本",
        "overseas-warehouse": "海外仓的对冲优势",
        "tiktok-direct-mail": "EU 直邮利润、税后售价和履约稳定性",
        "independent-site-direct-mail": "独立站直邮模型被税费和退件联手偷利润",
    }
    expected_focus_snippets = {
        "amazon-fba": "仓内履约",
        "overseas-warehouse": "仓内履约",
        "tiktok-direct-mail": "先盯毛利",
        "independent-site-direct-mail": "到手价、运费模板和退件链路",
    }
    expected_today_action = {
        "amazon-fba": "今天先把 EU 站内主力 SKU 的到手价和 FBA 成本重算一遍，确认还有没有安全垫",
        "overseas-warehouse": "今天先把海外仓现货和在途补货拆开看，确认哪批货还能继续扛住税费波动",
        "tiktok-direct-mail": "今天先复核低客单 SKU 的税后毛利率和到手利润",
        "independent-site-direct-mail": "今天先盘点 EU 直邮订单占比和最脆弱的低毛利 SKU",
    }

    for preset, brief in briefs.items():
        if brief.get("event_count", 0) < 3:
            errors.append(f"{preset}: expected at least 3 seed events")
        if expected_takeaway_snippets[preset] not in brief.get("overall_takeaway", ""):
            errors.append(f"{preset}: overall_takeaway missing profile-specific language")
        if expected_focus_snippets[preset] not in brief.get("profile_focus", ""):
            errors.append(f"{preset}: profile_focus missing profile-specific language")
        if expected_today_action[preset] not in brief.get("today_actions", []):
            errors.append(f"{preset}: today_actions missing tariff-first profile action")
        if brief.get("watch_items", [None])[0] == brief.get("today_actions", [None])[0]:
            errors.append(f"{preset}: today_actions and watch_items should not collapse to the same first item")
        if brief.get("overall_takeaway") not in human_outputs[preset]:
            errors.append(f"{preset}: human output missing takeaway echo")
        if not brief.get("overview") or not brief.get("fulfillment_actions"):
            errors.append(f"{preset}: layered structure missing")
        if len(brief.get("fulfillment_actions", [])) < 3:
            errors.append(f"{preset}: fulfillment_actions should cover at least 3 paths")
        path_labels = [item.get("path_label") for item in brief.get("fulfillment_actions", [])]
        for label in ["跨境直发", "本地履约-平台主导", "本地履约-3PL/商家主导"]:
            if label not in path_labels:
                errors.append(f"{preset}: missing fulfillment path {label}")
        actions_by_path = [tuple(item.get("actions", [])) for item in brief.get("fulfillment_actions", [])]
        if len(set(actions_by_path)) != len(actions_by_path):
            errors.append(f"{preset}: fulfillment paths should not share identical action lists")

    if briefs["amazon-fba"].get("overall_takeaway") == briefs["overseas-warehouse"].get("overall_takeaway"):
        errors.append("morning_brief: amazon-fba and overseas-warehouse should have different one-line takeaways")
    if briefs["tiktok-direct-mail"].get("today_actions") == briefs["independent-site-direct-mail"].get("today_actions"):
        errors.append("morning_brief: tiktok-direct-mail and independent-site-direct-mail should not have identical today actions")
    if briefs["amazon-fba"].get("profile_focus") == briefs["tiktok-direct-mail"].get("profile_focus"):
        errors.append("morning_brief: amazon-fba and tiktok-direct-mail should have different key reminders")
    if briefs["amazon-fba"].get("fulfillment_actions") == briefs["tiktok-direct-mail"].get("fulfillment_actions"):
        errors.append("morning_brief: fulfillment actions should still be profile-modified across different seller views")

    return errors


def main() -> int:
    failures = []

    analyze_errors = validate_analyze_event()
    if analyze_errors:
        failures.extend([f"analyze_event: {err}" for err in analyze_errors])

    with tempfile.TemporaryDirectory() as runtime_tmp:
        runtime_root = Path(runtime_tmp)
        env = dict(os.environ, CROSSBORDER_RADAR_RUNTIME_DIR=str(runtime_root))
        real_events = runtime_root / "data" / "real_events.json"
        brief_errors = validate_morning_brief(env, real_events)
        if brief_errors:
            failures.extend([f"morning_brief: {err}" for err in brief_errors])

    if failures:
        print("FAIL validate_seller_profile_regressions")
        for err in failures:
            print(f"- {err}")
        return 1

    print("PASS validate_seller_profile_regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
