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
    now = datetime(2026, 3, 10, 0, 0, tzinfo=timezone.utc)
    source = {
        "id": "test-source",
        "label": "Test Source",
        "type": "rss",
        "topic": "policy",
        "freshness_days": 7,
        "include_keywords": ["tariff", "shipping", "customs"],
        "exclude_patterns": ["newsletter", "podcast"],
    }
    errors = []

    fresh_event = {
        "title": "EU tariff update hits parcel imports",
        "content": "EU customs officials are discussing a new tariff on low-value parcel imports, raising cross-border shipping costs for sellers.",
        "url": "https://example.com/fresh",
        "published_at": "Mon, 09 Mar 2026 00:00:00 GMT",
    }
    keep, reason = module.should_keep_event(fresh_event, source, now)
    assert_true(keep and reason is None, "fresh relevant event should pass", errors)

    stale_event = dict(fresh_event, url="https://example.com/stale", published_at="Mon, 20 Jan 2026 00:00:00 GMT")
    keep, reason = module.should_keep_event(stale_event, source, now)
    assert_true((not keep) and reason == "stale", "stale event should be dropped", errors)

    empty_event = dict(fresh_event, url="https://example.com/empty", content="  ")
    keep, reason = module.should_keep_event(empty_event, source, now)
    assert_true((not keep) and reason in {"empty_content", "content_too_short"}, "empty event should be dropped", errors)

    noisy_event = dict(fresh_event, url="https://example.com/noisy", content="Podcast newsletter: this week we chat about random things")
    keep, reason = module.should_keep_event(noisy_event, source, now)
    assert_true((not keep) and reason == "noise", "noise event should be dropped", errors)

    earnings_event = dict(
        fresh_event,
        url="https://example.com/earnings",
        title="Carrier reports quarterly earnings after acquisition",
        content="The logistics company shared quarterly earnings and investor commentary after its latest acquisition.",
    )
    keep, reason = module.should_keep_event(earnings_event, source, now)
    assert_true((not keep) and reason == "noise", "enterprise earnings story should be dropped as noise", errors)

    marketing_event = dict(
        fresh_event,
        url="https://example.com/marketing",
        title="How to Catch the Attention of Etsy’s Marketing Team",
        content="Marketplace sellers discuss how to get more exposure from the marketing team and shop direct placements.",
    )
    keep, reason = module.should_keep_event(marketing_event, source, now)
    assert_true((not keep) and reason == "noise", "marketing exposure story should be dropped as noise", errors)

    enforcement_event = dict(
        fresh_event,
        url="https://example.com/counterfeit",
        title="Bogus watches intercepted by CBP officers in Cincinnati",
        content="CBP officers seized counterfeit watches in an enforcement action at the airport.",
    )
    keep, reason = module.should_keep_event(enforcement_event, source, now)
    assert_true((not keep) and reason == "noise", "counterfeit seizure story should be dropped as noise", errors)

    irrelevant_event = dict(fresh_event, url="https://example.com/irrelevant", title="Local culture feature", content="An arts and culture festival opened downtown with music and food.")
    keep, reason = module.should_keep_event(irrelevant_event, source, now)
    assert_true((not keep) and reason == "low_relevance", "irrelevant event should be dropped", errors)

    sig1 = module.build_signature(fresh_event["title"], fresh_event["url"], fresh_event["content"])
    sig2 = module.build_signature(fresh_event["title"] + " ", fresh_event["url"], fresh_event["content"])
    assert_true(sig1 == sig2, "signature should be stable across whitespace", errors)

    xml = b"""
    <rss><channel>
      <item>
        <title>EU tariff update hits parcel imports</title>
        <link>https://example.com/1</link>
        <description>EU customs officials are discussing a new tariff on low-value parcel imports, raising cross-border shipping costs for sellers.</description>
        <pubDate>Mon, 09 Mar 2026 00:00:00 GMT</pubDate>
      </item>
      <item>
        <title>EU tariff update hits parcel imports</title>
        <link>https://example.com/1</link>
        <description>EU customs officials are discussing a new tariff on low-value parcel imports, raising cross-border shipping costs for sellers.</description>
        <pubDate>Mon, 09 Mar 2026 00:00:00 GMT</pubDate>
      </item>
      <item>
        <title>Random feature story</title>
        <link>https://example.com/2</link>
        <description>An arts and culture festival opened downtown with music and food.</description>
        <pubDate>Mon, 09 Mar 2026 00:00:00 GMT</pubDate>
      </item>
      <item>
        <title>Very old shipping story</title>
        <link>https://example.com/3</link>
        <description>Major shipping delays continue at several ports.</description>
        <pubDate>Mon, 01 Dec 2025 00:00:00 GMT</pubDate>
      </item>
    </channel></rss>
    """
    events, drop_stats = module.parse_rss(xml, dict(source, max_items=3), now)
    assert_true(len(events) == 1, f"expected 1 kept event, got {len(events)}", errors)
    assert_true(events[0]["source_trust_tier"] == "industry", "expected source trust tier to be copied into rss event", errors)
    assert_true(events[0]["source_seller_signal_bias"] == "medium", "expected seller signal bias to be copied into rss event", errors)
    assert_true(events[0]["source_layer"] == "base-feed", "expected rss event source layer metadata", errors)
    assert_true(drop_stats.get("duplicate") == 1, "expected duplicate drop count", errors)
    assert_true(drop_stats.get("low_relevance") == 1, "expected low relevance drop count", errors)
    assert_true(drop_stats.get("stale") == 1, "expected stale drop count", errors)
    events, drop_stats, audit = module.parse_rss(xml, dict(source, max_items=3), now, include_audit=True)
    assert_true(bool(audit.get("kept_samples")), "expected kept_samples in rss audit mode", errors)
    assert_true(bool(audit.get("dropped_samples", {}).get("duplicate")), "expected duplicate sample in rss audit mode", errors)
    assert_true(bool(audit.get("dropped_samples", {}).get("low_relevance")), "expected low relevance sample in rss audit mode", errors)

    html = b"""
    <html><body>
      <time datetime="2026-03-09T12:00:00.000Z">1 day ago</time>
      <a href="/seller-forums/discussions/t/policy-1">2026 updates to FBA fee policy</a>
      <div class="search-content-post"><p>Amazon announces a new fee and compliance policy for FBA shipments.</p></div>

      <time datetime="2026-03-09T10:00:00.000Z">1 day ago</time>
      <a href="/seller-forums/discussions/t/policy-1">2026 updates to FBA fee policy</a>
      <div class="search-content-post"><p>Amazon announces a new fee and compliance policy for FBA shipments.</p></div>

      <time datetime="2026-03-09T09:00:00.000Z">1 day ago</time>
      <a href="/seller-forums/discussions/t/chat-1">Meet your top community contributors</a>
      <div class="search-content-post"><p>Community roundup and forum highlights.</p></div>
    </body></html>
    """
    forum_source = dict(
        source,
        id="amazon-forums",
        label="Amazon Seller Forums",
        type="html_forum_listing",
        base_url="https://sellercentral.amazon.com",
        trust_tier="platform-official",
        seller_signal_bias="high",
        source_priority="P0",
        source_type="platform-official",
        source_layer="official-watchlist",
        business_zone=["FBA与补货"],
        why_it_matters="直接影响 Amazon 卖家的费用、履约、违规与账号安全。",
        watchlist_id="amazon-seller-forums-news",
        include_keywords=["fee", "policy", "compliance", "fba"],
        exclude_patterns=["community contributors", "forum highlights"],
        max_items=3,
    )
    events, drop_stats = module.parse_html_forum_listing(html, forum_source, now)
    assert_true(len(events) == 1, f"expected 1 kept forum event, got {len(events)}", errors)
    assert_true(events[0]["url"] == "https://sellercentral.amazon.com/seller-forums/discussions/t/policy-1", "expected forum URL to be normalized", errors)
    assert_true(events[0]["source_trust_tier"] == "platform-official", "expected forum event trust tier metadata", errors)
    assert_true(events[0]["source_seller_signal_bias"] == "high", "expected forum event seller signal bias metadata", errors)
    assert_true(events[0]["source_priority"] == "P0", "expected forum event priority metadata", errors)
    assert_true(events[0]["source_layer"] == "official-watchlist", "expected forum event source layer metadata", errors)
    assert_true(events[0]["watchlist_id"] == "amazon-seller-forums-news", "expected forum event watchlist metadata", errors)
    assert_true(drop_stats.get("duplicate") == 1, "expected duplicate forum drop count", errors)
    assert_true(drop_stats.get("noise") == 1, "expected noise forum drop count", errors)
    events, drop_stats, audit = module.parse_html_forum_listing(html, forum_source, now, include_audit=True)
    assert_true(bool(audit.get("kept_samples")), "expected kept_samples in forum audit mode", errors)
    assert_true(bool(audit.get("dropped_samples", {}).get("noise")), "expected noise sample in forum audit mode", errors)

    html_listing = b"""
    <html><body>
      <a class="Link" aria-label="Sellers who use FBA Donations now have access to donation certificates" href="https://sell.amazon.com/blog/announcements/fba-donation-certificate">Read more</a>
    </body></html>
    """
    tiktok_listing = b"""
    <html><body>
      <span>March 9, 2026</span>
      <a class="navigation-base" href="/seller-update-fee-rule?lang=en"><h1>Seller update to fee rule</h1></a>
    </body></html>
    """
    article_pages = {
        "https://sell.amazon.com/blog/announcements/fba-donation-certificate": b'''
        <html><head>
          <meta property="og:title" content="Sellers who use FBA Donations now have access to donation certificates" />
          <meta property="og:description" content="Amazon updates documentation for FBA donation certificates and seller compliance." />
          <meta property="article:published_time" content="2026-03-09T12:00:00Z" />
          <link rel="canonical" href="https://sell.amazon.com/blog/announcements/fba-donation-certificate" />
        </head></html>
        ''',
        "https://newsroom.tiktok.com/seller-update-fee-rule?lang=en": b'''
        <html><head>
          <meta property="og:title" content="Seller update to fee rule" />
          <meta property="og:description" content="TikTok Shop updates seller fee and fulfillment compliance policy." />
          <link rel="canonical" href="https://newsroom.tiktok.com/seller-update-fee-rule?lang=en" />
        </head></html>
        ''',
    }
    original_fetch_url = module.fetch_url
    module.fetch_url = lambda url: article_pages[url]
    try:
        article_source = dict(
            source,
            id="amazon-announcements",
            label="Amazon Announcements",
            type="html_article_listing",
            content_url="https://sell.amazon.com/blog/announcements",
            article_url_prefix="https://sell.amazon.com/blog/announcements/",
            article_fetch_limit=2,
            trust_tier="platform-official",
            seller_signal_bias="high",
            source_priority="P0",
            source_type="platform-official",
            source_layer="official-content",
            business_zone=["FBA与补货"],
            why_it_matters="直接影响 Amazon 卖家的费用、履约、违规与账号安全。",
            watchlist_id="amazon-seller-announcements",
            include_keywords=["fba", "seller", "compliance", "fee", "policy", "fulfillment"],
            exclude_patterns=[],
            max_items=2,
        )
        events, drop_stats = module.parse_html_article_listing(html_listing, article_source, now)

        tiktok_source = dict(
            source,
            id="tiktok-newsroom",
            label="TikTok Newsroom",
            type="html_article_listing",
            content_url="https://newsroom.tiktok.com/",
            article_url_prefix="https://newsroom.tiktok.com/",
            article_link_regex=r"/[^\"?#]+\?lang=en",
            article_fetch_limit=2,
            trust_tier="platform-official",
            seller_signal_bias="high",
            source_priority="P0",
            source_type="platform-official",
            source_layer="official-content",
            business_zone=["店铺合规"],
            why_it_matters="TikTok Shop 规则更新频繁，直接影响流量、履约、禁售和店铺安全。",
            watchlist_id="tiktok-shop-newsroom",
            include_keywords=["seller", "fee", "policy", "fulfillment", "compliance", "shop"],
            exclude_patterns=[],
            max_items=2,
        )
        tiktok_events, _ = module.parse_html_article_listing(tiktok_listing, tiktok_source, now)
    finally:
        module.fetch_url = original_fetch_url

    snapshot_source = dict(
        source,
        id="usps-international-alerts",
        label="USPS International Service Alerts",
        type="html_page_snapshot",
        topic="logistics",
        trust_tier="carrier-official",
        seller_signal_bias="medium",
        source_priority="P1",
        source_type="carrier-official",
        source_layer="official-content",
        business_zone=["物流时效"],
        why_it_matters="国际停收与线路中断会直接影响直邮小包履约承诺。",
        watchlist_id="independent-site-carrier-usps-international-alerts",
        include_keywords=["international", "service suspension", "mail acceptance", "shipping"],
        published_regex=r"Updated:\s*([A-Z][a-z]+ \d{1,2}, \d{4})",
        content_focus_regex=r"International Mail Service Suspensions[\s\S]{0,1200}",
        content_url="https://about.usps.com/newsroom/service-alerts/international/",
        url="https://about.usps.com/newsroom/service-alerts/international/",
        max_items=1,
    )
    snapshot_html = b'''
    <html><head>
      <title>International Service Alerts - Newsroom - About.usps.com</title>
      <meta name="description" content="Information about disruptions that may affect service for customers shipping internationally." />
    </head><body>
      <main>
        <h1>International service disruptions</h1>
        <h2>International Mail Service Suspensions</h2>
        <p>Updated: March 13, 2026</p>
        <p>The Postal Service is temporarily suspending international mail acceptance for certain destinations due to inadequate transportation options or service disruptions within the country.</p>
      </main>
    </body></html>
    '''
    snapshot_events, snapshot_drop_stats = module.parse_html_page_snapshot(snapshot_html, snapshot_source, now)
    assert_true(len(snapshot_events) == 1, f"expected 1 kept snapshot event, got {len(snapshot_events)}", errors)
    if snapshot_events:
        assert_true(snapshot_events[0]["source_trust_tier"] == "carrier-official", "expected page snapshot trust tier metadata", errors)
        assert_true(snapshot_events[0]["published_at"].startswith("2026-03-13"), "expected page snapshot to normalize Updated date", errors)
        assert_true(snapshot_events[0]["url"] == "https://about.usps.com/newsroom/service-alerts/international/", "expected page snapshot to preserve source URL", errors)
    assert_true(not snapshot_drop_stats, "expected no drop stats for valid page snapshot", errors)
    assert_true(len(events) == 1, f"expected 1 kept amazon html article event, got {len(events)}", errors)
    assert_true(events[0]["source_layer"] == "official-content", "expected article listing event source layer metadata", errors)
    assert_true(events[0]["watchlist_id"] == "amazon-seller-announcements", "expected article listing watchlist metadata", errors)
    assert_true(events[0]["published_at"] == "2026-03-09T12:00:00Z", "expected article listing to use detail published time", errors)
    assert_true(len(tiktok_events) == 1, f"expected 1 kept tiktok html article event, got {len(tiktok_events)}", errors)
    assert_true(tiktok_events[0]["url"] == "https://newsroom.tiktok.com/seller-update-fee-rule?lang=en", "expected relative article URLs to normalize against source host", errors)
    assert_true(tiktok_events[0]["published_at"] == "2026-03-09T00:00:00Z", "expected article listing to fall back to listing date when article metadata is missing", errors)

    maintenance_source = dict(
        source,
        id="cbp-trade",
        label="CBP Newsroom",
        type="rss",
        exclude_patterns=[
            "automated commercial environment",
            "ace truck manifest",
            "carnet data elements",
            "container seal changes",
        ],
        include_keywords=["trade information notice", "customs", "import"],
        max_items=3,
    )
    maintenance_event = dict(
        fresh_event,
        url="https://example.com/ace-maintenance",
        title="Trade Information Notice: New Carnet Data Elements",
        content="Trade Information Notice for ACE Portal trade users covering new carnet data elements and automated commercial environment updates.",
    )
    keep, reason = module.should_keep_event(maintenance_event, maintenance_source, now)
    assert_true((not keep) and reason == "noise", "ACE/carnet maintenance notice should be dropped as noise", errors)

    packaging_innovation_event = dict(
        fresh_event,
        url="https://example.com/reusable-packaging",
        title="FedEx introduces reusable shipping boxes for B2B shipments",
        content="FedEx introduces reusable shipping boxes for B2B shipments to improve handling efficiency between facilities.",
    )
    keep, reason = module.should_keep_event(packaging_innovation_event, dict(source, topic="environment"), now)
    assert_true((not keep) and reason == "low_relevance", "corporate reusable packaging story should be dropped before entering the radar", errors)

    seller_fee_event = dict(
        fresh_event,
        url="https://example.com/amazon-ad-fees",
        title="Sellers Say Amazon Charged Ad Fees throughout Thursday's Outage",
        content="Sellers say Amazon charged ad fees throughout Thursday's outage, raising cost and checkout risk for marketplace merchants.",
    )
    keep, reason = module.should_keep_event(
        seller_fee_event,
        dict(source, topic="policy", include_keywords=["fee", "fees", "outage", "checkout", "seller", "amazon"]),
        now,
    )
    assert_true(keep and reason is None, "seller fee outage story should still pass fetch filtering", errors)

    publish_ok, reason = module.should_publish_ingest_snapshot(
        {
            "by_source": {
                "amazon-seller-forums-news-content": {
                    "source_layer": "official-content",
                    "status": "verified",
                }
            }
        },
        [],
        [{"title": "ok"}],
    )
    assert_true(publish_ok and reason is None, "expected ingest snapshot with stable success to publish", errors)

    publish_ok, reason = module.should_publish_ingest_snapshot(
        {
            "by_source": {
                "amazon-seller-forums-news-content": {
                    "source_layer": "official-content",
                    "status": "broken",
                    "error": "<urlopen error [Errno 1] Operation not permitted>",
                },
                "freightwaves": {
                    "source_layer": "base-feed",
                    "status": "broken",
                    "error": "<urlopen error [Errno 1] Operation not permitted>",
                },
            }
        },
        [{"source": "freightwaves", "error": "<urlopen error [Errno 1] Operation not permitted>"}],
        [{"title": "changedetection event only"}],
    )
    assert_true((not publish_ok) and reason == "stable content sources were unavailable; preserved previous ingest snapshot", "expected transient stable-source failures to block ingest publish", errors)

    if errors:
        print("FAIL validate_fetch_real_events")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_fetch_real_events")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
