#!/usr/bin/env python3
"""适用性分层模块：按履约路径分层评估事件影响。"""
from morning_brief_constants import FULFILLMENT_PATHS


def platform_modifier_label(profile: dict) -> str:
    platform = profile.get("platform")
    platform_map = {
        "amazon": "Amazon",
        "tiktok-shop": "TikTok Shop",
        "independent-site": "独立站",
        "general": "全平台扫描",
    }
    return platform_map.get(platform, str(platform or "unknown"))


def fulfillment_path_key(profile: dict) -> str:
    fulfillment = profile.get("fulfillment_model")
    if fulfillment == "direct-mail":
        return "crossborder-direct-mail"
    if fulfillment in {"fba", "platform-fulfillment"}:
        return "local-fulfillment-platform-led"
    if fulfillment == "overseas-warehouse":
        return "local-fulfillment-merchant-led"
    return "mixed-fulfillment"


def fulfillment_path_label(profile: dict) -> str:
    path_key = fulfillment_path_key(profile)
    if path_key == "crossborder-direct-mail":
        return "跨境直发"
    if path_key == "local-fulfillment-platform-led":
        return "本地履约-平台主导"
    if path_key == "local-fulfillment-merchant-led":
        return "本地履约-3PL/商家主导"
    return "混合履约"


def normalize_fulfillment_path(profile: dict) -> str:
    return fulfillment_path_label(profile)


def applicability_tier_label(level: str) -> str:
    mapping = {
        "high": "高相关",
        "medium": "中相关",
        "low": "低相关/观察",
    }
    return mapping.get(level, level)


def applicability_label_for_path(path_key: str, result: dict, profile: dict) -> str:
    platform = platform_modifier_label(profile)
    market = profile.get("market", "unknown")
    if path_key == "crossborder-direct-mail":
        if result.get("event_type") == "tariff":
            return f"跨境直发（平台修正：{platform} / 市场修正：{market} / 税后到手价与毛利最敏感）"
        if result.get("event_type") == "logistics":
            return f"跨境直发（平台修正：{platform} / 市场修正：{market} / 时效、签收、退款链路最敏感）"
        return f"跨境直发（平台修正：{platform} / 市场修正：{market}）"
    if path_key == "local-fulfillment-platform-led":
        return f"本地履约-平台主导（平台修正：{platform} / 市场修正：{market} / 重点看定价、补货、平台仓规则）"
    if path_key == "local-fulfillment-merchant-led":
        return f"本地履约-3PL/商家主导（平台修正：{platform} / 市场修正：{market} / 重点看仓储、清关、尾程）"
    return f"混合履约（平台修正：{platform} / 市场修正：{market}）"


def applicability_level_for_path(result: dict, path_key: str, profile: dict) -> str:
    event_type = result.get("event_type")
    region = str(result.get("region") or "")
    market = str(profile.get("market") or "")
    in_europe = bool(market and market.upper() in {"EU", "DE", "FR", "IT", "ES", "NL", "BE", "PL"})

    if event_type == "tariff" and region == "EU":
        if path_key == "crossborder-direct-mail" and in_europe:
            return "high"
        if path_key == "local-fulfillment-platform-led" and in_europe:
            return "medium"
        if path_key == "local-fulfillment-merchant-led" and in_europe:
            return "low"
        return "low"

    if event_type == "logistics":
        if path_key == "crossborder-direct-mail":
            return "high"
        if path_key == "local-fulfillment-merchant-led":
            return "medium"
        return "medium"

    if event_type in {"environment", "compliance"}:
        if path_key == "crossborder-direct-mail":
            return "medium"
        return "high"

    if result.get("risk_level") == "high":
        return "medium"
    if result.get("risk_level") == "low":
        return "low"
    return "medium"


