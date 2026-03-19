#!/usr/bin/env python3
import json
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from runtime_paths import CHANGEDETECTION_FEED_FILE  # noqa: E402

SKILL_ROOT = SCRIPT_DIR.parent
BASE_CONFIG_FILE = SCRIPT_DIR / "source_configs.json"
WATCHLIST_FILE = SKILL_ROOT / "monitoring" / "platform_official_watchlist.json"

SUPPORTED_EXECUTION_TYPES = {"rss", "html_forum_listing", "html_article_listing", "html_page_snapshot", "changedetection_rss"}


def load_json(path: Path) -> list[dict]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError(f"expected list payload: {path}")
    return [item for item in payload if isinstance(item, dict)]


def load_base_sources() -> list[dict]:
    return load_json(BASE_CONFIG_FILE)


def load_watchlist() -> list[dict]:
    return load_json(WATCHLIST_FILE)


def has_changedetection_input() -> bool:
    return CHANGEDETECTION_FEED_FILE.exists()


def priority_max_items(priority: str) -> int:
    return {"P0": 3, "P1": 2, "P2": 1}.get(priority, 2)


def topic_for_watchlist(source_type: str) -> str:
    if source_type == "carrier-official":
        return "logistics"
    return "policy"


def content_source_from_watchlist(item: dict) -> dict | None:
    content_url = item.get("content_url")
    content_method = item.get("content_method")
    if not str(content_url or "").startswith("https://"):
        return None
    if content_method not in {"rss", "html_forum_listing", "html_article_listing", "html_page_snapshot"}:
        return None

    normalized = {
        "id": f"{item['id']}-content",
        "label": f"{item.get('title') or item['id']} Content",
        "type": content_method,
        "url": content_url,
        "topic": topic_for_watchlist(item.get("source_type", "")),
        "platforms": item.get("platforms") or ["全平台扫描"],
        "trust_tier": item.get("source_type", "platform-official"),
        "seller_signal_bias": "high" if item.get("priority") == "P0" else "medium",
        "freshness_days": 21,
        "max_items": priority_max_items(item.get("priority", "P1")),
        "include_keywords": item.get("keywords") or [],
        "exclude_patterns": item.get("exclude_patterns") or [],
        "source_layer": "official-content",
        "watchlist_id": item.get("id"),
        "source_priority": item.get("priority", "P1"),
        "source_type": item.get("source_type"),
        "monitoring_method": "stable_content",
        "business_zone": item.get("business_zone") or [],
        "why_it_matters": item.get("why_it_matters") or "",
        "zh_title": item.get("zh_title"),
        "executable": True,
    }
    if normalized["type"] == "html_forum_listing":
        normalized["base_url"] = "https://sellercentral.amazon.com"
        normalized["min_content_length"] = 30
    if normalized["type"] == "html_article_listing":
        normalized["article_url_prefix"] = item.get("article_url_prefix", "")
        normalized["article_link_regex"] = item.get("article_link_regex", "")
        normalized["article_fetch_limit"] = int(item.get("article_fetch_limit", normalized["max_items"]))
    if normalized["type"] == "html_page_snapshot":
        normalized["published_regex"] = item.get("published_regex", "")
        normalized["content_focus_regex"] = item.get("content_focus_regex", "")
        normalized["snapshot_title_regex"] = item.get("snapshot_title_regex", "")
    return normalized


