#!/usr/bin/env python3
"""评分排序引擎：事件评分和排序逻辑。"""
import math
import re
from datetime import datetime, timezone

from morning_brief_constants import (
    CONFIDENCE_SCORES,
    ENTERPRISE_OPERATIONS_NOISE_TOKENS,
    HALF_LIFE_HOURS_BY_TOPIC,
    HARD_NOISE_PATTERNS,
    LOGISTICS_SOURCE_HINTS,
    MACRO_NOISE_TOKENS,
    OFFICIAL_SOURCE_HINTS,
    PLATFORM_SCORE_LABELS,
    POLICY_SOURCE_HINTS,
    RISK_SCORES,
    SELLER_OPERATIONAL_SIGNAL_TOKENS,
    SOURCE_BASE_WEIGHTS,
    SOURCE_LAYER_BONUS,
    SOURCE_SELLER_SIGNAL_BIAS_BONUS,
    SOURCE_TOPIC_BONUS,
    SOURCE_TRUST_TIER_BONUS,
    TOP_EVENT_LIMIT,
    TOPIC_PRIORITY_BONUS,
)
from applicability import build_applicability_layers, build_layer_actions
from brief_builder import event_seller_angle, parse_datetime


def source_strength(result: dict) -> tuple[int, dict]:
    source_id = str(result.get("source_id") or "").lower()
    source_label = str(result.get("source_label") or "").lower()
    source_text = f"{source_id} {source_label}".strip()
    topic = str(result.get("source_topic") or result.get("source_theme") or result.get("event_type") or "policy").lower()
    trust_tier = str(result.get("source_trust_tier") or "").lower()
    seller_signal_bias = str(result.get("source_seller_signal_bias") or "").lower()
    source_layer = str(result.get("source_layer") or "").lower()
    score = SOURCE_BASE_WEIGHTS.get(source_id, 0)
    reasons = {
        "source_base": score,
        "trust_tier_bonus": 0,
        "seller_signal_bias_bonus": 0,
        "source_layer_bonus": 0,
        "official_bonus": 0,
        "source_fit_bonus": 0,
    }

    if trust_tier in SOURCE_TRUST_TIER_BONUS:
        reasons["trust_tier_bonus"] += SOURCE_TRUST_TIER_BONUS[trust_tier]
        score += SOURCE_TRUST_TIER_BONUS[trust_tier]

    if seller_signal_bias in SOURCE_SELLER_SIGNAL_BIAS_BONUS:
        reasons["seller_signal_bias_bonus"] += SOURCE_SELLER_SIGNAL_BIAS_BONUS[seller_signal_bias]
        score += SOURCE_SELLER_SIGNAL_BIAS_BONUS[seller_signal_bias]

    if source_layer in SOURCE_LAYER_BONUS:
        reasons["source_layer_bonus"] += SOURCE_LAYER_BONUS[source_layer]
        score += SOURCE_LAYER_BONUS[source_layer]

    if any(hint in source_text for hint in OFFICIAL_SOURCE_HINTS):
        reasons["official_bonus"] += 12
        score += 12

    if topic in {"tariff", "policy", "compliance", "environment"} and any(hint in source_text for hint in POLICY_SOURCE_HINTS):
        reasons["source_fit_bonus"] += 6
        score += 6
    if topic == "logistics" and any(hint in source_text for hint in LOGISTICS_SOURCE_HINTS):
        reasons["source_fit_bonus"] += 7
        score += 7

    if source_layer == "base-feed" and trust_tier in {"industry", "media"}:
        reasons["source_fit_bonus"] -= 10
        score -= 10

    if source_layer == "official-content" and topic in {"policy", "tariff", "customs", "compliance"}:
        reasons["source_fit_bonus"] += 12
        score += 12
    if source_layer == "policy-watch" and topic in {"policy", "tariff", "customs"}:
        reasons["source_fit_bonus"] += 16
        score += 16

    if result.get("brief_source_mode") == "seed":
        reasons["source_base"] = max(reasons["source_base"], 4)
        score = max(score, 4)

    return score, reasons


def time_decay_bonus(result: dict) -> tuple[int, dict]:
    topic = str(result.get("event_type") or result.get("source_theme") or "policy").lower()
    published_at = parse_datetime(result.get("published_at")) or parse_datetime(result.get("fetched_at"))
    if published_at is None:
        return 0, {"age_hours": None, "freshness_bonus": 0}

    now = parse_datetime(result.get("fetched_at")) or datetime.now(timezone.utc)
    age_hours = max((now - published_at).total_seconds() / 3600, 0.0)
    half_life = HALF_LIFE_HOURS_BY_TOPIC.get(topic, 72)
    bonus = int(round(18 * math.exp(-math.log(2) * age_hours / half_life)))
    return bonus, {"age_hours": round(age_hours, 1), "freshness_bonus": bonus}


