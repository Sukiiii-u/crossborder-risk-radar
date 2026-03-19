#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
CONFIG = SKILL_ROOT / "monitoring" / "platform_official_watchlist.json"


def main() -> int:
    errors = []
    allowed_priorities = {"P0", "P1", "P2"}
    allowed_source_types = {"platform-official", "regulator-official", "carrier-official"}
    allowed_methods = {"changedetection", "rss_or_html", "manual"}
    allowed_content_methods = {"rss", "html_forum_listing", "html_article_listing", "html_page_snapshot"}
    required_platforms = {"Amazon", "TikTok", "Temu", "独立站"}

    try:
        payload = json.loads(CONFIG.read_text(encoding="utf-8"))
    except Exception as exc:
        print("FAIL validate_platform_watchlist")
        print(f"- failed to read watchlist: {exc}")
        return 1

    if not isinstance(payload, list) or not payload:
        errors.append("platform_official_watchlist.json should contain a non-empty array")

    ids = set()
    platform_coverage = set()
    for item in payload:
        if not isinstance(item, dict):
            errors.append("watchlist entries must be objects")
            continue
        item_id = item.get("id")
        if not item_id:
            errors.append("missing watchlist id")
        elif item_id in ids:
            errors.append(f"duplicate watchlist id: {item_id}")
        else:
            ids.add(item_id)

        if item.get("priority") not in allowed_priorities:
            errors.append(f"{item_id}: unsupported priority {item.get('priority')}")
        if item.get("source_type") not in allowed_source_types:
            errors.append(f"{item_id}: unsupported source_type {item.get('source_type')}")
        if item.get("monitoring_method") not in allowed_methods:
            errors.append(f"{item_id}: unsupported monitoring_method {item.get('monitoring_method')}")
        if not str(item.get("title", "")).strip():
            errors.append(f"{item_id}: missing title")
        if not str(item.get("url", "")).startswith("https://"):
            errors.append(f"{item_id}: url must be https")
        if not isinstance(item.get("platforms"), list) or not item.get("platforms"):
            errors.append(f"{item_id}: platforms must be a non-empty list")
        if not isinstance(item.get("keywords"), list) or not item.get("keywords"):
            errors.append(f"{item_id}: keywords must be a non-empty list")
        if not isinstance(item.get("business_zone"), list) or not item.get("business_zone"):
            errors.append(f"{item_id}: business_zone must be a non-empty list")
        if not str(item.get("why_it_matters", "")).strip():
            errors.append(f"{item_id}: missing why_it_matters")
        if item.get("content_url") is not None and not str(item.get("content_url", "")).startswith("https://"):
            errors.append(f"{item_id}: content_url must be https when provided")
        if item.get("content_method") is not None and item.get("content_method") not in allowed_content_methods:
            errors.append(f"{item_id}: unsupported content_method {item.get('content_method')}")
        if item.get("content_method") == "html_article_listing" and not str(item.get("article_url_prefix", "")).startswith("https://"):
            errors.append(f"{item_id}: html_article_listing requires https article_url_prefix")
        platform_coverage.update(item.get("platforms") or [])

    missing_platforms = sorted(required_platforms - platform_coverage)
    if missing_platforms:
        errors.append(f"watchlist should cover core platforms: missing {', '.join(missing_platforms)}")

    if errors:
        print("FAIL validate_platform_watchlist")
        for err in errors:
            print(f"- {err}")
        return 1

    print("PASS validate_platform_watchlist")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
