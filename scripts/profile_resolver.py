#!/usr/bin/env python3
"""画像解析模块：处理卖家画像的解析、预设匹配和 profile 合并。"""
from typing import Any

from morning_brief_constants import (
    DEFAULT_PROFILE,
    GENERAL_RADAR_PROFILE,
    PRESET_ALIASES,
    PROFILE_LABELS,
    PROFILE_PRESETS,
)
from applicability import fulfillment_path_label, platform_modifier_label


def canonicalize_profile_key(name: str) -> str:
    lowered = name.strip().lower().replace("_", "-")
    if lowered in PROFILE_PRESETS:
        return lowered
    alias_key = name.strip().lower().replace("_", " ")
    return PRESET_ALIASES.get(alias_key) or PRESET_ALIASES.get(lowered) or lowered


def resolve_profile_input(raw_profile: Any) -> tuple[dict, str | None]:
    if raw_profile is None:
        return dict(GENERAL_RADAR_PROFILE), None

    if isinstance(raw_profile, str):
        preset = canonicalize_profile_key(raw_profile)
        if preset in PROFILE_PRESETS:
            return dict(PROFILE_PRESETS[preset]), preset
        raise ValueError(f"unknown seller profile preset: {raw_profile}")

    if not isinstance(raw_profile, dict):
        raise ValueError("seller profile input must be a preset string or object")

    preset_name = None
    preset_hint = raw_profile.get("profile") or raw_profile.get("profile_preset") or raw_profile.get("preset")
    if isinstance(preset_hint, str) and preset_hint.strip():
        preset_name = canonicalize_profile_key(preset_hint)
        if preset_name not in PROFILE_PRESETS:
            raise ValueError(f"unknown seller profile preset: {preset_hint}")

    base = dict(DEFAULT_PROFILE)
    if preset_name:
        base.update(PROFILE_PRESETS[preset_name])

    overrides = {k: v for k, v in raw_profile.items() if k not in {"profile", "profile_preset", "preset"} and v is not None}
    base.update(overrides)
    return base, preset_name


def resolve_profile_inputs(raw_profile: Any) -> list[tuple[dict, str | None]]:
    if isinstance(raw_profile, list):
        if not raw_profile:
            raise ValueError("seller profile list cannot be empty")
        return [resolve_profile_input(item) for item in raw_profile]
    return [resolve_profile_input(raw_profile)]


def merge_profile(seed: dict, profile: dict) -> dict:
    merged = dict(seed)
    merged_profile = dict(DEFAULT_PROFILE)
    merged_profile.update(seed.get("seller_profile") or {})
    merged_profile.update(profile)
    merged["seller_profile"] = merged_profile
    return merged


def is_general_radar_profile(profile: dict, preset_name: str | None = None) -> bool:
    return preset_name is None and profile.get("platform") == "general" and profile.get("fulfillment_model") == "mixed"


def profile_display_name(profile: dict, preset_name: str | None = None) -> str:
    if is_general_radar_profile(profile, preset_name):
        return "通用雷达首页（事件驱动 / 不绑定默认画像）"
    if preset_name and preset_name in PROFILE_LABELS:
        return PROFILE_LABELS[preset_name]

    market = profile.get("market", "unknown")
    return f"{fulfillment_path_label(profile)}（平台修正：{platform_modifier_label(profile)} / 市场：{market}）"


def profile_focus(profile: dict) -> str:
    platform = profile.get("platform")
    fulfillment = profile.get("fulfillment_model")
    price_band = profile.get("price_band")

    if platform == "general" and fulfillment == "mixed":
        return "默认首页不再替任何单一画像站台；先按事件看，再看谁高相关、谁先动。"
    if platform == "tiktok-shop" and fulfillment == "direct-mail":
        return "你这类盘子对税费、签收体验和转化率特别敏感，今天别只盯流量，先盯毛利。"
    if platform == "independent-site" and fulfillment == "direct-mail":
        return "你更该关注到手价、运费模板和退件链路，别让广告把亏损放大。"
    if fulfillment in {"fba", "overseas-warehouse"}:
        return "仓内履约能帮你挡一部分冲击，但定价和补货节奏还是要立刻复核。"
    if price_band == "low":
        return "低客单模式最怕税费和尾程成本一起抬头，利润会先被打穿。"
    return "今天优先看税务、履约和合规变化，别被泛新闻带偏。"
