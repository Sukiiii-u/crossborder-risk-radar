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
    from brief_builder import collect_watch_items  # 延迟导入避免循环
    shared_watch = collect_watch_items(results)
    base_modifier = f"平台修正：{profile.get('platform', 'unknown')} / 市场修正：{profile.get('market', 'unknown')}"
    platform = profile.get("platform")
    fulfillment = profile.get("fulfillment_model")

    direct_mail_actions = [
        "先重算税后到手价、毛利率和退款缓冲，别让低客单 SKU 悄悄转负。",
        "把高风险 SKU 标成直发预警名单，今天就评估是否切去本地仓/更换物流方案。",
        f"紧盯 {top_title} 的正式细则和执行时间，避免广告继续把亏损放大。",
    ]
    if platform == "independent-site":
        direct_mail_actions = [
            "先把独立站 EU 直邮价卡、运费模板和毛利底线摆上桌，别让前台还在照旧卖。",
            "把高风险 SKU 拆成留量、提价、停推三档，今天就别再用一个广告策略打天下。",
            f"盯紧 {top_title} 的落地细则，同时看退件率和购物车转化有没有先掉。",
        ]
    elif platform == "tiktok-shop" or fulfillment == "direct-mail":
        direct_mail_actions = [
            "首要行动：立即圈出‘破发’利润边缘的低客单 SKU，同步调整达人建联佣金池，防止由于投流惯性带来的二次亏损。",
            "运营动作：针对 TikTok EU 潜在的合规收紧，储备‘备选白牌’方案，并复核短视频/直播间的宣传用语合规性。",
            f"时效防御：针对 {top_title} 引起的发货熔断风险，提前开启‘预售模式’或‘延长履约时效’设置，避免被平台扣罚。 ",
        ]

    platform_led_actions = [
        "先复核平台仓配链路的价格带、补货节奏和承诺时效，确认安全垫还在不在。",
        "检查平台托管/FBA 规则有没有同步变化，避免平台抽成、尾程或绩效门槛一起抬头。",
        f"把 {top_type} 风险翻译成平台内动作：提价、控量、调补货，不要只看新闻标题。",
    ]
    if fulfillment == "fba":
        platform_led_actions = [
            "先把 FBA 主力 SKU 的到手价、仓内费用和提价空间过一遍，别等利润塌了才补。",
            "把补货节奏和广告节奏一起复核，优先保住能扛住价格战的核心款。",
            f"把 {top_type} 风险落成平台动作：提价、控量、调补货，别让仓内优势被慢反应浪费掉。",
        ]

    merchant_led_actions = [
        "海外仓专项：针对 Temu 半托管或三方仓，立即盘点站点在途库存与库容利用率，防范由于政策突变引发的仓储费‘背刺’。",
        "履约协同：核对 3PL 承运商的‘旺季附加费’最新调价表，同步在前端进行‘售价阶梯化’对冲。",
        f"应急预案：针对 {top_title} 预留备用清关行联系方式，并评估是否将部分核心 SKU 从跨境仓向本地仓前置拨备。",
    ]
    if fulfillment == "overseas-warehouse":
        merchant_led_actions = [
            "先把海外仓现货、在途和尾程成本拆开看，确认哪一段最先吃掉利润。",
            "把利润薄、周转慢、占仓重的 SKU 先挑出来，本周就准备收口或换承运方案。",
            f"针对 {top_title} 预留替代清关/尾程方案，别等 SLA 掉了才被动救火。",
        ]

    # 针对不同平台的专家级专项建议
    tk_actions = [
        "TikTok 专项：立即复核‘达人建联’准入门槛，针对新政策调整佣金池，防止投流惯性亏损。",
        "合规专项：针对 TikTok Shop EU 的最新认证要求，启动‘备选白牌’链路申报，确保时效安全。",
        "运营动作：调整直播间/短视频关键词，避开合规敏感区，并核算最新‘含税到手价’。"
    ]
    temu_actions = [
        "Temu 专项：立即盘点‘半托管’在途库存，针对海关严查预留 7-10 天时效冗余。",
        "履约专项：核对 3PL 旺季附加费，同步在 Temu 后台更新‘阶梯定价’，对冲物流波动。",
        "风控动作：检查全托管/半托管质量绩效分，避免由于备货延迟引发的平台强制下架。"
    ]
    amz_actions = [
        "Amazon 专项：核查 FBA 库容与冗余库存，针对政策变动优化‘配送费’阶梯，保住利润底线。",
        "合规专项：复核欧盟/美国站点的保险、认证等硬门槛，防止由于文件缺失导致的‘链接变狗’。",
        "备货动作：针对物流链路波动，微调 FBA 补货节奏，并同步更新卖家自发货（FBM）的备选渠道。"
    ]

    path_actions = {
        "crossborder-direct-mail": direct_mail_actions + tk_actions,
        "local-fulfillment-platform-led": platform_led_actions + amz_actions,
        "local-fulfillment-merchant-led": merchant_led_actions + temu_actions,
    }

    # 按路径差异化注意事项，避免所有路径显示相同内容
    path_watchouts = {
        "crossborder-direct-mail": [
            f"密切关注 {top_title} 的最终执行日期和适用品类；如尚未落地，保持周频追踪。",
            "直邮链路的税费和时效最脆弱 — 一旦政策落地，立即重算到手价，避免广告投放打水漂。",
        ],
        "local-fulfillment-platform-led": [
            f"留意平台是否因 {top_title} 调整仓配规则、提高绩效门槛或修改补货频率限制。",
            "平台仓（FBA/全托管）的库容和合规文件是核心风险点 — 提前排查认证到期和库存健康度。",
        ],
        "local-fulfillment-merchant-led": [
            f"自发货/海外仓路径优先关注 {top_title} 对清关和尾程时效的影响，准备备选物流方案。",
            "3PL 旺季附加费和仓储费可能同步上涨 — 提前锁定费率或切换供应商。",
        ],
    }

    return [
        {
            "path_key": item["key"],
            "path_label": item["label"],
            "path_description": item["description"],
            "actions": path_actions[item["key"]],
            "watchouts": path_watchouts.get(item["key"], shared_watch[:2]),
            "modifier": base_modifier,
        }
        for item in FULFILLMENT_PATHS
    ]


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
