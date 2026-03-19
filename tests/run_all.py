#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# These tests mutate shared runtime files such as runtime/data/real_events.json.
# Keep them in a fixed serial order to avoid cross-test interference.
TEST_ORDER = [
    "validate_source_configs.py",
    "validate_fetch_network_config.py",
    "validate_changedetection_source_config.py",
    "validate_source_registry.py",
    "validate_platform_watchlist.py",
    "validate_analyze_event.py",
    "validate_changedetection_ingest.py",
    "validate_sync_changedetection_feed.py",
    "validate_generate_launchd_templates.py",
    "validate_ingest_sources.py",
    "validate_fetch_policy_watch.py",
    "validate_refresh_radar_pipeline.py",
    "validate_seed_events.py",
    "validate_audit_summary.py",
    "validate_demo_outputs.py",
    "validate_event_scoring.py",
    "validate_ranking_regressions.py",
    "validate_real_source_pool_regressions.py",
    "validate_seller_profile_regressions.py",
    "validate_fetch_real_events.py",
    "validate_publish_guard.py",
    "validate_refresh_radar_data.py",
    "validate_morning_brief.py",
    "validate_real_event_morning_brief.py",
    "validate_today_radar_entry.py",
    "validate_run_radar.py",
    "validate_multi_profile_views.py",
    "validate_product_acceptance.py",
]


def run_test(test_file: str) -> tuple[bool, str]:
    path = ROOT / test_file
    proc = subprocess.run(
        [sys.executable, str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    output = proc.stdout.strip() or proc.stderr.strip()
    status = proc.returncode == 0
    label = "PASS" if status else "FAIL"
    print(f"{label} {test_file}")
    if output:
        print(output)
    return status, test_file


def main() -> int:
    failures: list[str] = []
    for test_file in TEST_ORDER:
        status, name = run_test(test_file)
        if not status:
            failures.append(name)

    print("")
    if failures:
        print(f"Summary: {len(TEST_ORDER) - len(failures)}/{len(TEST_ORDER)} passed")
        print(f"Failed: {', '.join(failures)}")
        return 1

    print(f"Summary: {len(TEST_ORDER)}/{len(TEST_ORDER)} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
