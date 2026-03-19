#!/usr/bin/env python3
import hashlib
import html
import json
import os
import re
import ssl
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))
from analyze_event import classify_relevance  # noqa: E402
from runtime_paths import CHANGEDETECTION_FEED_FILE, REAL_EVENTS_AUDIT_FILE as AUDIT_FILE, REAL_EVENTS_FILE as OUTPUT_FILE, SOURCE_STATUS_FILE, ensure_runtime_data_dir  # noqa: E402
from freshness import is_within_age  # noqa: E402
from network_config import load_network_config, proxy_mapping  # noqa: E402
from source_registry import load_executable_sources  # noqa: E402
from zh_localization import localize_event_payload  # noqa: E402
MAX_ITEMS_PER_SOURCE = 3
MAX_AUDIT_SAMPLES_PER_REASON = 3
MAX_AUDIT_KEPT_SAMPLES = 3
DEFAULT_FRESHNESS_DAYS = 10
DEFAULT_MIN_CONTENT_LENGTH = 40
DEFAULT_RELEVANCE_KEYWORDS = [
    "tariff",
    "trade",
    "customs",
    "import",
    "export",
    "shipping",
    "logistics",
    "port",
    "freight",
    "supply chain",
    "compliance",
    "regulation",
    "policy",
    "packaging",
    "parcel",
    "vat",
    "duty",
    "fee",
    "fees",
    "sanction",
    "inspection",
    "container",
    "warehouse",
    "outage",
    "checkout",
    "ecommerce",
    "e-commerce",
    "cross-border",
]
DEFAULT_NOISE_PATTERNS = [
    r"subscribe now",
    r"listen to the article",
    r"sign up for",
    r"podcast",
    r"opinion",
]
SELLER_OPERATIONAL_NOISE_PATTERNS = [
    r"\bearnings\b",
    r"\brecord quarter\b",
    r"\bquarterly results\b",
    r"\bq[1-4]\b",
    r"\bacquires?\b",
    r"\bacquisition\b",
    r"\bmerger\b",
    r"\binvestor(?:s)?\b",
    r"\bshares?\b",
    r"\bstock\b",
    r"\bchief executive\b",
    r"\bceo\b",
    r"\bcfo\b",
    r"\bmarketing campaign\b",
    r"\bbrand campaign\b",
    r"\bmarketing team\b",
    r"\bshop direct\b",
    r"\bbuy for me\b",
    r"\bfull enterprise sale\b",
    r"\benterprise sale\b",
    r"\brecognition cycle\b",
    r"\bapplicants can expect next\b",
    r"\blearning opportunities\b",
    r"\bcounterfeit watches?\b",
    r"\bseized? counterfeit\b",
    r"\bcommunity contributors\b",
]
DEFAULT_BOILERPLATE_PATTERNS = [
    r"continue reading\.{0,3}",
    r"appeared first on [^.]+\.?",
]
BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}

# 域名级速率限制：记录每个域名最后一次请求的时间
_domain_last_request: dict[str, float] = {}
_RATE_LIMIT_SECONDS = 2.0
_MAX_RETRIES = 3
_RETRY_BASE_DELAY = 1.0


def _rate_limit(url: str) -> None:
    """在请求之前执行域名级速率限制。"""
    domain = urlparse(url).netloc
    if not domain:
        return
    last = _domain_last_request.get(domain, 0.0)
    elapsed = time.time() - last
    if elapsed < _RATE_LIMIT_SECONDS:
        time.sleep(_RATE_LIMIT_SECONDS - elapsed)
    _domain_last_request[domain] = time.time()


def fetch_url(url: str) -> bytes:
    """抓取 URL 内容，支持指数退避重试和域名级速率限制。"""
    _rate_limit(url)
    req = urllib.request.Request(url, headers=BROWSER_HEADERS)
    ctx = ssl.create_default_context()
    config = load_network_config()
    previous_no_proxy = os.environ.get("no_proxy")
    if config.get("no_proxy"):
        os.environ["no_proxy"] = config["no_proxy"]
    last_error: Exception | None = None
    try:
        opener = urllib.request.build_opener(
            urllib.request.ProxyHandler(proxy_mapping(config)),
            urllib.request.HTTPSHandler(context=ctx),
        )
        for attempt in range(1, _MAX_RETRIES + 1):
            try:
                with opener.open(req, timeout=20) as resp:
                    return resp.read()
            except Exception as exc:
                last_error = exc
                if attempt < _MAX_RETRIES:
                    delay = _RETRY_BASE_DELAY * (2 ** (attempt - 1))
                    print(f"[fetch_url] 重试 {attempt}/{_MAX_RETRIES} ({url[:80]}): {exc}", file=sys.stderr)
                    time.sleep(delay)
        raise last_error  # type: ignore[misc]
    finally:
        if config.get("no_proxy"):
            if previous_no_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = previous_no_proxy



