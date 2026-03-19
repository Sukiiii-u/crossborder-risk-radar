#!/usr/bin/env python3
"""摘要与概览生成模块：构建晨报概览、摘要和 Dashboard 数据。"""
import email.utils
from datetime import datetime, timezone
from typing import Any

from applicability import (
    normalize_fulfillment_path,
    platform_modifier_label,
)


def parse_datetime(value: Any) -> datetime | None:
    """解析各种格式的日期时间字符串。"""
    if not value:
        return None
    if isinstance(value, datetime):
        parsed = value
    else:
        text = str(value).strip()
        if not text:
            return None
        try:
            parsed = email.utils.parsedate_to_datetime(text)
        except (TypeError, ValueError, IndexError):
            parsed = None
        if parsed is None:
            try:
                parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
            except ValueError:
                return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def urgency_from_result(result: dict) -> str:
    if result.get("risk_level") == "high" and result.get("confidence") != "low":
        return "今天先看"
    if result.get("risk_level") == "medium":
        return "本周重点关注"
    return "先监控"


def event_impact_line(result: dict) -> str:
    event_type = result.get("event_type", "policy")
    risk_level = result.get("risk_level", "medium")
    dimensions = result.get("impact_dimensions", [])
    dimension_text = "、".join(dimensions[:3]) if dimensions else "经营动作"
    if event_type == "tariff":
        return f"这条更像利润表预警，重点冲击 {dimension_text}。"
    if event_type == "environment":
        return f"这条偏合规与包装成本，先看 {dimension_text}。"
    if event_type == "logistics":
        return f"这条偏履约稳定性，别让 {dimension_text} 失控。"
    return f"这条属于 {risk_level} 风险，核心看 {dimension_text}。"


def _logistics_angle_by_content(result: dict) -> str:
    """根据物流事件的具体内容关键词生成差异化的卖家视角文案。"""
    title = str(result.get("event_title") or result.get("raw_event_title") or "").lower()
    summary = str(result.get("event_summary") or "").lower()
    text = f"{title} {summary}"

    if any(kw in text for kw in ["附加费", "surcharge", "运价", "shipping rate", "freight rate", "运费"]):
        return "头程运费或附加费正在上涨，直接挤压毛利空间，需要重新核算物流成本和定价策略。"
    if any(kw in text for kw in ["关闭", "shut", "close", "consolidat", "整合", "网络调整"]):
        return "配送网络正在调整，部分区域的时效和可达性可能受影响，需要提前评估备选物流方案。"
    if any(kw in text for kw in ["退货", "return", "退款", "refund", "退件"]):
        return "退货退款链路变化会推高逆向物流成本，需要重新评估退货政策和利润缓冲。"
    if any(kw in text for kw in ["暂停", "suspend", "中断", "alert", "告警", "disruption"]):
        return "物流线路出现服务中断或告警，在途订单和新发货计划都需要立即排查。"
    if any(kw in text for kw in ["法案", "act", "法规", "regulation", "政策", "policy"]):
        return "物流相关政策法规变动可能改变运输成本结构或通关流程，需关注后续执行细则。"
    if any(kw in text for kw in ["集成", "integrat", "对接", "marketplace"]):
        return "新的物流或平台集成渠道出现，可能带来新的履约选择和竞争格局变化。"
    if any(kw in text for kw in ["海湾", "gulf", "红海", "red sea", "战争", "war", "冲突"]):
        return "地缘冲突正在扰动国际航运链路，附加费和时效都面临不确定性，需评估备选航线。"
    return "这条物流动态可能影响履约时效或成本结构，建议结合自身链路评估实际冲击。"


def event_seller_angle(result: dict, profile: dict) -> str:
    platform = profile.get("platform")
    fulfillment = profile.get("fulfillment_model")
    event_type = result.get("event_type")

    # 优先使用 LLM 生成的 impact_reasoning（如果有且有效）
    impact_reasoning = result.get("impact_reasoning")
    if impact_reasoning and "未解析出" not in impact_reasoning and len(impact_reasoning) > 15:
        return impact_reasoning

    if event_type == "tariff" and fulfillment == "direct-mail":
        return "对你这种直邮盘，税后到手价和毛利会最先被打。"
    if event_type == "tariff" and fulfillment in {"fba", "overseas-warehouse"}:
        return "你有仓配缓冲，但价格带和补货节奏还是会被挤压。"
    if event_type == "tariff":
        return "税费变化可能改变到手价和利润结构，需要重新核算受影响 SKU 的毛利。"
    if event_type == "logistics" and fulfillment in {"fba", "overseas-warehouse"}:
        return "仓内能扛一阵，但补货窗口和安全库存要提前改。"
    if event_type == "logistics":
        return _logistics_angle_by_content(result)
    if event_type == "environment" and platform == "independent-site":
        return "独立站更容易把包装/材料成本直接吃进毛利。"
    if event_type == "environment":
        return "合规或包装要求变化可能增加单件成本，需要评估受影响品类和适用范围。"
    if event_type == "policy":
        return "平台规则调整可能影响经营方式或成本结构，建议核查具体执行范围和时间节点。"

    return "这条更新对当前经营模型可能有直接的链路阻断或成本挤压作用，建议核实细则。"


