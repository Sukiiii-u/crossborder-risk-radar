#!/usr/bin/env python3
"""晨报文本渲染模块：将结构化 brief 数据渲染为可读文本。"""
from brief_builder import event_impact_line, urgency_from_result


def format_event(result: dict, index: int, heading_level: str = "###") -> str:
    actions = result.get("suggested_actions", [])
    top_actions = actions[:2] if actions else ["继续观察更多细则", "补更多信息再决定"]
    source_names = " / ".join(source.get("name", "") for source in result.get("sources", [])[:2] if source.get("name"))
    source_line = source_names or result.get("source_label") or result.get("seed_label") or "未知来源"
    applicability = result.get("applicability_layers", {})
    current_view = applicability.get("current_view", {})
    layer_actions = result.get("layer_actions", {})
    lines = [
        f"{heading_level} 事件 {index}｜{result.get('event_title', '未命名事件')}",
        f"- 雷达判断：{urgency_from_result(result)}｜{result.get('region', 'Other')}｜{result.get('event_type', 'policy')}｜score {result.get('ranking_score', 0)}",
        f"- 为什么排这里：{result.get('seller_angle', '')}",
        f"- 当前视角适用性：{current_view.get('path', 'unknown')} / {current_view.get('label', '未分层')}",
        f"- 发生了什么：{result.get('event_summary', '')}",
        f"- 为什么值得所有卖家知道：{event_impact_line(result)}",
        "- 适用性分层：",
        f"  - 高相关是谁：{'；'.join(applicability.get('high_relevance', [])) or '无'}",
        f"  - 中相关是谁：{'；'.join(applicability.get('medium_relevance', [])) or '无'}",
        f"  - 低相关/观察是谁：{'；'.join(applicability.get('low_relevance_or_watch', [])) or '无'}",
        "- 各层该做什么：",
        f"  - 高相关：{'；'.join(layer_actions.get('high', [])) or '无'}",
        f"  - 中相关：{'；'.join(layer_actions.get('medium', [])) or '无'}",
        f"  - 低相关/观察：{'；'.join(layer_actions.get('low', [])) or '无'}",
        f"- 当前首页先做：{top_actions[0]}",
        f"- 接着盯：{top_actions[1] if len(top_actions) > 1 else top_actions[0]}",
        f"- 来源：{source_line}",
    ]
    return "\n".join(lines)


