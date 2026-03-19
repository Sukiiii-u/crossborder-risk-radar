#!/usr/bin/env python3
from __future__ import annotations

import re
import json
from copy import deepcopy
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
import sys
sys.path.insert(0, str(SCRIPT_DIR))

from runtime_paths import SOURCE_STATUS_FILE  # noqa: E402
from zh_localization import localize_summary, localize_title, looks_chinese  # noqa: E402

GENERIC_TOPIC_TITLES = {
    "policy": "平台规则与售后政策更新",
    "platform": "平台规则与售后政策更新",
    "platform_rule": "平台规则与售后政策更新",
    "tariff": "税费与低货值包裹政策更新",
    "customs": "清关申报与海关政策更新",
    "compliance": "合规要求与商品规则更新",
    "environment": "合规要求与商品规则更新",
    "logistics": "国际物流与履约链路风险更新",
}


def load_source_status() -> dict[str, dict[str, Any]]:
    if not SOURCE_STATUS_FILE.exists():
        return {}
    try:
        payload = json.loads(SOURCE_STATUS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    by_source = payload.get("by_source")
    return by_source if isinstance(by_source, dict) else {}


def chinese_title_for_event(event: dict[str, Any]) -> str:
    # 1. 优先尝试提取预翻译的 zh_title
    explicit = str(event.get("zh_title") or "").strip()
    if looks_chinese(explicit) and len(explicit) > 6 and "业务动态" not in explicit:
        return explicit

    # 2. 深度尝试利用原始标题进行实时穿透
    raw_title = str(event.get("raw_event_title") or event.get("event_title") or "").strip()
    source_label = str(event.get("source_label") or "").strip()
    
    # 获取翻译结果
    localized = localize_title(raw_title, source_label)
    
    # 只要 localized 不是那种明显的 fallback (比如包含 '业务动态' 或太短)，就优先使用
    is_poor_fallback = "业务动态" in localized or "更新" == localized or len(localized) < 5
    if looks_chinese(localized) and not is_poor_fallback:
        return localized

    # 3. 如果翻译还是不好，我们尝试将【来源】与【原始标题/翻译标题】强行拼接，增加信息密度
    # 绝不直接返回“平台规则调整”
    topic = str(event.get("event_type") or event.get("primary_topic") or "policy").strip()
    fallback_base = GENERIC_TOPIC_TITLES.get(topic, "经营动态更新")
    
    final_title = localized if looks_chinese(localized) else raw_title
    
    # 如果最终标题还是太虚，至少带上来源和原始词根的一部分（如果 raw_title 是英文）
    # 4. 最后的清理：移除 URL、多余的 'Content' 标记和过长的标题
    final_title = re.sub(r'https?://\S+', '', final_title).strip()
    final_title = final_title.replace(" Content", "").replace(" content", "").strip()
    final_title = final_title.rstrip("：").rstrip(":").strip()
    
    # 限制长度
    if len(final_title) > 65:
        final_title = final_title[:62] + "..."
        
    # 最终防御：绝不允许空标题
    if not final_title.strip():
        prefix = f"【{source_label}】" if source_label else ""
        return f"{prefix}{fallback_base}"

    return final_title


def chinese_summary_for_event(event: dict[str, Any], title_zh: str) -> str:
    current = str(event.get("event_summary") or "").strip()
    if looks_chinese(current):
        return current

    explicit = str(event.get("zh_summary") or "").strip()
    if looks_chinese(explicit):
        return explicit

    raw_title = str(event.get("raw_event_title") or event.get("event_title") or "").strip()
    raw_content = str(event.get("raw_content") or current or event.get("impact_reasoning") or event.get("seller_angle") or "").strip()
    localized = localize_summary(
        raw_title or title_zh,
        raw_content,
        str(event.get("source_label") or ""),
        str(event.get("source_topic") or event.get("event_type") or ""),
    )
    if looks_chinese(localized):
        return localized
    return "这条经营信号已进入正式发布态，建议结合来源链接与执行范围继续判断。"


def replace_strings(value: Any, replacements: dict[str, str]) -> Any:
    if isinstance(value, str):
        output = value
        for old, new in replacements.items():
            if old and old in output:
                output = output.replace(old, new)
        return output
    if isinstance(value, list):
        return [replace_strings(item, replacements) for item in value]
    if isinstance(value, dict):
        return {key: replace_strings(item, replacements) for key, item in value.items()}
    return value


def should_publish_event(event: dict[str, Any], source_status: dict[str, dict[str, Any]]) -> bool:
    if str(event.get("source_layer") or "") != "official-content":
        return True
    source_id = str(event.get("source_id") or "")
    status = source_status.get(source_id, {})
    return status.get("status") == "verified"


def prepare_brief_for_publish(brief: dict[str, Any]) -> dict[str, Any]:
    prepared = deepcopy(brief)
    source_status = load_source_status()
    events = prepared.get("events")
    if not isinstance(events, list):
        return prepared

    replacements: dict[str, str] = {}
    normalized_events: list[dict[str, Any]] = []
    for event in events:
        if not isinstance(event, dict):
            continue
        if not should_publish_event(event, source_status):
            continue
        current = deepcopy(event)
        old_title = str(current.get("event_title") or "").strip()
        raw_title = str(current.get("raw_event_title") or old_title).strip()
        title_zh = chinese_title_for_event(current)
        summary_zh = chinese_summary_for_event(current, title_zh)
        current["event_title"] = title_zh
        current["event_summary"] = summary_zh
        if raw_title:
            current["raw_event_title"] = raw_title
        if old_title and old_title != title_zh:
            replacements[old_title] = title_zh
        if raw_title and raw_title != title_zh:
            replacements[raw_title] = title_zh
        normalized_events.append(current)

    prepared["events"] = normalized_events
    if replacements:
        prepared = replace_strings(prepared, replacements)
    return prepared