def build_overall_takeaway(profile: dict, results: list[dict], source_mode: str = "seed") -> str:
    if source_mode == "real":
        if results:
            top = results[0]
            if profile.get("platform") == "general" and profile.get("fulfillment_model") == "mixed":
                return (
                    "默认首页今天优先吃最新抓取快照；"
                    f"先看 {top.get('event_type', 'policy')} 事件本身怎么改全局经营，再按高/中/低相关分层动作。"
                )
            return (
                "今天这版晨报优先吃最新抓取快照；"
                f"最该先看的不是新闻量，而是 {top.get('event_type', 'policy')} 对 {profile.get('fulfillment_model', '当前履约')} 模型的直接冲击。"
            )
        return "今天这版晨报先吃最新抓取快照；只有真实事件空了，才回退到 seed demo。"

    high_risk_count = sum(1 for item in results if item.get("risk_level") == "high")
    fulfillment = profile.get("fulfillment_model")
    platform = profile.get("platform")

    if platform == "general" and fulfillment == "mixed":
        if results:
            top = results[0]
            return f"默认首页现在先按事件排优先级：先看 {top.get('event_type', 'policy')}，再看谁高相关、谁只需观察，不再默认站在 Amazon FBA 视角讲话。"
        return "默认首页现在先按事件排优先级，不再默认落到某个卖家画像。"
    if platform == "tiktok-shop" and fulfillment == "direct-mail":
        return "今天别先聊增长神话，先把 EU 直邮利润、税后售价和履约稳定性算明白。"
    if platform == "independent-site" and fulfillment == "direct-mail":
        return "今天最该防的是独立站直邮模型被税费和退件联手偷利润，先稳住到手价和交付体验。"
    if fulfillment == "fba":
        return "今天重点不是恐慌，而是确认 FBA 定价、补货和尾程成本还有没有安全垫。"
    if fulfillment == "overseas-warehouse":
        return "今天先把海外仓的对冲优势吃满：看仓配、定价和清关链路能不能继续撑住利润。"
    if high_risk_count >= 2:
        return "今天至少有两条高风险信号，优先处理会直接伤利润和履约的变化。"
    return "今天优先看税务、履约、合规三类变化，尤其先检查 EU 相关 SKU 的利润与履约风险。"


def collect_today_actions(results: list[dict]) -> list[str]:
    actions: list[str] = []
    for item in results:
        for action in item.get("suggested_actions", [])[:1]:
            if action not in actions:
                actions.append(action)
    return actions[:3]


def collect_watch_items(results: list[dict]) -> list[str]:
    watch_items: list[str] = []
    for item in results:
        actions = item.get("suggested_actions", [])
        if len(actions) > 1 and actions[1] not in watch_items:
            watch_items.append(actions[1])
    return watch_items[:3]


def collect_hold_line(profile: dict) -> str:
    platform = profile.get("platform")
    fulfillment = profile.get("fulfillment_model")

    if platform == "general" and fulfillment == "mixed":
        return "先别一上来就把首页绑定成某个默认画像；先看事件级别，再决定切去哪个画像深挖。"
    if platform == "independent-site" and fulfillment == "direct-mail":
        return "先别急着在独立站前台乱改全站价格和运费，先把 EU 直邮利润算透。"
    if platform == "tiktok-shop" and fulfillment == "direct-mail":
        return "先别急着继续冲量或硬扛低价，细则没落地前别让投流把亏损放大。"
    if fulfillment == "fba":
        return "先别急着大规模调仓或一口气提价，先确认 FBA 安全垫到底还剩多少。"
    if fulfillment == "overseas-warehouse":
        return "先别急着把备货计划全推翻，先确认海外仓和尾程链路哪一段最脆。"
    if fulfillment == "direct-mail":
        return "先别急着猛加预算或硬扛低价，细则没落地前，别把亏损放大。"
    return "先别急着大规模调仓，先确认新规影响范围和执行节奏。"


def build_key_signal(results: list[dict]) -> str:
    if not results:
        return "今天没有筛出值得晨报置顶的信号。"
    top = results[0]
    return f"{top.get('event_title', '未命名事件')}｜{top.get('seller_angle', '')}"


