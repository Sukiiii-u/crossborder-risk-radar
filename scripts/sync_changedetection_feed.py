#!/usr/bin/env python3
import argparse
import json
import os
import sys
import ssl
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlparse

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from feed_source_config import load_changedetection_source  # noqa: E402
from network_config import load_network_config, proxy_mapping  # noqa: E402
from runtime_paths import CHANGEDETECTION_FEED_FILE  # noqa: E402
from source_registry import load_watchlist  # noqa: E402


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Sync a changedetection RSS feed into the radar project's canonical local snapshot file."
    )
    parser.add_argument("--from-file", dest="from_file", help="Read changedetection RSS XML from a local file")
    parser.add_argument("--from-url", dest="from_url", help="Download changedetection RSS XML from a URL")
    return parser.parse_args()


def read_feed_bytes(args: argparse.Namespace) -> bytes:
    from_file = args.from_file
    from_url = args.from_url
    if not from_file and not from_url:
        configured = load_changedetection_source()
        if configured["mode"] == "file":
            from_file = configured["source"]
        else:
            from_url = configured["source"]
    elif bool(from_file) == bool(from_url):
        raise ValueError("provide exactly one of --from-file or --from-url")

    if from_file:
        return Path(from_file).read_bytes()

    config = load_network_config()
    previous_no_proxy = os.environ.get("no_proxy")
    if config.get("no_proxy"):
        os.environ["no_proxy"] = config["no_proxy"]
    req = urllib.request.Request(from_url, headers={"User-Agent": "crossborder-risk-radar/0.1"})
    opener = urllib.request.build_opener(
        urllib.request.ProxyHandler(proxy_mapping(config)),
        urllib.request.HTTPSHandler(context=ssl.create_default_context()),
    )
    try:
        with opener.open(req, timeout=20) as resp:
            return resp.read()
    finally:
        if config.get("no_proxy"):
            if previous_no_proxy is None:
                os.environ.pop("no_proxy", None)
            else:
                os.environ["no_proxy"] = previous_no_proxy


def watchlist_patterns() -> list[tuple[str, str, str]]:
    patterns: list[tuple[str, str, str]] = []
    for item in load_watchlist():
        url = str(item.get("url") or "").strip()
        if not url.startswith("https://"):
            continue
        parsed = urlparse(url)
        patterns.append((url.lower(), parsed.netloc.lower(), (parsed.path or "/").lower()))
    return patterns


def item_matches_watchlist(text: str, patterns: list[tuple[str, str, str]]) -> bool:
    combined = text.lower()
    for full_url, host, path in patterns:
        if full_url in combined:
            return True
        if host and host in combined:
            return True
        if path and path != "/" and path in combined:
            return True
    return False


def filter_feed_bytes(payload: bytes) -> tuple[bytes, int]:
    patterns = watchlist_patterns()
    root = ET.fromstring(payload)
    channel = root.find("./channel")
    if channel is None:
        return payload, 0

    kept = 0
    for item in list(channel.findall("item")):
        text = " ".join(
            part or ""
            for part in [
                item.findtext("title"),
                item.findtext("link"),
                item.findtext("description"),
            ]
        )
        if item_matches_watchlist(text, patterns):
            kept += 1
            continue
        channel.remove(item)

    return ET.tostring(root, encoding="utf-8", xml_declaration=True), kept


def main() -> int:
    try:
        args = parse_args()
        payload = read_feed_bytes(args)
        if b"<rss" not in payload and b"<feed" not in payload:
            raise ValueError("input does not look like RSS/Atom XML")
        filtered_payload, kept_items = filter_feed_bytes(payload)

        CHANGEDETECTION_FEED_FILE.parent.mkdir(parents=True, exist_ok=True)
        CHANGEDETECTION_FEED_FILE.write_bytes(filtered_payload)
        print(
            json.dumps(
                {
                    "synced": str(CHANGEDETECTION_FEED_FILE),
                    "bytes": len(filtered_payload),
                    "kept_items": kept_items,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
