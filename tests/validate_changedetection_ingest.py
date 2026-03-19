#!/usr/bin/env python3
import importlib.util
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "fetch_real_events.py"

spec = importlib.util.spec_from_file_location("fetch_real_events", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    now = datetime(2026, 3, 13, 0, 0, tzinfo=timezone.utc)
    source = {
        "id": "tiktok-shop-newsroom",
        "label": "TikTok Shop Academy / Seller Updates",
        "type": "changedetection_rss",
        "url": "https://seller-us.tiktok.com/university/home?lang=en",
        "topic": "policy",
        "platforms": ["TikTok"],
        "trust_tier": "platform-official",
        "seller_signal_bias": "high",
        "source_priority": "P0",
        "source_type": "platform-official",
        "source_layer": "official-watchlist",
        "business_zone": ["店铺合规", "履约时效"],
        "why_it_matters": "TikTok Shop 规则更新频繁，直接影响流量、履约、禁售和店铺安全。",
        "watchlist_id": "tiktok-shop-newsroom",
        "zh_title": "TikTok Shop 卖家规则更新",
        "routing_host": "seller-us.tiktok.com",
        "routing_path": "/university/home",
        "include_keywords": ["shop", "seller", "policy", "fulfillment", "compliance"],
        "exclude_patterns": [],
        "freshness_days": 14,
        "max_items": 2,
    }
    xml = b"""
    <rss><channel>
      <item>
        <title>ChangeDetection.io Notification - https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</title>
        <link>https://seller-us.tiktok.com/university/essay?identity=1&amp;role=1&amp;knowledge_id=123456789</link>
        <description>TikTok Shop seller policy update adds fulfillment compliance checks for marketplace orders.</description>
        <pubDate>Fri, 13 Mar 2026 00:00:00 GMT</pubDate>
      </item>
      <item>
        <title>ChangeDetection.io Notification - https://sell.amazon.com/blog/announcements</title>
        <link>https://sell.amazon.com/blog/announcements</link>
        <description>Amazon announcement about FBA fees.</description>
        <pubDate>Fri, 13 Mar 2026 00:00:00 GMT</pubDate>
      </item>
    </channel></rss>
    """
    errors: list[str] = []

    events, drop_stats = module.parse_changedetection_feed(xml, source, now)
    assert_true(len(events) == 1, f"expected 1 kept changedetection event, got {len(events)}", errors)
    if events:
        event = events[0]
        assert_true(event.get("source_layer") == "official-watchlist", "changedetection event should preserve source layer", errors)
        assert_true(event.get("watchlist_id") == "tiktok-shop-newsroom", "changedetection event should preserve watchlist id", errors)
        assert_true(event.get("source_priority") == "P0", "changedetection event should preserve priority metadata", errors)
        assert_true(event.get("url") == "https://seller-us.tiktok.com/university/essay?identity=1&role=1&knowledge_id=123456789", "changedetection event should preserve original page URL", errors)
        assert_true(event.get("title") == "TikTok Shop 卖家规则更新", "changedetection event title should be normalized to zh watchlist title", errors)
        assert_true("fulfillment compliance checks" in event.get("content", ""), "changedetection event content should preserve human-readable delta", errors)

    assert_true(not drop_stats.get("low_relevance"), "matching changedetection event should not be dropped for low relevance", errors)

    if errors:
        print("FAIL validate_changedetection_ingest")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_changedetection_ingest")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
