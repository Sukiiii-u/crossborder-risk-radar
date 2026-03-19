#!/usr/bin/env python3
import importlib.util
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
SCRIPT = SKILL_ROOT / "scripts" / "source_registry.py"

spec = importlib.util.spec_from_file_location("source_registry", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def assert_true(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> int:
    errors: list[str] = []

    registry = module.load_source_registry()
    executable = module.load_executable_sources()

    assert_true(bool(registry), "source registry should not be empty", errors)
    assert_true(bool(executable), "executable sources should not be empty", errors)

    watchlist_only = [item for item in registry if item.get("source_layer") == "official-watchlist"]
    assert_true(bool(watchlist_only), "registry should include official watchlist metadata", errors)

    amazon_forum_registry = next((item for item in registry if item.get("id") == "amazon-seller-forums-news"), None)
    assert_true(amazon_forum_registry is not None, "amazon forum official source should exist in registry", errors)
    if amazon_forum_registry:
        assert_true(amazon_forum_registry.get("monitoring_method") == "changedetection", "amazon forum source should now be routed through changedetection", errors)

    amazon_forum_content = next((item for item in registry if item.get("id") == "amazon-seller-forums-news-content"), None)
    assert_true(amazon_forum_content is not None, "amazon forum should also expose stable content source", errors)
    if amazon_forum_content:
        assert_true(amazon_forum_content.get("type") == "html_forum_listing", "amazon forum stable content should use html forum listing parser", errors)
        assert_true(amazon_forum_content.get("source_layer") == "official-content", "amazon forum stable content should use official-content layer", errors)
        assert_true(amazon_forum_content.get("monitoring_method") == "stable_content", "amazon forum stable content should be marked stable_content", errors)

    tiktok_registry_item = next((item for item in registry if item.get("id") == "tiktok-shop-newsroom"), None)
    assert_true(tiktok_registry_item is not None, "registry should preserve tiktok official source metadata", errors)
    if tiktok_registry_item:
        assert_true(tiktok_registry_item.get("monitoring_method") == "changedetection", "tiktok official source should preserve changedetection monitoring method", errors)
        if not module.has_changedetection_input():
            assert_true(tiktok_registry_item.get("executable") is False, "changedetection-only sources should stay non-executable without feed input", errors)
        assert_true(tiktok_registry_item.get("url") == "https://seller-us.tiktok.com/university/home?lang=en", "tiktok official source should use seller academy url", errors)

    amazon_blog_content = next((item for item in executable if item.get("id") == "amazon-seller-announcements-content"), None)
    assert_true(amazon_blog_content is not None, "amazon seller announcements should now have stable content source", errors)
    if amazon_blog_content:
        assert_true(amazon_blog_content.get("type") == "html_article_listing", "amazon seller announcements stable content should use html article listing parser", errors)
        assert_true(amazon_blog_content.get("source_layer") == "official-content", "amazon seller announcements stable content should use official-content layer", errors)

    tiktok_content = next((item for item in executable if item.get("id") == "tiktok-shop-newsroom-content"), None)
    assert_true(tiktok_content is None, "tiktok seller academy should stay in monitoring-only mode until a real stable listing source exists", errors)

    eu_content = next((item for item in executable if item.get("id") == "independent-site-regulators-eu-customs-content"), None)
    assert_true(eu_content is not None, "EU customs should expose stable content source", errors)
    if eu_content:
        assert_true(eu_content.get("type") == "rss", "EU customs stable content should use rss", errors)

    cbp_content = next((item for item in executable if item.get("id") == "independent-site-regulators-cbp-ecommerce-content"), None)
    assert_true(cbp_content is not None, "CBP e-commerce should expose stable content source", errors)
    if cbp_content:
        assert_true(cbp_content.get("type") == "html_article_listing", "CBP stable content should use html article listing parser", errors)

    usps_content = next((item for item in executable if item.get("id") == "independent-site-carrier-usps-international-alerts-content"), None)
    assert_true(usps_content is not None, "USPS international alerts should expose stable content source", errors)
    if usps_content:
        assert_true(usps_content.get("type") == "html_page_snapshot", "USPS stable content should use html page snapshot parser", errors)
        assert_true(usps_content.get("source_layer") == "official-content", "USPS stable content should use official-content layer", errors)

    canonical_feed = SKILL_ROOT / "monitoring" / "changedetection_feed.xml"
    original_feed = canonical_feed.read_text(encoding="utf-8") if canonical_feed.exists() else None
    with tempfile.NamedTemporaryFile("w", suffix=".xml", delete=False) as temp_feed:
        temp_feed.write("<rss><channel></channel></rss>")
        temp_path = temp_feed.name
    try:
        canonical_feed.write_text(Path(temp_path).read_text(encoding="utf-8"), encoding="utf-8")
        changedetection_exec = module.load_executable_sources()
    finally:
        if original_feed is None:
            canonical_feed.unlink(missing_ok=True)
        else:
            canonical_feed.write_text(original_feed, encoding="utf-8")
        Path(temp_path).unlink(missing_ok=True)

    tiktok_changedetection = next((item for item in changedetection_exec if item.get("id") == "tiktok-shop-newsroom"), None)
    assert_true(tiktok_changedetection is not None, "changedetection source should become executable when RSS input is configured", errors)
    if tiktok_changedetection:
        assert_true(tiktok_changedetection.get("type") == "changedetection_rss", "changedetection source should map to changedetection_rss", errors)
        assert_true(tiktok_changedetection.get("routing_host") == "seller-us.tiktok.com", "changedetection source should preserve routing host", errors)

    amazon_forum = next((item for item in changedetection_exec if item.get("id") == "amazon-seller-forums-news"), None)
    assert_true(amazon_forum is not None, "amazon forum official source should become executable when feed exists", errors)
    if amazon_forum:
        assert_true(amazon_forum.get("type") == "changedetection_rss", "amazon forum source should map to changedetection_rss", errors)
        assert_true(amazon_forum.get("source_priority") == "P0", "amazon forum source should preserve watchlist priority", errors)
        assert_true(amazon_forum.get("source_type") == "platform-official", "amazon forum source should preserve watchlist source_type", errors)
        assert_true(bool(amazon_forum.get("business_zone")), "amazon forum source should preserve business_zone metadata", errors)

    freightwaves = next((item for item in executable if item.get("id") == "freightwaves"), None)
    assert_true(freightwaves is not None, "base executable industry sources should remain available in registry", errors)
    if freightwaves:
        assert_true(freightwaves.get("source_layer") == "base-feed", "industry feed should stay in base-feed layer", errors)

    if errors:
        print("FAIL validate_source_registry")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_source_registry")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