def load_changedetection_feed_bytes() -> bytes:
    if CHANGEDETECTION_FEED_FILE.exists():
        return CHANGEDETECTION_FEED_FILE.read_bytes()
    raise FileNotFoundError("missing changedetection feed: monitoring/changedetection_feed.xml")


def text_of(node, tag_names: list[str]) -> str | None:
    for tag in tag_names:
        child = node.find(tag)
        if child is not None and child.text:
            return child.text.strip()
    return None


def strip_html(text: str) -> str:
    text = html.unescape(text or "")
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", strip_html(text)).strip()


def is_fresh(published_at: str, freshness_days: int, now: datetime) -> bool:
    return is_within_age(published_at, freshness_days, now)


def relevance_keywords_for_source(source: dict) -> list[str]:
    return source.get("include_keywords") or DEFAULT_RELEVANCE_KEYWORDS


def noise_patterns_for_source(source: dict) -> list[str]:
    return source.get("exclude_patterns") or DEFAULT_NOISE_PATTERNS


def build_signature(title: str, url: str, content: str) -> str:
    basis = "|".join([
        normalize_text(title).lower(),
        url.strip().lower(),
        normalize_text(content).lower()[:280],
    ])
    return hashlib.sha1(basis.encode("utf-8")).hexdigest()


def clean_boilerplate(text: str) -> str:
    cleaned = text
    for pattern in DEFAULT_BOILERPLATE_PATTERNS:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    return normalize_text(cleaned)