def render_single_human_brief(brief: dict, title_heading: str = "#", section_heading: str = "##", include_title: bool = True) -> str:
    path_heading = section_heading + "#"
    overview = brief.get("overview", {})
    general_mode = brief.get("radar_mode") == "general_event_view"
    lines = []

    if include_title:
        lines.extend([f"{title_heading} 今日跨境风险晨报", ""])

    if general_mode:
        dashboard = brief.get("dashboard", {})
        top_story = dashboard.get("top_story", {})
        lines.extend([
            "首页模式：Dashboard 首页",
            f"平台范围：{overview.get('active_profile_modifier', {}).get('platform', 'unknown')}",
            f"展示标签：{brief.get('profile_label', '未命名画像')}",
            f"一句话结论：{brief.get('overall_takeaway', '')}",
            f"首页提醒：{brief.get('profile_focus', '')}",
            "",
            f"{section_heading} Dashboard 总览",
            f"- 高优先级风险数：{dashboard.get('high_priority_count', 0)}",
            f"- 最该先看的 1 条：{top_story.get('title', '今天暂无置顶事件')}（{top_story.get('risk_type', 'none')} / {top_story.get('priority', 'none')}）",
            f"- 风险类型分布：{'、'.join(dashboard.get('risk_type_distribution', [])) or '暂无'}",
            f"- 首页视角：{overview.get('active_profile_modifier', {}).get('seller_profile', 'unknown')} / {overview.get('active_profile_modifier', {}).get('platform', 'unknown')}",
            "",
            f"{section_heading} 事件卡片",
        ])
        for card in dashboard.get("cards", []):
            lines.extend([
                f"{path_heading} 卡片 {card.get('rank', 0)}｜{card.get('title', '未命名事件')}",
                f"- 风险类型：{card.get('risk_type', 'policy')}",
                f"- 优先级：{card.get('priority', 'medium')}",
                f"- 高相关是谁：{card.get('who_to_watch', '待补充')}",
                f"- 一句话动作：{card.get('action', '继续观察更多细则')}",
                "",
            ])

        lines.extend([
            f"{section_heading} 打开深挖",
            f"- 今日最值得看：{overview.get('headline', '')}",
            f"- 为什么先看：{overview.get('why_it_matters', '')}",
            f"- 头号信号：{brief.get('key_signal', '')}",
            "",
        ])
    else:
        lines.extend([
            f"履约主视角：{overview.get('active_profile_modifier', {}).get('seller_profile', 'unknown')}",
            f"平台修正：{overview.get('active_profile_modifier', {}).get('platform', 'unknown')}",
            f"展示标签：{brief.get('profile_label', '未命名画像')}",
            f"一句话结论：{brief.get('overall_takeaway', '')}",
            f"画像提醒：{brief.get('profile_focus', '')}",
            f"头号信号：{brief.get('key_signal', '')}",
            "",
            f"{section_heading} 总览判断",
            f"- 今日最值得看：{overview.get('headline', '')}",
            f"- 为什么先看：{overview.get('why_it_matters', '')}",
            f"- 当前修正项：平台={overview.get('active_profile_modifier', {}).get('platform', 'unknown')} / 履约路径={overview.get('active_profile_modifier', {}).get('seller_profile', 'unknown')}",
            "",
            f"{section_heading} 分履约动作",
        ])

        for item in brief.get("fulfillment_actions", []):
            lines.append(f"{path_heading} 履约路径｜{item.get('path_label', '未命名路径')}")
            lines.append(f"- 路径说明：{item.get('path_description', '')}")
            for action in item.get("actions", []):
                lines.append(f"- 动作：{action}")
            if item.get("watchouts"):
                lines.append(f"- 继续盯：{'；'.join(item.get('watchouts', []))}")
            lines.append(f"- 路径修正项：{item.get('modifier', '')}")
            lines.append("")

        lines.append(f"{section_heading} 重点事件")

    event_heading = section_heading + "#"
    if not general_mode:
        for index, result in enumerate(brief.get("events", []), start=1):
            lines.append(format_event(result, index, heading_level=event_heading))
            lines.append("")

    priority_lens = brief.get("priority_lens", [])
    if priority_lens:
        lines.append(f"{section_heading} 优先级解释")
        lines.extend([f"- {item}" for item in priority_lens])
        lines.append("")

    today_actions = brief.get("today_actions", [])
    if today_actions:
        lines.append(f"{section_heading} 今日先做")
        lines.extend([f"- {action}" for action in today_actions])
        lines.append("")

    watch_items = brief.get("watch_items", [])
    if watch_items:
        lines.append(f"{section_heading} 继续观察")
        lines.extend([f"- {action}" for action in watch_items])
        lines.append("")

    if general_mode:
        lines.extend([
            f"{section_heading} 按画像深挖",
            "- 如果某条事件跟你的盘子高度相关，再显式切到 amazon-fba / tiktok-direct-mail / independent-site-direct-mail / overseas-warehouse 看专属动作。",
            "",
        ])

    lines.extend([
        f"{section_heading} 暂缓动作",
        f"- {brief.get('hold_line', '')}",
        "",
        f"{section_heading} 一句话结论",
        brief.get("overall_takeaway", ""),
    ])
    return "\n".join(lines).strip()


def render_human_brief(brief: dict) -> str:
    if brief.get("brief_type") != "morning_radar_multi_view":
        return render_single_human_brief(brief)

    lines = [
        "# 今日跨境风险晨报",
        "",
        "## 多画像视角总览",
        f"- 组合视角：{brief.get('profile_label', '')}",
        f"- 一句话结论：{brief.get('overall_takeaway', '')}",
    ]

    for index, view in enumerate(brief.get("views", []), start=1):
        lines.extend([
            "",
            f"## 画像视角 {index}｜{view.get('profile_label', '未命名画像')}",
            render_single_human_brief(view, title_heading="###", section_heading="###", include_title=False),
        ])

    return "\n".join(lines).strip()
