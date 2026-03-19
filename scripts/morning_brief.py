#!/usr/bin/env python3
"""跨境风险雷达晨报主编排模块。

拆分后的模块结构：
- morning_brief_constants.py  — 常量定义
- profile_resolver.py         — 画像解析
- event_scorer.py              — 评分排序引擎
- applicability.py             — 适用性分层
- brief_builder.py             — 摘要/概览生成
- brief_renderer.py            — 文本渲染输出
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from analyze_event import normalize_output, build_output  # noqa: E402
from runtime_paths import REAL_EVENTS_FILE, ensure_runtime_data_dir  # noqa: E402
from zh_localization import localize_summary, localize_title, looks_chinese  # noqa: E402

from morning_brief_constants import (  # noqa: E402, F401
    DEFAULT_PROFILE,
    EXAMPLES_DIR,
    FULFILLMENT_PATHS,
    GENERAL_RADAR_PROFILE,
    MAX_REAL_SNAPSHOT_AGE_HOURS,
    PRESET_ALIASES,
    PROFILE_LABELS,
    PROFILE_PRESETS,
    SEED_FILE,
)
from profile_resolver import (  # noqa: E402, F401
    canonicalize_profile_key,
    is_general_radar_profile,
    merge_profile,
    profile_display_name,
    profile_focus,
    resolve_profile_input,
    resolve_profile_inputs,
)
from event_scorer import (  # noqa: E402, F401
    content_signal_adjustment,
    rank_and_select_events,
    score_event,
    source_strength,
    time_decay_bonus,
)
from applicability import (  # noqa: E402, F401
    applicability_label_for_path,
    applicability_level_for_path,
    applicability_tier_label,
    build_applicability_layers,
    build_fulfillment_actions,
    build_layer_actions,
    fulfillment_path_key,
    fulfillment_path_label,
    normalize_fulfillment_path,
    platform_modifier_label,
)
from brief_builder import (  # noqa: E402, F401
    build_dashboard_summary,
    build_key_signal,
    build_overall_takeaway,
    build_overview,
    build_priority_lens,
    build_risk_type_distribution,
    collect_hold_line,
    collect_today_actions,
    collect_watch_items,
    event_impact_line,
    event_seller_angle,
    parse_datetime,
    urgency_from_result,
)
from brief_renderer import (  # noqa: E402, F401
    format_event,
    render_human_brief,
    render_single_human_brief,
)


def load_seed(name: str) -> dict:
    return json.loads((EXAMPLES_DIR / name).read_text(encoding="utf-8"))


def load_seed_configs() -> list[dict]:
    return json.loads(SEED_FILE.read_text(encoding="utf-8"))


def load_real_events() -> list[dict]:
    ensure_runtime_data_dir()
    if not REAL_EVENTS_FILE.exists():
        return []
    try:
        payload = json.loads(REAL_EVENTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    events = payload.get("events") if isinstance(payload, dict) else None
    if not isinstance(events, list):
        return []
    return [event for event in events if isinstance(event, dict) and str(event.get("content") or "").strip()]


def inspect_real_events_snapshot(max_age_hours: int = MAX_REAL_SNAPSHOT_AGE_HOURS) -> dict[str, Any]:
    ensure_runtime_data_dir()
    status: dict[str, Any] = {
        "file": str(REAL_EVENTS_FILE),
        "exists": REAL_EVENTS_FILE.exists(),
        "has_events": False,
        "generated_at": None,
        "age_hours": None,
        "max_age_hours": max_age_hours,
        "usable": False,
        "reason": "missing",
    }
    if not REAL_EVENTS_FILE.exists():
        return status

    try:
        payload = json.loads(REAL_EVENTS_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        status["reason"] = "invalid_json"
        return status

    events = payload.get("events") if isinstance(payload, dict) else None
    if not isinstance(events, list) or not events:
        status["reason"] = "empty"
        return status

    status["has_events"] = True
    generated_at = parse_datetime(payload.get("generated_at"))
    if generated_at is None:
        event_times = [
            parse_datetime(event.get("fetched_at")) or parse_datetime(event.get("published_at"))
            for event in events
            if isinstance(event, dict)
        ]
        event_times = [value for value in event_times if value is not None]
        generated_at = max(event_times) if event_times else None

    if generated_at is None:
        status["reason"] = "unknown_age"
        return status

    now = datetime.now(timezone.utc)
    age_hours = max((now - generated_at).total_seconds() / 3600, 0.0)
    status["generated_at"] = generated_at.isoformat()
    status["age_hours"] = round(age_hours, 1)
    if age_hours <= max_age_hours:
        status["usable"] = True
        status["reason"] = "fresh"
    else:
        status["reason"] = "stale"
    return status


def enrich_result(result: dict, source_mode: str, sequence: int) -> dict:
    enriched = dict(result)
    enriched["brief_source_mode"] = source_mode
    enriched["source_theme"] = enriched.get("event_type") or enriched.get("source_topic") or "policy"
    enriched["unique_key"] = enriched.get("event_title") or enriched.get("seed_id") or f"event-{sequence}"
    return enriched


def build_seed_results(profile: dict) -> list[dict]:
    results = []
    for index, seed_config in enumerate(load_seed_configs(), start=1):
        seed = load_seed(seed_config["example_file"])
        merged = merge_profile(seed, profile)
        result = normalize_output(build_output(merged))
        result["seed_id"] = seed_config["id"]
        result["seed_label"] = seed_config["label"]
        result["source_topic"] = result.get("event_type")
        if result.get("is_relevant"):
            results.append(enrich_result(result, "seed", index))
    return results


def build_real_event_results(profile: dict) -> list[dict]:
    results = []
    for index, event in enumerate(load_real_events(), start=1):
        merged = merge_profile({
            "content": event.get("content", ""),
            "url": event.get("url"),
        }, profile)
        result = normalize_output(build_output(merged))
        result["real_event_index"] = index
        result["source_id"] = event.get("source_id")
        result["source_label"] = event.get("source_label")
        result["source_topic"] = event.get("source_topic")
        result["source_platforms"] = event.get("source_platforms") or []
        result["source_trust_tier"] = event.get("source_trust_tier")
        result["source_seller_signal_bias"] = event.get("source_seller_signal_bias")
        result["source_priority"] = event.get("source_priority")
        result["source_type"] = event.get("source_type")
        result["source_layer"] = event.get("source_layer")
        result["source_display_zh"] = event.get("source_display_zh")
        result["source_business_zone"] = event.get("source_business_zone") or []
        result["source_why_it_matters"] = event.get("source_why_it_matters")
        result["watchlist_id"] = event.get("watchlist_id")
        result["published_at"] = event.get("published_at")
        result["fetched_at"] = event.get("fetched_at")
        raw_title = str(event.get("raw_title") or event.get("title") or "").strip()
        raw_content = str(event.get("raw_content") or event.get("content") or "").strip()
        source_label = str(event.get("source_label") or "")
        source_topic = str(event.get("source_topic") or "")
        if raw_title:
            result["raw_event_title"] = raw_title
        localized_title = str(event.get("zh_title") or "").strip()
        if not localized_title:
            existing_title = str(result.get("event_title") or "").strip()
            localized_title = localize_title(raw_title or existing_title, source_label)

        localized_summary = str(event.get("zh_summary") or "").strip()
        if not localized_summary:
            existing_summary = str(result.get("event_summary") or "").strip()
            localized_summary = existing_summary if looks_chinese(existing_summary) else localize_summary(
                raw_title or str(result.get("event_title") or ""),
                raw_content or existing_summary,
                source_label,
                source_topic,
            )
        if localized_title:
            result["event_title"] = localized_title
        if localized_summary:
            result["event_summary"] = localized_summary
        if event.get("url"):
            result["sources"] = [{"name": event.get("source_label") or "real-event", "url": event["url"]}]
        if result.get("is_relevant"):
            results.append(enrich_result(result, "real", index))
    return results


def build_single_brief(profile: dict, preset_name: str | None, use_real_events: bool = True) -> dict:
    results = build_real_event_results(profile) if use_real_events else []
    source_mode = "real" if results else "seed"
    if not results:
        results = build_seed_results(profile)

    ranked_events = rank_and_select_events(results, profile)
    overview = build_overview(profile, ranked_events, source_mode)
    fulfillment_actions = build_fulfillment_actions(ranked_events, profile)
    general_mode = is_general_radar_profile(profile, preset_name)

    brief = {
        "brief_type": "morning_radar_general" if general_mode else "morning_radar_demo",
        "radar_mode": "general_event_view" if general_mode else "profile_view",
        "profile_preset": preset_name,
        "profile_label": profile_display_name(profile, preset_name),
        "event_count": len(ranked_events),
        "seller_profile": profile,
        "profile_focus": profile_focus(profile),
        "key_signal": build_key_signal(ranked_events),
        "priority_lens": build_priority_lens(ranked_events),
        "overall_takeaway": build_overall_takeaway(profile, ranked_events, source_mode),
        "overview": overview,
        "fulfillment_actions": fulfillment_actions,
        "today_actions": collect_today_actions(ranked_events),
        "watch_items": collect_watch_items(ranked_events),
        "hold_line": collect_hold_line(profile),
        "events": ranked_events,
    }
    if general_mode:
        brief["dashboard"] = build_dashboard_summary(brief)
    return brief


def build_brief(profile_input: Any = None, use_real_events: bool = True) -> dict:
    resolved_profiles = resolve_profile_inputs(profile_input)
    views = [build_single_brief(profile, preset_name, use_real_events=use_real_events) for profile, preset_name in resolved_profiles]

    if len(views) == 1:
        return views[0]

    profile_labels = [view.get("profile_label", "未命名画像") for view in views]
    return {
        "brief_type": "morning_radar_multi_view",
        "view_count": len(views),
        "profile_labels": profile_labels,
        "profile_label": " / ".join(profile_labels),
        "overall_takeaway": f"今天按 {len(views)} 条履约路径拆开看，平台只做修正标签，别再把平台名当第一层视角。",
        "views": views,
    }


def read_input() -> Any:
    args = [arg for arg in sys.argv[1:] if arg != "--human"]
    if not args:
        return None

    arg = args[0]
    path = Path(arg)
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))

    try:
        return json.loads(arg)
    except json.JSONDecodeError:
        return arg


def main() -> None:
    profile_input = read_input()
    brief = build_brief(profile_input)
    if "--human" in sys.argv:
        print(render_human_brief(brief))
    else:
        print(json.dumps(brief, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
