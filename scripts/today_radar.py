#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from morning_brief import build_brief, inspect_real_events_snapshot, render_human_brief  # noqa: E402
from publish_guard import prepare_brief_for_publish  # noqa: E402
from radar_state import persist_run  # noqa: E402

PROFILE_SHORTCUTS = {
    "amazon": "amazon-fba",
    "fba": "amazon-fba",
    "warehouse": "overseas-warehouse",
    "overseas-warehouse": "overseas-warehouse",
    "tiktok": "tiktok-direct-mail",
    "tt": "tiktok-direct-mail",
    "independent-site": "independent-site-direct-mail",
    "indie": "independent-site-direct-mail",
    "shopify": "independent-site-direct-mail",
    "dtc": "independent-site-direct-mail",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Thin manual entry for 今日雷达：不传 preset/profile 时默认输出通用雷达首页；传入画像时仍按履约路径优先输出；可选 refresh 后渲染 human/JSON。",
    )
    parser.add_argument("profile", nargs="?", help="Preset or alias, such as tiktok / amazon / independent-site；仅作输入快捷方式，展示层会转成履约优先视角")
    parser.add_argument("--preset", action="append", help="Explicit preset or alias; repeat to build multi-view radar（输出仍按履约路径作为第一层）")
    parser.add_argument("--platform")
    parser.add_argument("--fulfillment-model")
    parser.add_argument("--market")
    parser.add_argument("--price-band")
    parser.add_argument("--category")
    parser.add_argument("--risk-profile")
    parser.add_argument("--seed-only", action="store_true", help="Ignore the latest real-event snapshot and force seed demo output")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of the default human-readable radar")
    parser.add_argument("--publish", action="store_true", help="Publish this run as the UI-facing snapshot")
    return parser.parse_args()


def canonical_profile_name(raw: str | None) -> str | None:
    if not raw:
        return None
    lowered = raw.strip().lower().replace("_", "-")
    return PROFILE_SHORTCUTS.get(lowered, raw)


def build_profile_input(args: argparse.Namespace):
    raw_presets = args.preset if isinstance(args.preset, list) else ([args.preset] if args.preset else [])
    preset_values = [canonical_profile_name(value) for value in raw_presets if canonical_profile_name(value)]

    if args.profile:
        profile = canonical_profile_name(args.profile)
        if profile:
            preset_values.insert(0, profile)

    overrides = {
        "platform": args.platform,
        "fulfillment_model": args.fulfillment_model,
        "market": args.market,
        "price_band": args.price_band,
        "category": args.category,
        "risk_profile": args.risk_profile,
    }
    overrides = {key: value for key, value in overrides.items() if value}

    if len(preset_values) > 1 and overrides:
        raise ValueError("overrides are only supported for a single profile view")

    if len(preset_values) > 1:
        return preset_values

    profile_name = preset_values[0] if preset_values else None
    if profile_name and not overrides:
        return profile_name
    if not profile_name and not overrides:
        return None

    payload = dict(overrides)
    if profile_name:
        payload["profile"] = profile_name
    return payload


def main() -> int:
    args = parse_args()
    profile_input = build_profile_input(args)

    try:
        snapshot_status = inspect_real_events_snapshot()
        use_real_events = not args.seed_only and snapshot_status.get("usable", False)
        brief = build_brief(profile_input, use_real_events=use_real_events)
        source_mode = "seed" if args.seed_only else "auto"
        brief["delivery_mode"] = "morning"
        brief["runner"] = "today_radar.py"
        brief["requested_source_mode"] = source_mode
        brief["trigger"] = "manual"
        brief["real_event_snapshot"] = snapshot_status
        if args.publish:
            brief = prepare_brief_for_publish(brief)

        rendered = json.dumps(brief, ensure_ascii=False, indent=2) if args.json else render_human_brief(brief)
        run_meta = persist_run(
            mode="morning",
            source=source_mode,
            output_format="json" if args.json else "human",
            trigger="manual",
            runner="today_radar.py",
            brief=brief,
            rendered=rendered,
            publish=args.publish,
        )
        brief["delivery_metadata"] = run_meta

        if args.json:
            print(json.dumps(brief, ensure_ascii=False, indent=2))
        else:
            print(render_human_brief(brief))
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