def executable_source_from_watchlist(item: dict) -> dict | None:
    method = item.get("monitoring_method")
    url = item.get("url")
    if not str(url or "").startswith("https://"):
        return None
    if method == "changedetection":
        if not has_changedetection_input():
            return None
        parsed = urlparse(url)
        host = parsed.netloc.lower()
        path = parsed.path or "/"
        return {
            "id": item["id"],
            "label": item.get("title") or item["id"],
            "type": "changedetection_rss",
            "url": url,
            "topic": topic_for_watchlist(item.get("source_type", "")),
            "platforms": item.get("platforms") or ["全平台扫描"],
            "trust_tier": item.get("source_type", "platform-official"),
            "seller_signal_bias": "high" if item.get("priority") == "P0" else "medium",
            "freshness_days": 14,
            "max_items": priority_max_items(item.get("priority", "P1")),
            "include_keywords": item.get("keywords") or [],
            "exclude_patterns": [],
            "source_layer": "official-watchlist",
            "watchlist_id": item.get("id"),
            "source_priority": item.get("priority", "P1"),
            "source_type": item.get("source_type"),
            "monitoring_method": method,
            "business_zone": item.get("business_zone") or [],
            "why_it_matters": item.get("why_it_matters") or "",
            "zh_title": item.get("zh_title"),
            "routing_host": host,
            "routing_path": path,
            "routing_patterns": [host, path, item.get("title", "")],
            "executable": True,
        }
    if method != "rss_or_html":
        return None

    normalized = {
        "id": item["id"],
        "label": item.get("title") or item["id"],
        "type": "html_forum_listing" if "seller-forums/discussions" in url else "rss",
        "url": url,
        "topic": topic_for_watchlist(item.get("source_type", "")),
        "platforms": item.get("platforms") or ["全平台扫描"],
        "trust_tier": item.get("source_type", "platform-official"),
        "seller_signal_bias": "high" if item.get("priority") == "P0" else "medium",
        "freshness_days": 21,
        "max_items": priority_max_items(item.get("priority", "P1")),
        "include_keywords": item.get("keywords") or [],
        "exclude_patterns": [],
        "source_layer": "official-watchlist",
        "watchlist_id": item.get("id"),
        "source_priority": item.get("priority", "P1"),
        "source_type": item.get("source_type"),
        "monitoring_method": method,
        "business_zone": item.get("business_zone") or [],
        "why_it_matters": item.get("why_it_matters") or "",
        "zh_title": item.get("zh_title"),
        "executable": True,
    }
    if normalized["type"] == "html_forum_listing":
        normalized["base_url"] = "https://sellercentral.amazon.com"
        normalized["min_content_length"] = 30
    return normalized


def merge_watchlist_metadata(source: dict, watch_item: dict | None) -> dict:
    merged = dict(source)
    merged["source_layer"] = "base-feed"
    merged["executable"] = merged.get("type") in SUPPORTED_EXECUTION_TYPES
    if not watch_item:
        return merged

    merged["watchlist_id"] = watch_item.get("id")
    merged["source_priority"] = watch_item.get("priority")
    merged["source_type"] = watch_item.get("source_type")
    merged["monitoring_method"] = watch_item.get("monitoring_method")
    merged["business_zone"] = watch_item.get("business_zone") or []
    merged["why_it_matters"] = watch_item.get("why_it_matters") or ""
    merged["zh_title"] = watch_item.get("zh_title")
    merged["source_layer"] = "official-watchlist"
    return merged


def load_source_registry() -> list[dict]:
    base_sources = load_base_sources()
    watchlist = load_watchlist()
    watch_by_url = {
        item.get("url"): item
        for item in watchlist
        if str(item.get("url") or "").startswith("https://")
    }

    registry: list[dict] = []
    seen_ids: set[str] = set()
    seen_keys: set[tuple[str, str, str]] = set()

    for source in base_sources:
        merged = merge_watchlist_metadata(source, watch_by_url.get(source.get("url")))
        registry.append(merged)
        seen_ids.add(str(merged.get("id")))
        seen_keys.add((str(merged.get("url")), str(merged.get("type")), str(merged.get("source_layer"))))

    for item in watchlist:
        content_source = content_source_from_watchlist(item)
        if content_source:
            content_key = (
                str(content_source.get("url")),
                str(content_source.get("type")),
                str(content_source.get("source_layer")),
            )
            if content_source["id"] not in seen_ids and content_key not in seen_keys:
                registry.append(content_source)
                seen_ids.add(content_source["id"])
                seen_keys.add(content_key)

        executable = executable_source_from_watchlist(item)
        if not executable:
            wl_id = str(item.get("id") or "")
            if wl_id and wl_id not in seen_ids:
                registry.append(
                    {
                        "id": item.get("id"),
                        "label": item.get("title") or item.get("id"),
                        "url": item.get("url"),
                        "platforms": item.get("platforms") or ["全平台扫描"],
                        "source_priority": item.get("priority"),
                        "source_type": item.get("source_type"),
                        "monitoring_method": item.get("monitoring_method"),
                        "business_zone": item.get("business_zone") or [],
                        "why_it_matters": item.get("why_it_matters") or "",
                        "zh_title": item.get("zh_title"),
                        "source_layer": "official-watchlist",
                        "watchlist_id": item.get("id"),
                        "executable": False,
                    }
                )
                seen_ids.add(wl_id)
            continue
        exec_key = (
            str(executable.get("url")),
            str(executable.get("type")),
            str(executable.get("source_layer")),
        )
        if executable["id"] in seen_ids or exec_key in seen_keys:
            continue
        registry.append(executable)
        seen_ids.add(executable["id"])
        seen_keys.add(exec_key)

    return registry


def load_executable_sources() -> list[dict]:
    return [
        item for item in load_source_registry()
        if item.get("executable") and item.get("type") in SUPPORTED_EXECUTION_TYPES
    ]