def content_signal_adjustment(result: dict) -> tuple[int, dict]:
    haystack = " ".join([
        str(result.get("event_title") or ""),
        str(result.get("event_summary") or ""),
        str(result.get("relevance_reason") or ""),
    ]).lower()
    event_type = str(result.get("event_type") or result.get("source_theme") or "").lower()
    source_layer = str(result.get("source_layer") or "")
    trust_tier = str(result.get("source_trust_tier") or "").lower()
    seller_hits = [token for token in SELLER_OPERATIONAL_SIGNAL_TOKENS if token in haystack]
    macro_hits = [token for token in MACRO_NOISE_TOKENS if token in haystack]
    enterprise_hits = [token for token in ENTERPRISE_OPERATIONS_NOISE_TOKENS if token in haystack]
    hard_noise_hits = [pattern for pattern in HARD_NOISE_PATTERNS if re.search(pattern, haystack, flags=re.IGNORECASE)]

    bonus = min(len(seller_hits), 4) * 12
    penalty = min(len(macro_hits), 4) * 35 # 进一步提高惩罚 (25 -> 35)
    enterprise_penalty = 0
    # 只要不是 P1/P0 的官方源，就执行企业杂讯惩罚
    if event_type in {"environment", "logistics", "news"} and source_layer not in {"policy-watch", "official-content"}:
        enterprise_penalty = min(len(enterprise_hits), 3) * 40 # 再次提高 (30 -> 40)
    hard_noise_penalty = min(len(hard_noise_hits), 3) * 100 # 再次提高 (80 -> 100)
    score = bonus - penalty - enterprise_penalty - hard_noise_penalty
    return score, {
        "seller_signal_bonus": bonus,
        "macro_noise_penalty": penalty,
        "enterprise_noise_penalty": enterprise_penalty,
        "hard_noise_penalty": hard_noise_penalty,
        "seller_signal_hits": seller_hits[:4],
        "macro_noise_hits": macro_hits[:3],
        "enterprise_noise_hits": enterprise_hits[:3],
        "hard_noise_hits": hard_noise_hits[:2],
    }


def score_event(result: dict, profile: dict) -> tuple[int, dict]:
    breakdown = {
        "risk": RISK_SCORES.get(result.get("risk_level"), 0),
        "confidence": CONFIDENCE_SCORES.get(result.get("confidence"), 0),
        "source_topic": SOURCE_TOPIC_BONUS.get(result.get("source_theme"), 0),
        "topic_priority": TOPIC_PRIORITY_BONUS.get(result.get("event_type") or result.get("source_theme"), 0),
        "market_fit": 0,
        "seller_profile": 0,
        "platform_fit": 0,
        "negative_adjustment": 0,
    }
    source_score, source_reasons = source_strength(result)
    time_score, time_reasons = time_decay_bonus(result)
    content_score, content_reasons = content_signal_adjustment(result)
    breakdown["source_strength"] = source_score
    breakdown["source_strength_reason"] = source_reasons
    breakdown["time_decay"] = time_score
    breakdown["time_decay_reason"] = time_reasons
    breakdown["content_signal"] = content_score
    breakdown["content_signal_reason"] = content_reasons

    event_type = result.get("event_type")
    platform = profile.get("platform")
    fulfillment = profile.get("fulfillment_model")
    price_band = profile.get("price_band")
    risk_profile = profile.get("risk_profile")
    region = str(result.get("region") or "")
    market = str(profile.get("market") or "")
    profile_platform = PLATFORM_SCORE_LABELS.get(str(platform or "").lower())
    source_platforms = result.get("source_platforms") or []
    source_platforms = [str(item) for item in source_platforms if str(item).strip()]

    if market and market.upper() in region.upper():
        breakdown["market_fit"] += 12
    if event_type == "tariff" and fulfillment == "direct-mail":
        breakdown["seller_profile"] += 24
    if event_type == "tariff" and price_band == "low":
        breakdown["seller_profile"] += 15
    if event_type == "tariff" and risk_profile == "margin-sensitive":
        breakdown["seller_profile"] += 10
    if event_type == "logistics" and fulfillment in {"direct-mail", "overseas-warehouse", "fba"}:
        breakdown["seller_profile"] += 12
    if str(result.get("source_layer") or "") in {"official-content", "policy-watch"} and event_type in {"policy", "tariff", "customs", "compliance"}:
        breakdown["seller_profile"] += 18
    if event_type in {"environment", "compliance"} and profile.get("category") not in {None, "general"}:
        breakdown["seller_profile"] += 8
    if platform == "independent-site" and event_type in {"tariff", "logistics"}:
        breakdown["seller_profile"] += 8
    if profile_platform and source_platforms:
        # 统一转小写进行匹配，增加容错性
        sp_lower = [s.lower() for s in source_platforms]
        pp_lower = profile_platform.lower()
        if pp_lower in sp_lower:
            breakdown["platform_fit"] += 45 # 大幅提高匹配权重 (18 -> 45)
        elif "全平台扫描" in source_platforms or "all" in sp_lower:
            breakdown["platform_fit"] += 15
        else:
            # 如果明确指定了平台但信源不包含，显著扣分
            breakdown["platform_fit"] -= 25

    summary = str(result.get("event_summary") or "").lower()
    if any(token in summary for token in ["no direct seller-operational impact", "no direct seller"]):
        breakdown["negative_adjustment"] -= 40
    if content_reasons["macro_noise_penalty"] > 0 and content_reasons["seller_signal_bonus"] == 0:
        breakdown["negative_adjustment"] -= 40 # 加大惩罚
    if content_reasons.get("enterprise_noise_penalty", 0) > 0:
        breakdown["negative_adjustment"] -= 50 # 加大惩罚
    if content_reasons.get("hard_noise_penalty", 0) > 0:
        breakdown["negative_adjustment"] -= 100 # 加大惩罚
    if str(result.get("source_layer") or "") in {"", "base-feed"} and event_type in {"logistics", "news"}:
        breakdown["negative_adjustment"] -= 30 # 空 layer 也视为 base-feed 进行降权

    score = sum(value for key, value in breakdown.items() if isinstance(value, int))
    return score, breakdown


