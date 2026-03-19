#!/usr/bin/env python3
"""晨报常量定义模块：集中管理所有评分权重、预设画像和标签映射。"""
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_ROOT = SCRIPT_DIR.parent
EXAMPLES_DIR = SKILL_ROOT / "examples"

DEFAULT_PROFILE = {
    "platform": None,
    "fulfillment_model": None,
    "market": None,
    "price_band": None,
    "category": "general",
    "risk_profile": "general",
}

GENERAL_RADAR_PROFILE = {
    "platform": "general",
    "fulfillment_model": "mixed",
    "market": "EU",
    "price_band": "medium",
    "category": "general",
    "risk_profile": "general",
}

PROFILE_PRESETS = {
    "amazon-fba": {
        "platform": "amazon",
        "fulfillment_model": "fba",
        "market": "DE",
        "price_band": "medium",
        "category": "general",
        "risk_profile": "general",
    },
    "overseas-warehouse": {
        "platform": "amazon",
        "fulfillment_model": "overseas-warehouse",
        "market": "DE",
        "price_band": "medium",
        "category": "home",
        "risk_profile": "general",
    },
    "tiktok-direct-mail": {
        "platform": "tiktok-shop",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    },
    "independent-site-direct-mail": {
        "platform": "independent-site",
        "fulfillment_model": "direct-mail",
        "market": "EU",
        "price_band": "low",
        "category": "general",
        "risk_profile": "margin-sensitive",
    },
}

PRESET_ALIASES = {
    "amazon_fba": "amazon-fba",
    "amazon fba": "amazon-fba",
    "fba": "amazon-fba",
    "amazon": "amazon-fba",
    "overseas_warehouse": "overseas-warehouse",
    "overseas warehouse": "overseas-warehouse",
    "warehouse": "overseas-warehouse",
    "amazon-overseas-warehouse": "overseas-warehouse",
    "tiktok direct-mail": "tiktok-direct-mail",
    "tiktok direct mail": "tiktok-direct-mail",
    "tiktok_shop_direct_mail": "tiktok-direct-mail",
    "tiktok-shop": "tiktok-direct-mail",
    "tiktok": "tiktok-direct-mail",
    "independent-site direct-mail": "independent-site-direct-mail",
    "independent site direct mail": "independent-site-direct-mail",
    "independent_site_direct_mail": "independent-site-direct-mail",
    "shopify-direct-mail": "independent-site-direct-mail",
    "dtc-direct-mail": "independent-site-direct-mail",
    "independent-site": "independent-site-direct-mail",
}

PROFILE_LABELS = {
    "amazon-fba": "本地履约-平台主导（平台修正：Amazon / 市场：德国站）",
    "overseas-warehouse": "本地履约-3PL/商家主导（平台修正：Amazon / 市场：德国站）",
    "tiktok-direct-mail": "跨境直发（平台修正：TikTok Shop / 市场：欧盟低客单）",
    "independent-site-direct-mail": "跨境直发（平台修正：独立站 / 市场：欧盟低客单）",
}

SEED_FILE = SCRIPT_DIR / "seed_events.json"
MAX_REAL_SNAPSHOT_AGE_HOURS = 18
RISK_SCORES = {"high": 120, "medium": 70, "low": 20}
CONFIDENCE_SCORES = {"high": 24, "medium": 12, "low": -12}
SOURCE_TOPIC_BONUS = {
    "tariff": 28,
    "compliance": 24,
    "policy": 20,
    "customs": 22,
    "environment": 8,
    "logistics": 5,
}
TOPIC_PRIORITY_BONUS = {
    "tariff": 30,
    "compliance": 26,
    "customs": 28,
    "policy": 18,
    "logistics": 10,
    "environment": 8,
    "holiday": 2,
    "news": -10,
}
SOURCE_BASE_WEIGHTS = {
    "wto-latest-news": 22,
    "wto": 22,
    "reuters": 18,
    "guardian-world": 12,
    "freightwaves": 10,
    "cbp": 25,
    "customs": 20,
    "eu-taxud": 22,
}
SOURCE_TRUST_TIER_BONUS = {
    "official": 12,
    "platform-official": 14,
    "industry": 4,
    "media": 2,
}
SOURCE_SELLER_SIGNAL_BIAS_BONUS = {
    "high": 10,
    "medium": 4,
    "low": 0,
}
SOURCE_LAYER_BONUS = {
    "policy-watch": 52,
    "official-content": 40,
    "official-watchlist": 16,
    "base-feed": 0,
}
PLATFORM_SCORE_LABELS = {
    "amazon": "Amazon",
    "tiktok-shop": "TikTok",
    "temu": "Temu",
    "independent-site": "独立站",
    "general": "全平台扫描",
}
OFFICIAL_SOURCE_HINTS = ("wto", "commission", "customs", "ministry", "government", "official")
POLICY_SOURCE_HINTS = ("wto", "reuters", "guardian", "commission", "customs", "ministry", "government")
LOGISTICS_SOURCE_HINTS = ("freightwaves", "lloyd", "port", "shipping")
SELLER_OPERATIONAL_SIGNAL_TOKENS = (
    "seller", "sellers", "merchant", "marketplace", "direct-mail", "direct mail",
    "parcel", "low-value", "low value", "customs", "tariff", "duty", "clearance",
    "fulfillment", "inventory", "replenishment", "cross-border", "e-commerce",
    "ecommerce", "amazon", "tiktok shop",
)
MACRO_NOISE_TOKENS = (
    "b2b", "oil", "costco", "fortune 500", "enterprise", "corporate",
    "shareholder", "earnings", "quarterly", "investor",
)
ENTERPRISE_OPERATIONS_NOISE_TOKENS = (
    "reusable packaging", "reusable shipping boxes", "closed-loop shipping",
    "closed loop shipping", "distribution operations", "between facilities",
    "handling efficiency", "returnity", "b2b shipments", "introduced a design",
)
HARD_NOISE_PATTERNS = (
    r"\bcounterfeit\b", r"\bbogus watches?\b", r"\bintercepted by cbp\b",
    r"\bseize(?:d|s)?\b", r"\brecord quarter\b", r"\bquarterly earnings\b",
    r"\bacquisition\b", r"\bmarketing team\b", r"\bshop direct\b",
    r"\bbuy for me\b", r"\brecognition cycle\b", r"\bapplicants can expect next\b",
)
HALF_LIFE_HOURS_BY_TOPIC = {
    "tariff": 168,
    "compliance": 168,
    "policy": 168,
    "customs": 168,
    "environment": 168,
    "logistics": 72,
    "holiday": 72,
    "news": 48,
}
TOP_EVENT_LIMIT = 15
FULFILLMENT_PATHS = [
    {
        "key": "crossborder-direct-mail",
        "label": "跨境直发",
        "description": "包裹从境外直发到目标市场，先看税费、到手价、签收和退款链路。",
    },
    {
        "key": "local-fulfillment-platform-led",
        "label": "本地履约-平台主导",
        "description": "平台托管/半托管/FBA 一类，本地仓配能缓冲一部分冲击，但要盯价格带、补货和平台规则。",
    },
    {
        "key": "local-fulfillment-merchant-led",
        "label": "本地履约-3PL/商家主导",
        "description": "商家自控海外仓或 3PL，本地履约更稳，但仓储、清关和尾程协同压力更高。",
    },
]
