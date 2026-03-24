#!/usr/bin/env python3
"""统一的 LLM 调用封装层。

默认模型和 API 地址通过配置文件指定，支持 Anthropic Messages 协议。
配置读取优先级：环境变量 > configs/llm_config.json > 默认值。
内置重试（3 次指数退避）和超时（30s）。
LLM 不可用时自动回退到 fallback 结果。
"""
from __future__ import annotations

import json
import logging
import os
import ssl
import time
import urllib.request
from pathlib import Path
from typing import Any

logger = logging.getLogger("llm_client")

DEFAULT_MODEL = "MiniMax-M2.5"
DEFAULT_API_BASE = "https://api.minimaxi.com/anthropic"
DEFAULT_TIMEOUT = 60
MAX_RETRIES = 3
RETRY_BASE_DELAY = 1.0  # 秒，指数退避基数

# 配置文件路径
_CONFIG_FILE = Path(__file__).resolve().parent.parent / "configs" / "llm_config.json"
_file_config: dict[str, str] | None = None


def _load_file_config() -> dict[str, str]:
    """从 configs/llm_config.json 加载配置，并缓存。"""
    global _file_config
    if _file_config is not None:
        return _file_config
    _file_config = {}
    try:
        if _CONFIG_FILE.exists():
            data = json.loads(_CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                _file_config = {k: str(v).strip() for k, v in data.items()
                                if isinstance(v, str) and not k.startswith("_")}
    except Exception:
        pass
    return _file_config


def _get_api_key() -> str | None:
    """读取 API Key：环境变量优先，其次配置文件。"""
    key = os.environ.get("OPENAI_API_KEY", "").strip()
    if key:
        return key
    file_key = _load_file_config().get("api_key", "").strip()
    # 过滤掉占位符文本
    if file_key and "填入" not in file_key and "your" not in file_key.lower():
        return file_key
    return None


def _get_api_base() -> str:
    """读取 API Base：环境变量优先，其次配置文件，最后默认值。"""
    env_base = os.environ.get("OPENAI_API_BASE", "").strip()
    if env_base:
        return env_base
    return _load_file_config().get("api_base", "").strip() or DEFAULT_API_BASE


def _get_model() -> str:
    """读取模型名：环境变量优先，其次配置文件，最后默认值。"""
    env_model = os.environ.get("LLM_MODEL", "").strip()
    if env_model:
        return env_model
    return _load_file_config().get("model", "").strip() or DEFAULT_MODEL


def is_available() -> bool:
    """检查 LLM 是否可用（即 API Key 已配置）。"""
    return _get_api_key() is not None


def chat_completion(
    messages: list[dict[str, str]],
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 800,
    timeout: int = DEFAULT_TIMEOUT,
) -> str | None:
    """调用 LLM Chat API（Anthropic Messages 协议），返回文本结果。

    失败时返回 None（调用方应检查并使用 fallback）。
    """
    if model is None:
        model = _get_model()
    api_key = _get_api_key()
    if not api_key:
        logger.debug("API Key 未配置，跳过 LLM 调用")
        return None

    api_base = _get_api_base().rstrip("/")
    url = f"{api_base}/v1/messages"

    # 分离 system 消息和 user/assistant 消息（Anthropic 格式）
    system_text = ""
    user_messages: list[dict[str, str]] = []
    for msg in messages:
        if msg.get("role") == "system":
            system_text += msg.get("content", "") + "\n"
        else:
            user_messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})

    # 确保至少有一条 user 消息
    if not user_messages:
        return None

    payload_dict: dict[str, Any] = {
        "model": model,
        "messages": user_messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    if system_text.strip():
        payload_dict["system"] = system_text.strip()

    payload = json.dumps(payload_dict).encode("utf-8")

    headers = {
        "Content-Type": "application/json",
        "x-api-key": api_key,
        "anthropic-version": "2023-06-01",
    }

    ctx = ssl.create_default_context()
    last_error: Exception | None = None

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
                body = json.loads(resp.read().decode("utf-8"))
            # Anthropic 格式响应：content 数组可能含 thinking + text 块
            content_blocks = body.get("content", [])
            for block in content_blocks:
                if isinstance(block, dict) and block.get("type") == "text":
                    text = block.get("text", "").strip()
                    if text:
                        return text
            # 如果只有 thinking 块没有 text 块，可能是 max_tokens 不够
            stop_reason = body.get("stop_reason", "")
            if stop_reason == "max_tokens":
                logger.warning("LLM 返回被截断（max_tokens），无 text 输出")
            logger.warning("LLM 返回了空内容（attempt %d/%d）", attempt, MAX_RETRIES)
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_BASE_DELAY * (2 ** (attempt - 1)))
                continue
            return None
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES:
                delay = RETRY_BASE_DELAY * (2 ** (attempt - 1))
                logger.warning(
                    "LLM 调用失败（attempt %d/%d）：%s，%.1fs 后重试",
                    attempt, MAX_RETRIES, exc, delay,
                )
                time.sleep(delay)
            else:
                logger.error("LLM 调用最终失败：%s", exc)

    return None