def slug_to_title(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return ""
    slug = path.split("/")[-1]
    slug = re.sub(r"[-_]+", " ", slug)
    slug = re.sub(r"\s+", " ", slug).strip()
    return slug.title()


def clean_changedetection_title(title: str, source: dict, content: str) -> str:
    normalized = normalize_text(title)
    if not normalized:
        return source.get("zh_title") or source.get("label") or "官方页面更新"

    generic_prefix = "changedetection.io notification -"
    if normalized.lower().startswith(generic_prefix):
        cleaned = normalized[len(generic_prefix):].strip(" -")
        if cleaned.startswith("http://") or cleaned.startswith("https://"):
            cleaned = ""
        if not cleaned:
            return source.get("zh_title") or source.get("label") or "官方页面更新"

    if normalized.lower().startswith(generic_prefix):
        return source.get("zh_title") or source.get("label") or "官方页面更新"

    return normalized


def clean_changedetection_content(title: str, content: str, source: dict) -> str:
    normalized = normalize_text(content)
    prefix = normalize_text(title)
    if prefix and normalized.lower().startswith(prefix.lower()):
        normalized = normalized[len(prefix):].strip(" -")
    if not normalized:
        return source.get("why_it_matters") or source.get("label") or "官方页面发生更新"
    return normalized


def sample_event_summary(event: dict) -> dict:
    return {
        "title": normalize_text(event.get("title", ""))[:180],
        "url": event.get("url"),
        "published_at": event.get("published_at"),
    }


def normalize_article_url(link: str, source: dict) -> str:
    normalized = normalize_text(link)
    if not normalized:
        return ""
    if normalized.startswith("http://") or normalized.startswith("https://"):
        return normalized
    base = str(source.get("content_url") or source.get("url") or "").strip()
    if not base:
        return normalized
    parsed = urlparse(base)
    root = f"{parsed.scheme}://{parsed.netloc}"
    if normalized.startswith("/"):
        return f"{root}{normalized}"
    return f"{root}/{normalized.lstrip('/')}"


def extract_meta_content(html_text: str, patterns: list[str]) -> str:
    for pattern in patterns:
        if not pattern:
            continue
        match = re.search(pattern, html_text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            if match.lastindex:
                return normalize_text(match.group(1))
            return normalize_text(match.group(0))
    return ""


def normalize_listing_date(raw_date: str) -> str:
    normalized = normalize_text(raw_date)
    if not normalized:
        return ""
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(normalized, fmt).replace(tzinfo=timezone.utc).isoformat().replace("+00:00", "Z")
        except ValueError:
            continue
    return normalized


def load_json_object(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, dict) else {}


def should_publish_ingest_snapshot(
    source_status_report: dict,
    failures: list[dict],
    all_events: list[dict],
) -> tuple[bool, str | None]:
    by_source = source_status_report.get("by_source", {})
    stable_layers = {"base-feed", "official-content"}

    stable_success = any(
        isinstance(entry, dict)
        and entry.get("source_layer") in stable_layers
        and entry.get("status") in {"ok", "verified", "empty"}
        for entry in by_source.values()
    )
    stable_broken = [
        entry for entry in by_source.values()
        if isinstance(entry, dict)
        and entry.get("source_layer") in stable_layers
        and entry.get("status") == "broken"
    ]
    transient_errors = [
        str(entry.get("error") or "")
        for entry in stable_broken
        if any(
            token in str(entry.get("error") or "").lower()
            for token in [
                "operation not permitted",
                "temporarily unavailable",
                "name or service not known",
                "nodename nor servname provided",
                "connection refused",
                "timed out",
            ]
        )
    ]

    if not all_events and failures:
        return False, "all sources failed; preserved previous real-event snapshot"
    if stable_broken and not stable_success and transient_errors:
        return False, "stable content sources were unavailable; preserved previous ingest snapshot"
    return True, None


def parse_article_detail(article_url: str, fallback_title: str, source: dict, now: datetime, fallback_published_at: str = "") -> dict | None:
    article_html = fetch_url(article_url).decode("utf-8", errors="ignore")
    title = extract_meta_content(
        article_html,
        [
            r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"',
            r'<meta[^>]+name="twitter:title"[^>]+content="([^"]+)"',
            r"<title>(.*?)</title>",
        ],
    ) or normalize_text(fallback_title) or slug_to_title(article_url)
    summary = extract_meta_content(
        article_html,
        [
            r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"',
            r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
        ],
    )
    published_at = extract_meta_content(
        article_html,
        [
            r'<meta[^>]+property="article:published_time"[^>]+content="([^"]+)"',
            r'<meta[^>]+name="article:published_time"[^>]+content="([^"]+)"',
            r'<time[^>]+datetime="([^"]+)"',
            r'"datePublished"\s*:\s*"([^"]+)"',
        ],
    )
    if not published_at:
        visible_date = extract_meta_content(article_html, [r"([A-Z][a-z]+ \d{1,2}, \d{4})"])
        published_at = normalize_listing_date(visible_date)
    canonical_url = extract_meta_content(
        article_html,
        [
            r'<link[^>]+rel="canonical"[^>]+href="([^"]+)"',
            r'<meta[^>]+property="og:url"[^>]+content="([^"]+)"',
        ],
    ) or article_url

    if not published_at:
        published_at = normalize_listing_date(fallback_published_at)
    if not published_at:
        return None

    content = " ".join(part for part in [title, summary] if part).strip()
    if not content:
        content = title

    return {
        "source_id": source["id"],
        "source_label": source["label"],
        "source_topic": source.get("topic", "news"),
        "source_platforms": source.get("platforms", []),
        "source_trust_tier": source.get("trust_tier", "industry"),
        "source_seller_signal_bias": source.get("seller_signal_bias", "medium"),
        "source_priority": source.get("source_priority"),
        "source_type": source.get("source_type"),
        "source_layer": source.get("source_layer", "official-content"),
        "source_display_zh": source.get("zh_title"),
        "source_business_zone": source.get("business_zone", []),
        "source_why_it_matters": source.get("why_it_matters", ""),
        "watchlist_id": source.get("watchlist_id"),
        "title": title,
        "content": clean_boilerplate(content),
        "url": canonical_url,
        "published_at": published_at,
        "fetched_at": now.isoformat(),
    }


def matches_changedetection_source(event: dict, source: dict) -> bool:
    combined = " ".join(
        [
            normalize_text(event.get("title", "")),
            normalize_text(event.get("content", "")),
            normalize_text(event.get("url", "")),
        ]
    ).lower()
    host = str(source.get("routing_host") or "").lower()
    path = str(source.get("routing_path") or "").lower()
    source_url = str(source.get("url") or "").lower()
    if host and host in combined:
        return True
    if path and path != "/" and path in combined:
        return True
    if source_url and source_url in combined:
        return True
    return False


def should_keep_event(event: dict, source: dict, now: datetime) -> tuple[bool, str | None]:
    content = clean_boilerplate(event.get("content", ""))
    title = normalize_text(event.get("title", ""))
    combined = f"{title} {content}".strip().lower()
    min_content_length = int(source.get("min_content_length", DEFAULT_MIN_CONTENT_LENGTH))
    freshness_days = int(source.get("freshness_days", DEFAULT_FRESHNESS_DAYS))

    if not title and not content:
        return False, "empty_content"
    if len(content) < min_content_length:
        return False, "content_too_short"
    if not event.get("url"):
        return False, "missing_url"
    if not is_fresh(event.get("published_at", ""), freshness_days, now):
        return False, "stale"

    for pattern in noise_patterns_for_source(source):
        if re.search(pattern, combined, flags=re.IGNORECASE):
            return False, "noise"

    for pattern in SELLER_OPERATIONAL_NOISE_PATTERNS:
        if re.search(pattern, combined, flags=re.IGNORECASE):
            return False, "noise"

    keywords = [kw.lower() for kw in relevance_keywords_for_source(source)]
    if keywords and not any(keyword in combined for keyword in keywords):
        return False, "low_relevance"

    is_relevant, _, _ = classify_relevance(f"{title} {content}".strip())
    if not is_relevant and source.get("source_layer", "base-feed") == "base-feed":
        return False, "low_relevance"

    return True, None



def parse_rss(xml_bytes: bytes, source: dict, now: datetime, include_audit: bool = False):
    root = ET.fromstring(xml_bytes)
    items = root.findall("./channel/item")
    events = []
    drop_stats: dict[str, int] = {}
    audit = {"kept_samples": [], "dropped_samples": {}}
    seen_signatures: set[str] = set()
    for item in items:
        title = normalize_text(text_of(item, ["title"]) or "")
        link = normalize_text(text_of(item, ["link"]) or "")
        desc = normalize_text(text_of(item, ["description"]) or "")
        pub = normalize_text(text_of(item, ["pubDate"]) or "")
        content = " ".join(x for x in [title, desc] if x).strip()
        event = {
            "source_id": source["id"],
            "source_label": source["label"],
            "source_topic": source.get("topic", "news"),
            "source_platforms": source.get("platforms", []),
            "source_trust_tier": source.get("trust_tier", "industry"),
            "source_seller_signal_bias": source.get("seller_signal_bias", "medium"),
            "source_priority": source.get("source_priority"),
            "source_type": source.get("source_type"),
            "source_layer": source.get("source_layer", "base-feed"),
            "source_display_zh": source.get("zh_title"),
            "source_business_zone": source.get("business_zone", []),
            "source_why_it_matters": source.get("why_it_matters", ""),
            "watchlist_id": source.get("watchlist_id"),
            "title": title,
            "content": content,
            "url": link,
            "published_at": pub,
            "fetched_at": now.isoformat(),
        }
        event["content"] = clean_boilerplate(event["content"])
        keep, reason = should_keep_event(event, source, now)
        if not keep:
            drop_stats[reason] = drop_stats.get(reason, 0) + 1
            if include_audit and reason:
                bucket = audit["dropped_samples"].setdefault(reason, [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        signature = build_signature(title, link, content)
        if signature in seen_signatures:
            drop_stats["duplicate"] = drop_stats.get("duplicate", 0) + 1
            if include_audit:
                bucket = audit["dropped_samples"].setdefault("duplicate", [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        seen_signatures.add(signature)
        events.append(localize_event_payload(event))
        if include_audit and len(audit["kept_samples"]) < MAX_AUDIT_KEPT_SAMPLES:
            audit["kept_samples"].append(sample_event_summary(event))
        if len(events) >= int(source.get("max_items", MAX_ITEMS_PER_SOURCE)):
            break
    if include_audit:
        return events, drop_stats, audit
    return events, drop_stats


def parse_html_forum_listing(html_bytes: bytes, source: dict, now: datetime, include_audit: bool = False):
    html_text = html_bytes.decode("utf-8", errors="ignore")
    card_pattern = re.compile(
        r'<time datetime="(?P<published>[^"]+)"[^>]*>.*?</time>.*?'
        r'<a[^>]+href="(?P<href>/seller-forums/discussions/t/[^"]+)"[^>]*>(?P<title>.*?)</a>.*?'
        r'<div class="search-content-post[^>]*>(?P<snippet>.*?)</div>',
        re.IGNORECASE | re.DOTALL,
    )
    base_url = source.get("base_url", "")
    events = []
    drop_stats: dict[str, int] = {}
    audit = {"kept_samples": [], "dropped_samples": {}}
    seen_signatures: set[str] = set()
    for match in card_pattern.finditer(html_text):
        title = normalize_text(match.group("title"))
        link = normalize_text(match.group("href"))
        if base_url and link.startswith("/"):
            link = f"{base_url.rstrip('/')}{link}"
        desc = normalize_text(match.group("snippet"))
        pub = normalize_text(match.group("published"))
        content = " ".join(x for x in [title, desc] if x).strip()
        event = {
            "source_id": source["id"],
            "source_label": source["label"],
            "source_topic": source.get("topic", "news"),
            "source_platforms": source.get("platforms", []),
            "source_trust_tier": source.get("trust_tier", "industry"),
            "source_seller_signal_bias": source.get("seller_signal_bias", "medium"),
            "source_priority": source.get("source_priority"),
            "source_type": source.get("source_type"),
            "source_layer": source.get("source_layer", "base-feed"),
            "source_display_zh": source.get("zh_title"),
            "source_business_zone": source.get("business_zone", []),
            "source_why_it_matters": source.get("why_it_matters", ""),
            "watchlist_id": source.get("watchlist_id"),
            "title": title,
            "content": content,
            "url": link,
            "published_at": pub,
            "fetched_at": now.isoformat(),
        }
        event["content"] = clean_boilerplate(event["content"])
        keep, reason = should_keep_event(event, source, now)
        if not keep:
            drop_stats[reason] = drop_stats.get(reason, 0) + 1
            if include_audit and reason:
                bucket = audit["dropped_samples"].setdefault(reason, [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        signature = build_signature(title, link, content)
        if signature in seen_signatures:
            drop_stats["duplicate"] = drop_stats.get("duplicate", 0) + 1
            if include_audit:
                bucket = audit["dropped_samples"].setdefault("duplicate", [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        seen_signatures.add(signature)
        events.append(localize_event_payload(event))
        if include_audit and len(audit["kept_samples"]) < MAX_AUDIT_KEPT_SAMPLES:
            audit["kept_samples"].append(sample_event_summary(event))
        if len(events) >= int(source.get("max_items", MAX_ITEMS_PER_SOURCE)):
            break
    if include_audit:
        return events, drop_stats, audit
    return events, drop_stats


def parse_html_article_listing(html_bytes: bytes, source: dict, now: datetime, include_audit: bool = False):
    html_text = html_bytes.decode("utf-8", errors="ignore")
    events = []
    drop_stats: dict[str, int] = {}
    audit = {"kept_samples": [], "dropped_samples": {}}
    seen_signatures: set[str] = set()
    seen_urls: set[str] = set()

    article_url_prefix = str(source.get("article_url_prefix") or "")
    article_link_regex = str(source.get("article_link_regex") or "")
    fetch_limit = int(source.get("article_fetch_limit", source.get("max_items", MAX_ITEMS_PER_SOURCE)))

    anchor_pattern = re.compile(r"<a(?P<attrs>[^>]+)href=\"(?P<href>[^\"]+)\"[^>]*>(?P<body>.*?)</a>", re.IGNORECASE | re.DOTALL)

    candidates: list[tuple[str, str, str]] = []
    for match in anchor_pattern.finditer(html_text):
        href = normalize_article_url(match.group("href"), source)
        if not href:
            continue
        if article_url_prefix and not href.startswith(article_url_prefix):
            continue
        if article_link_regex and not re.search(article_link_regex, match.group("href"), flags=re.IGNORECASE):
            continue
        if href in seen_urls:
            continue
        seen_urls.add(href)
        attrs = match.group("attrs")
        anchor_text = normalize_text(match.group("body"))
        aria_label_match = re.search(r'aria-label="([^"]+)"', attrs, flags=re.IGNORECASE)
        fallback_title = normalize_text(aria_label_match.group(1)) if aria_label_match else anchor_text
        if not fallback_title:
            fallback_title = slug_to_title(href)
        if not fallback_title:
            continue
        listing_context = html_text[max(0, match.start() - 2000):match.start() + 400]
        date_match = re.search(r"([A-Z][a-z]+ \d{1,2}, \d{4})", listing_context)
        fallback_published_at = date_match.group(1) if date_match else ""
        candidates.append((href, fallback_title, fallback_published_at))
        if len(candidates) >= fetch_limit:
            break

    for href, fallback_title, fallback_published_at in candidates:
        event = parse_article_detail(href, fallback_title, source, now, fallback_published_at=fallback_published_at)
        if not event:
            drop_stats["missing_article_metadata"] = drop_stats.get("missing_article_metadata", 0) + 1
            if include_audit:
                bucket = audit["dropped_samples"].setdefault("missing_article_metadata", [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append({"title": fallback_title[:180], "url": href, "published_at": None})
            continue
        keep, reason = should_keep_event(event, source, now)
        if not keep:
            drop_stats[reason] = drop_stats.get(reason, 0) + 1
            if include_audit and reason:
                bucket = audit["dropped_samples"].setdefault(reason, [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        signature = build_signature(event["title"], event["url"], event["content"])
        if signature in seen_signatures:
            drop_stats["duplicate"] = drop_stats.get("duplicate", 0) + 1
            if include_audit:
                bucket = audit["dropped_samples"].setdefault("duplicate", [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        seen_signatures.add(signature)
        events.append(localize_event_payload(event))
        if include_audit and len(audit["kept_samples"]) < MAX_AUDIT_KEPT_SAMPLES:
            audit["kept_samples"].append(sample_event_summary(event))
        if len(events) >= int(source.get("max_items", MAX_ITEMS_PER_SOURCE)):
            break

    if include_audit:
        return events, drop_stats, audit
    return events, drop_stats


def parse_html_page_snapshot(html_bytes: bytes, source: dict, now: datetime, include_audit: bool = False):
    html_text = html_bytes.decode("utf-8", errors="ignore")
    drop_stats: dict[str, int] = {}
    audit = {"kept_samples": [], "dropped_samples": {}}

    title = extract_meta_content(
        html_text,
        [
            str(source.get("snapshot_title_regex") or ""),
            r'<meta[^>]+property="og:title"[^>]+content="([^"]+)"',
            r'<meta[^>]+name="twitter:title"[^>]+content="([^"]+)"',
            r"<title>(.*?)</title>",
            r"<h1[^>]*>(.*?)</h1>",
        ],
    ) or normalize_text(source.get("label") or source.get("zh_title") or "官方页面更新")

    summary = extract_meta_content(
        html_text,
        [
            r'<meta[^>]+name="description"[^>]+content="([^"]+)"',
            r'<meta[^>]+property="og:description"[^>]+content="([^"]+)"',
        ],
    )
    published_at = extract_meta_content(
        html_text,
        [
            str(source.get("published_regex") or ""),
            r"Updated:\s*([A-Z][a-z]+ \d{1,2}, \d{4})",
            r"Last update:\s*([A-Z][a-z]+ \d{1,2}, \d{4})",
            r'<time[^>]+datetime="([^"]+)"',
        ],
    )
    published_at = normalize_listing_date(published_at)

    focus = extract_meta_content(
        html_text,
        [
            str(source.get("content_focus_regex") or ""),
            r"<main[\s\S]*?</main>",
            r"<body[\s\S]*?</body>",
        ],
    )
    if not focus:
        focus = summary or title
    focus = clean_boilerplate(focus)
    content = " ".join(part for part in [title, summary, focus] if part).strip()
    event = {
        "source_id": source["id"],
        "source_label": source["label"],
        "source_topic": source.get("topic", "news"),
        "source_platforms": source.get("platforms", []),
        "source_trust_tier": source.get("trust_tier", "industry"),
        "source_seller_signal_bias": source.get("seller_signal_bias", "medium"),
        "source_priority": source.get("source_priority"),
        "source_type": source.get("source_type"),
        "source_layer": source.get("source_layer", "official-content"),
        "source_display_zh": source.get("zh_title"),
        "source_business_zone": source.get("business_zone", []),
        "source_why_it_matters": source.get("why_it_matters", ""),
        "watchlist_id": source.get("watchlist_id"),
        "title": title,
        "content": content[:4000],
        "url": str(source.get("content_url") or source.get("url") or ""),
        "published_at": published_at,
        "fetched_at": now.isoformat(),
    }
    keep, reason = should_keep_event(event, source, now)
    if not keep:
        drop_stats[reason] = drop_stats.get(reason, 0) + 1
        if include_audit and reason:
            audit["dropped_samples"].setdefault(reason, []).append(sample_event_summary(event))
        return ([], drop_stats, audit) if include_audit else ([], drop_stats)

    localized = localize_event_payload(event)
    if include_audit:
        audit["kept_samples"].append(sample_event_summary(event))
        return [localized], drop_stats, audit
    return [localized], drop_stats


def parse_changedetection_feed(xml_bytes: bytes, source: dict, now: datetime, include_audit: bool = False):
    root = ET.fromstring(xml_bytes)
    items = root.findall("./channel/item")
    events = []
    drop_stats: dict[str, int] = {}
    audit = {"kept_samples": [], "dropped_samples": {}}
    seen_signatures: set[str] = set()
    for item in items:
        raw_title = normalize_text(text_of(item, ["title"]) or "")
        link = normalize_text(text_of(item, ["link"]) or "")
        desc = normalize_text(text_of(item, ["description"]) or "")
        pub = normalize_text(text_of(item, ["pubDate"]) or "")
        title = clean_changedetection_title(raw_title, source, desc)
        cleaned_desc = clean_changedetection_content(raw_title, desc, source)
        content = " ".join(x for x in [title, cleaned_desc] if x).strip()
        event = {
            "source_id": source["id"],
            "source_label": source["label"],
            "source_topic": source.get("topic", "news"),
            "source_platforms": source.get("platforms", []),
            "source_trust_tier": source.get("trust_tier", "industry"),
            "source_seller_signal_bias": source.get("seller_signal_bias", "medium"),
            "source_priority": source.get("source_priority"),
            "source_type": source.get("source_type"),
            "source_layer": source.get("source_layer", "official-watchlist"),
            "source_display_zh": source.get("zh_title"),
            "source_business_zone": source.get("business_zone", []),
            "source_why_it_matters": source.get("why_it_matters", ""),
            "watchlist_id": source.get("watchlist_id"),
            "title": title,
            "content": content,
            "url": link,
            "published_at": pub,
            "fetched_at": now.isoformat(),
        }
        if not matches_changedetection_source(event, source):
            continue
        event["content"] = clean_boilerplate(event["content"])
        keep, reason = should_keep_event(event, source, now)
        if not keep:
            drop_stats[reason] = drop_stats.get(reason, 0) + 1
            if include_audit and reason:
                bucket = audit["dropped_samples"].setdefault(reason, [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        signature = build_signature(title, link, content)
        if signature in seen_signatures:
            drop_stats["duplicate"] = drop_stats.get("duplicate", 0) + 1
            if include_audit:
                bucket = audit["dropped_samples"].setdefault("duplicate", [])
                if len(bucket) < MAX_AUDIT_SAMPLES_PER_REASON:
                    bucket.append(sample_event_summary(event))
            continue
        seen_signatures.add(signature)
        events.append(localize_event_payload(event))
        if include_audit and len(audit["kept_samples"]) < MAX_AUDIT_KEPT_SAMPLES:
            audit["kept_samples"].append(sample_event_summary(event))
        if len(events) >= int(source.get("max_items", MAX_ITEMS_PER_SOURCE)):
            break
    if include_audit:
        return events, drop_stats, audit
    return events, drop_stats


def main() -> int:
    ensure_runtime_data_dir()
    now = datetime.now(timezone.utc)
    all_events = []
    failures = []
    quality_report = {"kept": 0, "dropped": {}, "by_source": {}}
    audit_report = {"generated_at": now.isoformat(), "by_source": {}}
    source_status_report = {"generated_at": now.isoformat(), "by_source": {}}
    global_signatures: set[str] = set()

    for source in load_executable_sources():
        try:
            if source["type"] == "rss":
                raw = fetch_url(source["url"])
                source_events, drop_stats, source_audit = parse_rss(raw, source, now, include_audit=True)
            elif source["type"] == "html_forum_listing":
                raw = fetch_url(source["url"])
                source_events, drop_stats, source_audit = parse_html_forum_listing(raw, source, now, include_audit=True)
            elif source["type"] == "html_article_listing":
                raw = fetch_url(source["url"])
                source_events, drop_stats, source_audit = parse_html_article_listing(raw, source, now, include_audit=True)
            elif source["type"] == "html_page_snapshot":
                raw = fetch_url(source["url"])
                source_events, drop_stats, source_audit = parse_html_page_snapshot(raw, source, now, include_audit=True)
            elif source["type"] == "changedetection_rss":
                raw = load_changedetection_feed_bytes()
                source_events, drop_stats, source_audit = parse_changedetection_feed(raw, source, now, include_audit=True)
            else:
                failures.append({"source": source["id"], "error": "unsupported source type"})
                continue

            kept_events = []
            for event in source_events:
                signature = build_signature(event["title"], event["url"], event["content"])
                if signature in global_signatures:
                    drop_stats["duplicate"] = drop_stats.get("duplicate", 0) + 1
                    continue
                global_signatures.add(signature)
                kept_events.append(event)
            all_events.extend(kept_events)
            quality_report["by_source"][source["id"]] = {
                "kept": len(kept_events),
                "dropped": drop_stats,
            }
            audit_report["by_source"][source["id"]] = {
                "label": source["label"],
                "topic": source.get("topic", "news"),
                "trust_tier": source.get("trust_tier", "industry"),
                "seller_signal_bias": source.get("seller_signal_bias", "medium"),
                "kept_count": len(kept_events),
                "drop_counts": drop_stats,
                "kept_samples": source_audit["kept_samples"],
                "dropped_samples": source_audit["dropped_samples"],
            }
            status = "verified" if source.get("source_layer") == "official-content" and kept_events else "ok"
            if source.get("source_layer") == "official-content" and not kept_events:
                status = "empty"
            source_status_report["by_source"][source["id"]] = {
                "label": source["label"],
                "source_layer": source.get("source_layer", "base-feed"),
                "source_type": source.get("source_type"),
                "monitoring_method": source.get("monitoring_method"),
                "status": status,
                "kept_count": len(kept_events),
                "drop_counts": drop_stats,
                "last_checked_at": now.isoformat(),
            }
            quality_report["kept"] += len(kept_events)
            for key, value in drop_stats.items():
                quality_report["dropped"][key] = quality_report["dropped"].get(key, 0) + value
        except Exception as exc:
            failures.append({"source": source["id"], "error": str(exc)})
            source_status_report["by_source"][source["id"]] = {
                "label": source["label"],
                "source_layer": source.get("source_layer", "base-feed"),
                "source_type": source.get("source_type"),
                "monitoring_method": source.get("monitoring_method"),
                "status": "broken",
                "kept_count": 0,
                "drop_counts": {},
                "last_checked_at": now.isoformat(),
                "error": str(exc),
            }
            audit_report["by_source"][source["id"]] = {
                "label": source["label"],
                "topic": source.get("topic", "news"),
                "trust_tier": source.get("trust_tier", "industry"),
                "seller_signal_bias": source.get("seller_signal_bias", "medium"),
                "error": str(exc),
            }

    payload = {
        "generated_at": now.isoformat(),
        "event_count": len(all_events),
        "events": all_events,
        "failures": failures,
        "quality_report": quality_report,
    }
    should_publish, preserve_reason = should_publish_ingest_snapshot(source_status_report, failures, all_events)
    previous_output = load_json_object(OUTPUT_FILE)
    previous_source_status = load_json_object(SOURCE_STATUS_FILE)
    if should_publish:
        temp_path = OUTPUT_FILE.with_suffix(".json.tmp")
        temp_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp_path.replace(OUTPUT_FILE)
    audit_temp_path = AUDIT_FILE.with_suffix(".json.tmp")
    audit_temp_path.write_text(json.dumps(audit_report, ensure_ascii=False, indent=2), encoding="utf-8")
    audit_temp_path.replace(AUDIT_FILE)
    if should_publish:
        source_status_temp_path = SOURCE_STATUS_FILE.with_suffix(".json.tmp")
        source_status_temp_path.write_text(json.dumps(source_status_report, ensure_ascii=False, indent=2), encoding="utf-8")
        source_status_temp_path.replace(SOURCE_STATUS_FILE)
    else:
        payload["preserved_previous_snapshot"] = bool(previous_output)
        payload["preserved_previous_source_status"] = bool(previous_source_status)
        payload["warning"] = preserve_reason
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if all_events or not should_publish else 1


if __name__ == "__main__":
    raise SystemExit(main())