def build_applicability_layers(result: dict, profile: dict) -> dict:
    buckets = {"high": [], "medium": [], "low": []}
    for item in FULFILLMENT_PATHS:
        level = applicability_level_for_path(result, item["key"], profile)
        buckets[level].append(applicability_label_for_path(item["key"], result, profile))

    general_mode = profile.get("platform") == "general" and profile.get("fulfillment_model") == "mixed"
    current_path = "通用雷达首页" if general_mode else normalize_fulfillment_path(profile)
    current_level = applicability_level_for_path(result, fulfillment_path_key(profile), profile)
    current_label = "首页总览" if general_mode else applicability_tier_label(current_level)
    return {
        "current_view": {
            "path": current_path,
            "level": current_level,
            "label": current_label,
        },
        "high_relevance": buckets["high"],
        "medium_relevance": buckets["medium"],
        "low_relevance_or_watch": buckets["low"],
    }


def build_fulfillment_actions(results: list[dict], profile: dict) -> list[dict]:
    top_event = results[0] if results else {}
    top_title = top_event.get("event_title", "当前置顶风险")
    top_type = top_event.get("event_type", "policy")
    from brief_builder import collect_watch_items
    shared_watch = collect_watch_items(results)
    base_modifier = f"平台修正：{profile.get('platform', 'unknown')} / 市场修正：{profile.get('market', 'unknown')}"

    LLM_KEY_MAP = {
        "crossborder-direct-mail": "direct_mail",
        "local-fulfillment-platform-led": "platform_led",
        "local-fulfillment-merchant-led": "merchant_led",
    }
    llm_sop = top_event.get("llm_sop", {})
    if not isinstance(llm_sop, dict):
        llm_sop = {}

    fallback_actions = {
        "crossborder-direct-mail": [
            "先重算税后到手价、毛利率和退款缓冲，别让低客单 SKU 悄悄转负。",
            f"紧盯 {top_title} 的正式细则和执行时间，避免广告继续把亏损放大。",
        ],
        "local-fulfillment-platform-led": [
            "先复核平台仓配链路的价格带、补货节奏和承诺时效，确认安全垫还在不在。",
            f"把 {top_type} 风险翻译成平台内动作：提价、控量、调补货，不要只看新闻标题。",
        ],
        "local-fulfillment-merchant-led": [
            "立即盘点站点在途库存与库容利用率，防范政策突变引发的仓储费异动。",
            f"针对 {top_title} 预留备用清关行联系方式，评估核心 SKU 是否需前置拨备。",
        ],
    }
    fallback_watchouts = {
        "crossborder-direct-mail": [f"密切关注 {top_title} 的最终执行日期和适用品类。"],
        "local-fulfillment-platform-led": [f"留意平台是否因 {top_title} 调整仓配规则或绩效门槛。"],
        "local-fulfillment-merchant-led": [f"自发货路径优先关注 {top_title} 对清关和尾程时效的影响。"],
    }

    output = []
    for item in FULFILLMENT_PATHS:
        path_key = item["key"]
        llm_key = LLM_KEY_MAP.get(path_key, "")
        llm_path = llm_sop.get(llm_key, {}) if llm_key else {}
        if not isinstance(llm_path, dict):
            llm_path = {}
        llm_acts = llm_path.get("actions", [])
        if isinstance(llm_acts, list) and len(llm_acts) >= 2:
            actions = [str(a) for a in llm_acts]
        else:
            actions = fallback_actions.get(path_key, ["继续观察细则变化"])
        llm_w = llm_path.get("watchout", "")
        if isinstance(llm_w, str) and llm_w.strip():
            watchouts = [llm_w.strip()]
        else:
            watchouts = fallback_watchouts.get(path_key, shared_watch[:1])
        output.append({
            "path_key": path_key,
            "path_label": item["label"],
            "path_description": item["description"],
            "actions": actions,
            "watchouts": watchouts,
            "modifier": base_modifier,
        })
    return output


def build_layer_actions(result: dict, profile: dict) -> dict:
    path_actions = {item["path_key"]: item for item in build_fulfillment_actions([result], profile)}
    layer_actions = {"high": [], "medium": [], "low": []}
    for item in FULFILLMENT_PATHS:
        level = applicability_level_for_path(result, item["key"], profile)
        action_set = path_actions.get(item["key"], {})
        top_action = (action_set.get("actions") or ["继续观察细则变化"])[0]
        layer_actions[level].append(f"{item['label']}：{top_action}")
    return {
        "high": layer_actions["high"],
        "medium": layer_actions["medium"],
        "low": layer_actions["low"],
    }