def call_with_fallback(
    messages: list[dict[str, str]],
    fallback: str,
    model: str | None = None,
    temperature: float = 0.3,
    max_tokens: int = 1500,
) -> tuple[str, bool]:
    """调用 LLM，失败时自动返回 fallback。

    Returns:
        (结果文本, 是否来自 LLM)
    """
    result = chat_completion(messages, model=model, temperature=temperature, max_tokens=max_tokens)
    if result is not None:
        return result, True
    return fallback, False


def translate_to_chinese(
    text: str,
    context: str = "跨境电商",
    max_tokens: int = 1024,
) -> str | None:
    """将英文文本翻译为中文（跨境卖家视角）。"""
    if not text or not text.strip():
        return None
    messages = [
        {
            "role": "system",
            "content": (
                "你是一位跨境电商风险资讯的专业翻译。将以下英文内容翻译为精准、简洁的中文，"
                "面向中国跨境卖家群体。保留关键专业术语（如 FBA、SKU、SLA 等）原文。"
                "不要添加任何解释或评论，仅输出翻译结果。"
            ),
        },
        {"role": "user", "content": text},
    ]
    return chat_completion(messages, max_tokens=max_tokens, temperature=0.1)


def generate_risk_analysis(
    event_content: str,
    event_type: str,
    region: str,
    platform: str = "全平台",
    fulfillment_model: str = "跨境",
    max_tokens: int = 2000,
) -> dict[str, Any] | None:
    """基于事件内容，使用 LLM 生成深度风险研判 + 动态 SOP。

    返回包含 title、impact、actions、sop 的 dict，失败时返回 None。
    """
    messages = [
        {
            "role": "system",
            "content": (
                "你是跨境电商风险分析专家。基于事件内容，输出结构化 JSON 风险研判。\n"
                "要求：\n"
                "1. title：精炼的中文标题（≤40 字），直击卖家痛点\n"
                "2. impact：核心影响分析（2-3 句话），必须具体到利润、库存、合规等维度\n"
                "3. actions：3 条具体行动建议（数组），每条 ≤30 字，以动作动词开头\n"
                "4. sop：针对三条履约路径的差异化应急建议（对象），包含：\n"
                "   - direct_mail：跨境直邮路径（小包直发、邮政渠道）\n"
                "     - actions: 2 条针对该路径的具体行动（数组）\n"
                "     - watchout: 1 条该路径的关键注意事项（字符串）\n"
                "   - platform_led：平台仓配路径（FBA/全托管）\n"
                "     - actions: 2 条针对该路径的具体行动（数组）\n"
                "     - watchout: 1 条该路径的关键注意事项（字符串）\n"
                "   - merchant_led：卖家自发货/海外仓路径（半托管/3PL）\n"
                "     - actions: 2 条针对该路径的具体行动（数组）\n"
                "     - watchout: 1 条该路径的关键注意事项（字符串）\n\n"
                "每条行动 ≤35 字，以动作动词开头，必须与该事件直接相关。\n"
                "注意事项要具体到该路径最脆弱的环节，不要写通用套话。\n\n"
                "输出纯 JSON，不要 Markdown 代码块包裹。"
            ),
        },
        {
            "role": "user",
            "content": (
                f"事件类型：{event_type}\n"
                f"区域：{region}\n"
                f"平台：{platform}\n"
                f"履约模式：{fulfillment_model}\n"
                f"事件内容：{event_content[:2000]}"
            ),
        },
    ]
    raw = chat_completion(messages, max_tokens=max_tokens, temperature=0.3)
    if raw is None:
        return None
    return _parse_json_robust(raw)


def _parse_json_robust(raw: str) -> dict[str, Any] | None:
    """增强 JSON 解析：处理代码块包裹、截断、格式异常等情况。"""
    cleaned = raw.strip()
    # 去除 markdown 代码块
    if cleaned.startswith("```"):
        cleaned = cleaned.split("\n", 1)[-1]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()
    # 直接解析
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    # 尝试提取 JSON 对象（可能前后有多余文本）
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(cleaned[start:end + 1])
        except json.JSONDecodeError:
            pass
    # 截断的 JSON：尝试补全
    if start >= 0 and end <= start:
        truncated = cleaned[start:]
        for suffix in ['"}]', '"}', '"]', '"}]}', '"]}']:
            try:
                return json.loads(truncated + suffix)
            except json.JSONDecodeError:
                continue
    logger.warning("LLM JSON 解析失败，原始内容：%s", raw[:300])
    return None