def rank_and_select_events(results: list[dict], profile: dict) -> list[dict]:
    for index, result in enumerate(results):
        score, breakdown = score_event(result, profile)
        result["ranking_score"] = score
        result["seller_angle"] = event_seller_angle(result, profile)
        result["applicability_layers"] = build_applicability_layers(result, profile)
        result["layer_actions"] = build_layer_actions(result, profile)
        result["primary_topic"] = result.get("source_theme") or result.get("event_type") or "policy"
        result["ranking_reason"] = {
            "risk_level": result.get("risk_level"),
            "confidence": result.get("confidence"),
            "primary_topic": result.get("primary_topic"),
            "seller_angle": result.get("seller_angle"),
            "score": result.get("ranking_score"),
            "breakdown": breakdown,
        }
        result["_fallback_order"] = index

    ordered = sorted(
        results,
        key=lambda r: (
            -int(r.get("ranking_score", 0)),
            0 if r.get("brief_source_mode") == "real" else 1,
            -(r.get("ranking_reason", {}).get("breakdown", {}).get("source_strength", 0)),
            -(r.get("ranking_reason", {}).get("breakdown", {}).get("time_decay", 0)),
            r.get("_fallback_order", 0),
        ),
    )

    selected: list[dict] = []
    seen_topics: set[str] = set()
    platform_counts: dict[str, int] = {}
    preferred_layers = {"policy-watch", "official-content", "official-watchlist"}
    
    pp_raw = str(profile.get("platform") or "general").lower()
    profile_platform = PLATFORM_SCORE_LABELS.get(pp_raw, pp_raw)
    
    def get_plat(r):
        p = str((r.get("platforms") or ["Other"])[0]).lower()
        for k in ["amazon", "tiktok", "shopee", "walmart", "temu",
                   "aliexpress", "ebay", "lazada", "mercado", "shein", "shopify"]:
            if k in p: return k
        if "跨境通用" in p or "多平台" in p:
            return "general"
        return p

    # 第一阶段：选取官方核心池与 P0 快照（权重最高，且符合平台偏好）
    for result in ordered:
        if len(selected) >= TOP_EVENT_LIMIT: break
        if result.get("ranking_score", 0) < 30: continue 
        p = get_plat(result)
        
        # 如果是专属视角，非匹配平台的官方资讯也要限制比例，保住“专属感”
        is_match = False
        if profile_platform:
            sp = [str(s).lower() for s in (result.get("source_platforms") or [])]
            if profile_platform.lower() in sp or "全平台扫描" in sp or "all" in sp:
                is_match = True
        
        if not is_match and platform_counts.get(p, 0) >= 2: continue

        if str(result.get("source_layer") or "") in preferred_layers:
            selected.append(result)
            platform_counts[p] = platform_counts.get(p, 0) + 1
            seen_topics.add(result.get("primary_topic", "policy"))

    # 第二阶段：补齐其他高价值多样性内容
    for result in ordered:
        if len(selected) >= TOP_EVENT_LIMIT: break
        if result in selected: continue
        if result.get("ranking_score", 0) < 35: continue 
        p = get_plat(result)
        
        # 强制倾向性：如果是专属视角，非匹配平台的内容严控数量
        is_match = False
        if profile_platform:
            sp = [str(s).lower() for s in (result.get("source_platforms") or [])]
            if profile_platform.lower() in sp or "全平台扫描" in sp or "all" in sp:
                is_match = True
        
        if not is_match and platform_counts.get(p, 0) >= 1: continue

        if result.get("primary_topic", "policy") not in seen_topics or len(selected) < 5:
            selected.append(result)
            platform_counts[p] = platform_counts.get(p, 0) + 1
            seen_topics.add(result.get("primary_topic", "policy"))

    # 第三阶段：末尾兜底（仍需满足分值门槛）
    for result in ordered:
        if len(selected) >= TOP_EVENT_LIMIT: break
        if result.get("ranking_score", 0) < 40: continue # 硬分值过滤
        if result not in selected: selected.append(result)

    for rank, result in enumerate(selected[:TOP_EVENT_LIMIT], start=1):
        result.pop("_fallback_order", None)
        result["brief_rank"] = rank

    return selected[:TOP_EVENT_LIMIT]
