#!/usr/bin/env python3
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "morning_brief.py"

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
    }
    base.update(overrides)
    return base


def main() -> int:
    errors = []

    policy_profile = {
        "platform": "amazon",
        "fulfillment_model": "fba",
        "market": "EU",
        "price_band": "medium",
        "category": "general",
        "risk_profile": "general",
    }

    official_policy = build_result(
        source_id="wto-latest-news",
        source_label="WTO Latest News",
        event_type="policy",
        source_theme="policy",
        source_trust_tier="official",
        source_seller_signal_bias="high",
    )
    generic_policy = build_result(
        source_trust_tier="media",
        source_seller_signal_bias="low",
    )
    official_score, official_breakdown = module.score_event(official_policy, policy_profile)
    generic_score, generic_breakdown = module.score_event(generic_policy, policy_profile)
    assert_true(official_score > generic_score, "official/policy source should outrank generic source", errors)
    assert_true(official_breakdown["source_strength"] > generic_breakdown["source_strength"], "official source should have stronger source weight", errors)
    assert_true(official_breakdown["source_strength_reason"]["trust_tier_bonus"] > generic_breakdown["source_strength_reason"]["trust_tier_bonus"], "official source should get trust tier bonus", errors)

    fresh_logistics = build_result(
        event_type="logistics",
        source_theme="logistics",
        source_id="freightwaves",
        source_label="FreightWaves",
        published_at="Tue, 10 Mar 2026 09:00:00 +0000",
    )
    stale_logistics = build_result(
        event_type="logistics",
        source_theme="logistics",
        source_id="freightwaves",
        source_label="FreightWaves",
        published_at="Thu, 05 Mar 2026 09:00:00 +0000",
    )
    fresh_score, fresh_breakdown = module.score_event(fresh_logistics, policy_profile)
    stale_score, stale_breakdown = module.score_event(stale_logistics, policy_profile)
    assert_true(fresh_score > stale_score, "fresh logistics event should outrank stale logistics event", errors)
    assert_true(fresh_breakdown["time_decay"] > stale_breakdown["time_decay"], "fresh event should get larger freshness bonus", errors)

    direct_mail_profile = {
        "platform": "tiktok-shop",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    }
    tariff_event = build_result(
        event_type="tariff",
        source_theme="tariff",
        source_id="reuters",
        source_label="Reuters",
        source_platforms=["Amazon", "TikTok", "Temu", "独立站"],
        event_summary="Detected EU tariff event that may affect cross-border seller operations.",
    )
    fba_score, _ = module.score_event(tariff_event, policy_profile)
    direct_mail_score, direct_mail_breakdown = module.score_event(tariff_event, direct_mail_profile)
    assert_true(direct_mail_score > fba_score, "seller profile boost should keep direct-mail tariff event above fba", errors)
    assert_true(direct_mail_breakdown["seller_profile"] >= 40, "direct-mail margin-sensitive tariff profile should receive strong seller boost", errors)

    amazon_only_event = build_result(
        event_type="policy",
        source_theme="policy",
        source_id="amazon-seller-forums-news",
        source_label="Amazon Seller Forums - News and Announcements",
        source_platforms=["Amazon"],
    )
    tiktok_score, tiktok_breakdown = module.score_event(amazon_only_event, direct_mail_profile)
    amazon_score, amazon_breakdown = module.score_event(amazon_only_event, policy_profile)
    assert_true(amazon_score > tiktok_score, "platform-aligned source should outrank off-platform source", errors)
    assert_true(amazon_breakdown["platform_fit"] > tiktok_breakdown["platform_fit"], "platform_fit should reward platform-aligned source", errors)

    if errors:
        print("FAIL validate_event_scoring")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_event_scoring")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
