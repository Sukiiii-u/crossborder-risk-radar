#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import ssl
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from network_config import load_network_config, proxy_mapping  # noqa: E402
from freshness import is_within_age  # noqa: E402
from runtime_paths import POLICY_WATCH_FILE, ensure_runtime_data_dir  # noqa: E402

CONFIG_FILE = Path(os.environ.get("POLICY_WATCH_CONFIG_FILE", SCRIPT_DIR.parent / "configs" / "policy_watch_sources.json"))

BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


def fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    ctx = ssl.create_default_context()
    config = load_network_config()
    previous_no_proxy = os.environ.get("no_proxy")
    if config.get("no_proxy"):
        os.environ["no_proxy"] = config["no_proxy"]
    try:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler(proxy_mapping(config)),
            urllib.request.HTTPSHandler(context=ctx),
        )
        with opener.open(req, timeout=20) as resp:
            return resp.read().decode("utf-8", errors="ignore")
    finally:
        if config.get("no_proxy"):
            if previous_no_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = previous_no_proxy


def strip_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<script.*?</script>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<style.*?</style>", " ", text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def extract_meta(html_text: str, attr: str, value: str) -> str:
    pattern = re.compile(
        rf'<meta[^>]+{attr}=["\']{re.escape(value)}["\'][^>]+content=["\']([^"\']+)["\']',
        re.IGNORECASE,
    )
    match = pattern.search(html_text)
    return html.unescape(match.group(1)).strip() if match else ""


def extract_title(html_text: str) -> str:
    for attr, value in (("property", "og:title"), ("name", "twitter:title")):
        meta = extract_meta(html_text, attr, value)
        if meta:
            return meta
    match = re.search(r"<title>(.*?)</title>", html_text, flags=re.IGNORECASE | re.DOTALL)
    return strip_html(match.group(1)) if match else ""


def extract_published_at(source: dict, html_text: str) -> str | None:
    patterns = [
        r'Release Date\s*</[^>]+>\s*<[^>]+>([^<]+)',
        r'Last Modified:\s*([^<]+)',
        r'"datePublished"\s*:\s*"([^"]+)"',
        r'"dateModified"\s*:\s*"([^"]+)"',
        r'(\d{4}-\d{2}-\d{2})',
        r'([A-Z][a-z]{2},\s*\d{2}/\d{2}/\d{4})',
        r'([A-Z][a-z]{2}\s+\d{1,2},\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            raw = match.group(1).strip()
            for fmt in ("%Y-%m-%d", "%a, %m/%d/%Y", "%b %d, %Y", "%B %d, %Y"):
                try:
                    return datetime.strptime(raw, fmt).replace(tzinfo=timezone.utc).isoformat()
                except ValueError:
                    continue
    url_match = re.search(r"-(\d{4})-(\d{2})-(\d{2})_", source.get("url", ""))
    if url_match:
        year, month, day = url_match.groups()
        return datetime(int(year), int(month), int(day), tzinfo=timezone.utc).isoformat()
    return None


def build_policy_item(source: dict, html_text: str, fetched_at: str) -> dict | None:
    title = extract_title(html_text) or source["title"]
    description = (
        extract_meta(html_text, "property", "og:description")
        or extract_meta(html_text, "name", "description")
    )
    plain_text = strip_html(html_text)
    haystack = f"{title} {description} {plain_text[:12000]}".lower()
    keywords = [kw.lower() for kw in source.get("match_any_keywords", [])]
    if keywords and not any(keyword in haystack for keyword in keywords):
        return None

    published_at = extract_published_at(source, html_text)
    max_age_days = source.get("max_age_days")
    if max_age_days:
        if not is_within_age(published_at, int(max_age_days), datetime.fromisoformat(fetched_at)):
            return None

    summary = source.get("zh_summary_template") or description or plain_text[:400]
    summary = re.sub(r"\s+", " ", summary).strip()
    if len(summary) > 220:
        summary = summary[:217].rstrip() + "..."

    return {
        "id": source["id"],
        "title": source.get("zh_title") or title,
        "source_title": title,
        "summary": summary,
        "event_type": source["event_type"],
        "risk_level": source["risk_level"],
        "platforms": source["platforms"],
        "regions": source["regions"],
        "source_type": source["source_type"],
        "source_layer": "policy-watch",
        "source": {
            "name": source["source_name"],
            "url": source["url"],
        },
        "impact": summary,
        "action": source["action"],
        "published_at": published_at,
        "timestamp": fetched_at,
        "effective_date": source.get("effective_date"),
        "monitor_until": source.get("monitor_until"),
        "impact_dimensions": source.get("impact_dimensions", []),
    }


def main() -> int:
    ensure_runtime_data_dir()
    config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    fetched_at = datetime.now(timezone.utc).isoformat()
    items = []
    failures = []

    for source in config:
        try:
            html_text = fetch_url(source["url"])
            item = build_policy_item(source, html_text, fetched_at)
            if item:
                items.append(item)
        except Exception as exc:
            failures.append({"source": source["id"], "error": str(exc)})

    payload = {
        "generated_at": fetched_at,
        "item_count": len(items),
        "items": items,
        "failures": failures,
    }
    preserve_existing = len(items) == 0 and bool(failures) and POLICY_WATCH_FILE.exists()
    if preserve_existing:
        payload["preserved_previous_snapshot"] = True
        payload["warning"] = "all policy-watch sources failed; preserved previous policy snapshot"
    else:
        temp = POLICY_WATCH_FILE.with_suffix(".json.tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(POLICY_WATCH_FILE)
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if items or preserve_existing else 1


if __name__ == "__main__":
    raise SystemExit(main())
