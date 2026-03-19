#!/usr/bin/env python3
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SKILL_ROOT = ROOT.parent
CONFIG = SKILL_ROOT / "scripts" / "source_configs.json"


def main() -> int:
    configs = json.loads(CONFIG.read_text(encoding="utf-8"))
    errors = []
    allowed_topics = {"news", "policy", "logistics"}
    allowed_types = {"rss", "html_forum_listing"}
    allowed_trust_tiers = {"industry", "media"}
    allowed_biases = {"high", "medium", "low"}
    allowed_platforms = {"Amazon", "TikTok", "Temu", "独立站", "全平台扫描"}
    topics = set()
    trust_tiers = set()
    if len(configs) < 3:
        errors.append("expected at least 3 sources")
    ids = set()
    for item in configs:
        if not item.get("id"):
            errors.append("missing id")
        if item.get("id") in ids:
            errors.append(f"duplicate id: {item.get('id')}")
        ids.add(item.get("id"))
        if item.get("type") not in allowed_types:
            errors.append(f"unsupported type: {item.get('type')}")
        if not str(item.get("url", "")).startswith("https://"):
            errors.append(f"source url must be https: {item.get('url')}")
        topic = item.get("topic")
        if topic not in allowed_topics:
            errors.append(f"unsupported topic: {topic}")
        else:
            topics.add(topic)
        trust_tier = item.get("trust_tier")
        if trust_tier not in allowed_trust_tiers:
            errors.append(f"unsupported trust_tier: {trust_tier}")
        else:
            trust_tiers.add(trust_tier)
        seller_signal_bias = item.get("seller_signal_bias")
        if seller_signal_bias not in allowed_biases:
            errors.append(f"unsupported seller_signal_bias: {seller_signal_bias}")
        platforms = item.get("platforms")
        if not isinstance(platforms, list) or not platforms:
            errors.append(f"source platforms missing or invalid: {item.get('id')}")
        elif any(platform not in allowed_platforms for platform in platforms):
            errors.append(f"unsupported platform label in {item.get('id')}: {platforms!r}")

    if len(topics) < 2:
        errors.append("expected topic coverage across at least 2 categories")
    if "industry" not in trust_tiers:
        errors.append("expected at least one industry source")

    if errors:
        print("FAIL validate_source_configs")
        for err in errors:
            print(f"- {err}")
        return 1
    print("PASS validate_source_configs")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
