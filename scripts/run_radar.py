#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from audit_summary import load_audit, render_human_summary  # noqa: E402
from morning_brief import build_brief, inspect_real_events_snapshot, render_human_brief  # noqa: E402
from radar_state import persist_run  # noqa: E402
from today_radar import build_profile_input  # noqa: E402

MODE_ALIASES = {
    "am": "morning",
    "morning": "morning",
    "pm": "evening",
    "evening": "evening",
    "night": "evening",
}

SOURCE_MODES = {"auto", "seed"}
OUTPUT_FORMATS = {"human", "json"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Non-interactive radar runner for future scheduled delivery. "
            "Supports explicit mode/profile/source selection and optional file output."
        )
    )
    parser.add_argument("profile", nargs="?", help="Optional profile preset or alias, such as tiktok / amazon / independent-site")
    parser.add_argument("--preset", help="Explicit preset or alias")
    parser.add_argument("--platform")
    parser.add_argument("--fulfillment-model")
    parser.add_argument("--market")
    parser.add_argument("--price-band")
    parser.add_argument("--category")
    parser.add_argument("--risk-profile")
    parser.add_argument("--mode", default="morning", help="Delivery mode: morning / evening (default: morning)")
    parser.add_argument(
        "--source",
        default="auto",
        help="Event source mode: auto (prefer real snapshot, fallback seed) / seed (force demo seed)",
    )
    parser.add_argument("--format", default="human", help="Output format: human / json (default: human)")
    parser.add_argument("--output", help="Write final payload to a file instead of stdout")
    parser.add_argument("--audit-summary", action="store_true", help="Attach fetch audit summary to the final output when available")
    return parser.parse_args()


def load_audit_attachment() -> dict | None:
    try:
        return load_audit()
    except Exception:
        return None


def canonical_mode(raw: str) -> str:
    lowered = raw.strip().lower()
    mode = MODE_ALIASES.get(lowered)
    if not mode:
        raise ValueError(f"unknown mode: {raw}")
    return mode


def canonical_source(raw: str) -> str:
    lowered = raw.strip().lower()
    if lowered not in SOURCE_MODES:
        raise ValueError(f"unknown source mode: {raw}")
    return lowered


def canonical_output_format(raw: str) -> str:
    lowered = raw.strip().lower()
    if lowered not in OUTPUT_FORMATS:
        raise ValueError(f"unknown output format: {raw}")
    return lowered


def build_delivery_payload(args: argparse.Namespace) -> dict:
    mode = canonical_mode(args.mode)
    source = canonical_source(args.source)
    output_format = canonical_output_format(args.format)
    trigger = "scheduled"

    snapshot_status = inspect_real_events_snapshot()
    use_real_events = source != "seed" and snapshot_status.get("usable", False)

    profile_input = build_profile_input(args)
    if source == "seed":
        profile_input = profile_input or None
    brief = build_brief(profile_input, use_real_events=use_real_events)

    brief["delivery_mode"] = mode
    brief["runner"] = "run_radar.py"
    brief["requested_source_mode"] = source
    brief["trigger"] = trigger
    brief["real_event_snapshot"] = snapshot_status
    if args.audit_summary:
        audit_payload = load_audit_attachment()
        if audit_payload is not None:
            brief["audit_summary"] = audit_payload

    rendered = json.dumps(brief, ensure_ascii=False, indent=2) if output_format == "json" else render_human_brief(brief)
    run_meta = persist_run(
        mode=mode,
        source=source,
        output_format=output_format,
        trigger=trigger,
        runner="run_radar.py",
        brief=brief,
        rendered=rendered,
        output_path=args.output,
    )
    brief["delivery_metadata"] = run_meta
    if output_format == "json":
        rendered = json.dumps(brief, ensure_ascii=False, indent=2)
    else:
        rendered = render_human_brief(brief)
        if brief.get("audit_summary"):
            rendered = f"{rendered}\n\n{render_human_summary(brief['audit_summary'])}"

    return {
        "mode": mode,
        "source": source,
        "format": output_format,
        "brief": brief,
        "rendered": rendered,
    }


def write_output(text: str, destination: str | None) -> None:
    if not destination or destination == "-":
        print(text)
        return

    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text + ("" if text.endswith("\n") else "\n"), encoding="utf-8")


def main() -> int:
    try:
        args = parse_args()
        payload = build_delivery_payload(args)
        write_output(payload["rendered"], args.output)
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
