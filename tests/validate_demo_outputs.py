#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
INPUT_DIR = SKILL_ROOT / "examples"
STUB = SKILL_ROOT / "scripts" / "analyze_event.py"

EXPECTATIONS = {
    "demo_01_tariff_us.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "US",
        "risk_level_in": ["medium", "high"],
        "confidence_in": ["medium", "high"],
        "sources_non_empty": True,
    },
    "demo_02_eu_packaging.json": {
        "is_relevant": True,
        "event_type": "environment",
        "region": "EU",
        "sources_non_empty": True,
    },
    "demo_03_tariff_rumor.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "US",
        "confidence_in": ["low"],
        "risk_level_in": ["medium"],
    },
    "demo_04_port_vote.json": {
        "is_relevant": True,
        "event_type": "logistics",
        "confidence_in": ["low"],
        "risk_level_in": ["medium"],
    },
    "demo_05_generic_policy.json": {
        "is_relevant": False,
        "event_type": "policy",
        "risk_level_in": ["low"],
        "confidence_in": ["low"],
    },
    "demo_06_brand_packaging_pr.json": {
        "is_relevant": False,
        "event_type": "environment",
        "risk_level_in": ["low"],
        "confidence_in": ["low"],
    },
    "demo_07_algorithm_update.json": {
        "is_relevant": False,
        "event_type": "policy",
        "risk_level_in": ["low"],
        "confidence_in": ["low"],
    },
    "demo_08_full_object.json": {
        "is_relevant": True,
        "event_type": "environment",
        "region": "EU",
        "sources_non_empty": True,
        "affected_categories_contains": ["home"],
    },
    "demo_09_eu_small_parcel_direct_mail.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "EU",
        "risk_level_in": ["high"],
        "affected_sellers_contains": ["tiktok-shop sellers using direct-mail targeting EU", "margin-sensitive sellers"],
        "suggested_actions_contains": ["今天先复核低客单 SKU 的税后毛利率和到手利润"],
    },
    "demo_10_eu_small_parcel_overseas_warehouse.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "EU",
        "risk_level_in": ["medium", "high"],
        "affected_sellers_contains": ["amazon sellers using overseas-warehouse targeting DE"],
        "suggested_actions_contains": ["今天先把海外仓现货和在途补货拆开看，确认哪批货还能继续扛住税费波动"],
    },
    "demo_11_eu_small_parcel_fba.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "EU",
        "risk_level_in": ["medium", "high"],
        "affected_sellers_contains": ["amazon sellers using fba targeting DE"],
        "suggested_actions_contains": ["今天先把 EU 站内主力 SKU 的到手价和 FBA 成本重算一遍，确认还有没有安全垫"],
    },
    "demo_12_eu_small_parcel_independent_site.json": {
        "is_relevant": True,
        "event_type": "tariff",
        "region": "EU",
        "risk_level_in": ["high"],
        "affected_sellers_contains": ["independent-site sellers using direct-mail targeting EU", "margin-sensitive sellers"],
        "suggested_actions_contains": ["今天先盘点 EU 直邮订单占比和最脆弱的低毛利 SKU"],
    },
}


def run_stub(input_path: Path) -> dict:
    proc = subprocess.run(
        [sys.executable, str(STUB), str(input_path)],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"stub failed for {input_path.name}: {proc.stderr.strip()}")
    return json.loads(proc.stdout)


def check_expectations(name: str, result: dict) -> list[str]:
    exp = EXPECTATIONS[name]
    errors: list[str] = []

    for field in ["is_relevant", "event_type", "region"]:
        if field in exp and result.get(field) != exp[field]:
            errors.append(f"{field} expected {exp[field]!r}, got {result.get(field)!r}")

    if "risk_level_in" in exp and result.get("risk_level") not in exp["risk_level_in"]:
        errors.append(f"risk_level expected one of {exp['risk_level_in']}, got {result.get('risk_level')!r}")

    if "confidence_in" in exp and result.get("confidence") not in exp["confidence_in"]:
        errors.append(f"confidence expected one of {exp['confidence_in']}, got {result.get('confidence')!r}")

    if exp.get("sources_non_empty") and not result.get("sources"):
        errors.append("sources expected non-empty")

    if "affected_categories_contains" in exp:
        categories = result.get("affected_categories", [])
        for item in exp["affected_categories_contains"]:
            if item not in categories:
                errors.append(f"affected_categories missing {item!r}")

    if "affected_sellers_contains" in exp:
        sellers = result.get("affected_sellers", [])
        for item in exp["affected_sellers_contains"]:
            if item not in sellers:
                errors.append(f"affected_sellers missing {item!r}")

    if "suggested_actions_contains" in exp:
        actions = result.get("suggested_actions", [])
        for item in exp["suggested_actions_contains"]:
            if item not in actions:
                errors.append(f"suggested_actions missing {item!r}")

    return errors


def main() -> int:
    failures = []
    total = 0
    collected_results = {}

    for name in sorted(EXPECTATIONS):
        total += 1
        input_path = INPUT_DIR / name
        try:
            result = run_stub(input_path)
            collected_results[name] = result
            errors = check_expectations(name, result)
            if errors:
                failures.append((name, errors))
                print(f"FAIL {name}")
                for err in errors:
                    print(f"  - {err}")
            else:
                print(f"PASS {name}")
        except Exception as exc:
            failures.append((name, [str(exc)]))
            print(f"FAIL {name}")
            print(f"  - {exc}")

    total += 1
    profile_diff_errors = []
    fba = collected_results.get("demo_11_eu_small_parcel_fba.json", {})
    warehouse = collected_results.get("demo_10_eu_small_parcel_overseas_warehouse.json", {})
    if fba.get("suggested_actions", [None])[0] == warehouse.get("suggested_actions", [None])[0]:
        profile_diff_errors.append("demo_10 vs demo_11 should not share the same first tariff action")
    if profile_diff_errors:
        failures.append(("profile-diff-checks", profile_diff_errors))
        print("FAIL profile-diff-checks")
        for err in profile_diff_errors:
            print(f"  - {err}")
    else:
        print("PASS profile-diff-checks")
        total += 1

    print(f"\nSummary: {total - len(failures)}/{total} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