def build_overview(profile: dict, ranked_events: list[dict], source_mode: str) -> dict:
    general_mode = profile.get("platform") == "general" and profile.get("fulfillment_model") == "mixed"
    if not ranked_events:
        return {
            "headline": "今天没有筛出值得置顶的风险信号。",
            "why_it_matters": "先继续看真实抓取是否有新增，再决定要不要发动作提醒。",
            "top_risk": None,
            "source_mode": source_mode,
            "active_profile_modifier": {
                "platform": platform_modifier_label(profile),
                "seller_profile": "通用雷达首页" if general_mode else normalize_fulfillment_path(profile),
            },
        }

    top = ranked_events[0]
    top_topic = top.get("event_type", "policy")
    top_title = top.get("event_title", "未命名事件")
    profile_path = normalize_fulfillment_path(profile)
    if general_mode:
        why_it_matters = (
            f"这条 {top_topic} 事件已经不是某个单一画像的小波动，而是所有卖家都该先扫一眼的首页信号；"
            "先看事件本身，再按高相关 / 中相关 / 低相关分层动作。"
        )
        return {
            "headline": f"通用雷达先盯 {top_topic}：{top_title}",
            "why_it_matters": why_it_matters,
            "top_risk": {
                "event_title": top_title,
                "event_type": top_topic,
                "risk_level": top.get("risk_level"),
                "seller_angle": top.get("seller_angle"),
            },
            "source_mode": source_mode,
            "active_profile_modifier": {
                "platform": platform_modifier_label(profile),
                "seller_profile": "通用雷达首页",
            },
        }

    why_it_matters = (
        f"今天最值得看的不是新闻数量，而是 {top_topic} 风险已经开始直接碰 {profile_path} 的利润和履约动作；"
        f"当前画像里的 platform={profile.get('platform', 'unknown')} 只是修正项，不该再抢第一层。"
    )
    return {
        "headline": f"今天先盯 {top_topic}：{top_title}",
        "why_it_matters": why_it_matters,
        "top_risk": {
            "event_title": top_title,
            "event_type": top_topic,
            "risk_level": top.get("risk_level"),
            "seller_angle": top.get("seller_angle"),
        },
        "source_mode": source_mode,
        "active_profile_modifier": {
            "platform": platform_modifier_label(profile),
            "seller_profile": profile_path,
        },
    }


def build_priority_lens(results: list[dict]) -> list[str]:
    lenses = []
    for item in results:
        topic = item.get("primary_topic", item.get("event_type", "policy"))
        risk = item.get("risk_level", "medium")
        current_view = item.get("applicability_layers", {}).get("current_view", {})
        tier = current_view.get("label")
        if tier:
            line = f"{topic} / {risk} / 当前视角={tier}：{item.get('seller_angle', '')}"
        else:
            line = f"{topic} / {risk}：{item.get('seller_angle', '')}"
        if line not in lenses:
            lenses.append(line)
    return lenses[:3]


def build_risk_type_distribution(results: list[dict]) -> list[str]:
    counts: dict[str, int] = {}
    for item in results:
        topic = str(item.get("primary_topic") or item.get("event_type") or "policy")
        counts[topic] = counts.get(topic, 0) + 1
    ordered = sorted(counts.items(), key=lambda pair: (-pair[1], pair[0]))
    return [f"{topic}×{count}" for topic, count in ordered]


def build_dashboard_summary(brief: dict) -> dict:
    events = brief.get("events", [])
    high_priority_count = sum(1 for item in events if item.get("risk_level") == "high")
    top_event = events[0] if events else None
    distribution = build_risk_type_distribution(events)

    cards = []
    for index, item in enumerate(events, start=1):
        high_relevance = item.get("applicability_layers", {}).get("high_relevance", [])
        cards.append({
            "rank": index,
            "title": item.get("event_title", "未命名事件"),
            "risk_type": item.get("event_type", "policy"),
            "priority": item.get("risk_level", "medium"),
            "who_to_watch": high_relevance[0] if high_relevance else item.get("seller_angle", "待补充"),
            "action": (item.get("suggested_actions") or ["继续观察更多细则"])[0],
        })

    return {
        "high_priority_count": high_priority_count,
        "top_story": {
            "title": top_event.get("event_title", "今天暂无置顶事件") if top_event else "今天暂无置顶事件",
            "risk_type": top_event.get("event_type", "none") if top_event else "none",
            "priority": top_event.get("risk_level", "none") if top_event else "none",
        },
        "risk_type_distribution": distribution,
        "cards": cards,
    }
