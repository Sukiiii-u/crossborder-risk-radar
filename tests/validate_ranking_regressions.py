#!/usr/bin/env python3
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"
REAL_EVENTS = SKILL_ROOT / "runtime" / "data" / "real_events.json"
FIXTURE = ROOT / "fixtures" / "real_events_priority_mix.json"

spec = importlib.util.spec_from_file_location("morning_brief", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def build_result(**overrides):
    base = {
        "event_title": "Test event",
        "event_summary": "Detected EU policy event that may affect cross-border seller operations.",
        "event_type": "policy",
        "risk_level": "medium",
        "confidence": "medium",
        "region": "EU",
        "source_theme": "policy",
        "brief_source_mode": "real",
        "source_id": "generic-news",
        "source_label": "Generic News",
        "published_at": "Tue, 10 Mar 2026 08:00:00 +0000",
        "fetched_at": "2026-03-10T10:00:00+00:00",
        "suggested_actions": ["先确认细则"],
        "sources": [{"name": "Generic News", "url": "https://example.com/generic"}],
        "is_relevant": True,
        "relevance_reason": "Detected seller-operational signals: seller, inventory",
        "affected_sellers": ["cross-border sellers targeting EU"],
        "affected_categories": ["general"],
        "impact_dimensions": ["cost", "inventory"],
    }
    base.update(overrides)
    return base


def main() -> int:
    errors: list[str] = []

    direct_mail_profile = {
        "platform": "tiktok-shop",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    }

    results = [
        build_result(
            event_title="EU weighs low-value parcel fee for imported packages",
            event_summary="Detected EU tariff event that may affect cross-border seller operations.",
            event_type="tariff",
            source_theme="tariff",
            source_id="reuters",
            source_label="Reuters",
            relevance_reason="Detected seller-operational signals: tariff, seller, parcel, direct-mail",
            suggested_actions=["先重算低客单直邮 SKU 的税后毛利"],
            impact_dimensions=["cost", "pricing", "inventory"],
            risk_level="high",
        ),
        build_result(
            event_title="EU packaging compliance timeline moves forward",
            event_summary="Detected EU environment event that may affect cross-border seller operations.",
            event_type="environment",
            source_theme="environment",
            source_id="commission",
            source_label="European Commission",
            relevance_reason="Detected seller-operational signals: packaging, compliance, seller",
            suggested_actions=["先核查包装与标签要求"],
            impact_dimensions=["compliance", "cost"],
            risk_level="medium",
        ),
        build_result(
            event_title="Northern Europe congestion delays seller replenishment",
            event_summary="Detected EU logistics event that may affect cross-border seller operations.",
            event_type="logistics",
            source_theme="logistics",
            source_id="freightwaves",
            source_label="FreightWaves",
            relevance_reason="Detected seller-operational signals: logistics, seller, replenishment, inventory",
            suggested_actions=["先看断货风险和补货窗口"],
            impact_dimensions=["inventory", "supply_chain"],
            risk_level="medium",
        ),
        build_result(
            event_title="How Costco and B2B importers are rethinking oil-driven delivery costs",
            event_summary="Detected logistics event that may affect enterprise import planning.",
            event_type="logistics",
            source_theme="logistics",
            source_id="generic-b2b",
            source_label="B2B Enterprise News",
            relevance_reason="Detected broad enterprise logistics discussion without clear marketplace seller action.",
            suggested_actions=["继续观察企业物流趋势"],
            impact_dimensions=["supply_chain"],
            risk_level="medium",
        ),
    ]

    ranked = module.rank_and_select_events(results, direct_mail_profile)
    titles = [item.get("event_title") for item in ranked]

    assert_true(
        titles[0] == "EU weighs low-value parcel fee for imported packages",
        "seller-operational tariff signal should stay at the top for EU direct-mail profile",
        errors,
    )
    assert_true(
        "How Costco and B2B importers are rethinking oil-driven delivery costs" not in titles,
        "macro B2B/corporate logistics story should be pushed out of top ranked events",
        errors,
    )

    parcel_event = next(item for item in ranked if item.get("event_title") == "EU weighs low-value parcel fee for imported packages")
    macro_event = next(item for item in results if item.get("event_title") == "How Costco and B2B importers are rethinking oil-driven delivery costs")
    macro_score, macro_breakdown = module.score_event(macro_event, direct_mail_profile)

    assert_true(
        parcel_event.get("ranking_score", 0) > macro_score,
        "seller-operational parcel event should outrank macro B2B logistics story by score",
        errors,
    )
    assert_true(
        macro_breakdown.get("content_signal_reason", {}).get("macro_noise_penalty", 0) > 0,
        "macro B2B logistics story should incur macro noise penalty",
        errors,
    )

    REAL_EVENTS.parent.mkdir(parents=True, exist_ok=True)
    original = REAL_EVENTS.read_text(encoding="utf-8") if REAL_EVENTS.exists() else None
    try:
        REAL_EVENTS.write_text(FIXTURE.read_text(encoding="utf-8"), encoding="utf-8")
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "tiktok-direct-mail"],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode != 0:
            errors.append(f"real fixture morning_brief run failed: {proc.stderr.strip() or proc.stdout.strip()}")
        else:
            payload = json.loads(proc.stdout)
            ids = [item.get("source_id") for item in payload.get("events", [])]
            assert_true(
                ids[:3] == [
                    "reuters",
                    "commission",
                    "freightwaves",
                ],
                "real fixture ranking should keep seller-relevant tariff/environment/logistics as top 3 in order regardless of display language",
                errors,
            )
            assert_true(
                "generic-b2b" not in ids[:3],
                "real fixture ranking should push macro B2B logistics story out of top 3",
                errors,
            )
    finally:
        if original is None:
            REAL_EVENTS.unlink(missing_ok=True)
        else:
            REAL_EVENTS.write_text(original, encoding="utf-8")

    if errors:
        print("FAIL validate_ranking_regressions")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_ranking_regressions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
