#!/usr/bin/env python3
import json
import logging
import re
import sys
from pathlib import Path
from typing import Any

_SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(_SCRIPT_DIR))

import llm_client  # noqa: E402

logger = logging.getLogger("analyze_event")
SCRIPT_DIR = _SCRIPT_DIR

EVENT_TYPE_KEYWORDS = {
    "tariff": [
        "tariff", "tariffs", "关税", "进口税", "trade policy", "trade war", "加税", "额外费用",
        "征收费用", "小包税", "免税", "低价值包裹", "税费", "cbam", "carbon border",
        "duties", "duty", "nearshoring", "reshoring", "近岸", "回流", "贸易战",
        "supply chain cost", "供应链成本", "anti-dumping", "反倾销",
    ],
    "environment": ["环保", "packaging", "包装", "plastic", "sustainability", "可回收"],
    "compliance": [
        "compliance", "合规", "regulation", "认证", "监管", "标签要求",
        "counterfeit", "假冒", "fake", "伪冒", "知识产权", "trademark", "品牌侵权",
        "seized", "扣押", "走私", "违禁品", "recall", "召回", "禁售",
    ],
    "logistics": [
        "logistics", "shipping", "port", "物流", "航运", "延误", "港口", "罢工",
        "locomotive", "列车", "铁路",
        # 补充缺失的高频物流词
        "freight", "cargo", "container", "warehouse", "warehousing", "trucking",
        "trailer", "supply chain", "carrier", "ocean", "vessel", "transit",
        "delivery", "fulfillment", "surcharge", "rate",
        "货运", "仓储", "运输", "集装箱", "承运", "舱位", "运价", "附加费", "清关",
        "头程", "尾程", "时效", "航线", "海运", "空运", "陆运",
    ],
    "holiday": ["holiday", "节假日", "旺季", "peak season", "促销季"],
    "policy": [
        "立法", "法案", "法规", "禁令", "ban", "制裁", "sanction",
        "行政令", "executive order", "carnet", "manifest",
        "legislation", "act", "directive",
    ],
    "platform": [
        "launch", "推出", "上线", "新功能", "feature", "update", "升级",
        "alexa", "algorithm", "算法", "佣金", "commission", "fee change",
        "marketplace", "seller central", "卖家中心", "公告", "规则", "措施",
        "限流", "降权", "流量",
    ],
}

IMPACT_MAP = {
    "tariff": ["cost", "pricing", "inventory", "supply_chain"],
    "environment": ["compliance", "cost", "supply_chain"],
    "compliance": ["compliance", "inventory", "pricing"],
    "logistics": ["supply_chain", "inventory"],
    "holiday": ["demand", "inventory"],
    "policy": ["cost", "compliance"],
    "platform": ["demand", "pricing", "compliance"],
}

ACTIONS_MAP = {
    "tariff": [
        "重新测算重点 SKU 毛利率",
        "评估是否需要提价或压缩广告投入",
        "暂缓高风险 SKU 的激进补货",
    ],
    "environment": [
        "盘点当前包装或材料方案",
        "评估替代材料与合规成本",
        "确认正式执行时间与适用品类",
    ],
    "compliance": [
        "核查认证、标签与说明书要求",
        "复核目标市场的合规文件是否齐全",
        "暂缓高风险商品扩量",
    ],
    "logistics": [
        "增加履约和补货缓冲时间",
        "复核当前物流方案的时效风险",
        "优先保障重点 SKU 库存安全",
    ],
    "holiday": [
        "复盘旺季备货节奏",
        "调整广告与促销排期",
        "优先保障高转化 SKU 的库存",
    ],
    "policy": [
        "补充更多政策细节后再判断",
        "先确认影响对象、执行时间和适用品类",
        "只对高敏感 SKU 做预排查",
    ],
    "platform": [
        "关注平台功能变更对流量和转化的影响",
        "评估是否需要适配新功能或调整运营策略",
        "监控竞品是否已利用新功能抢占优势",
    ],
}

EVENT_TYPES = {"tariff", "environment", "compliance", "logistics", "holiday", "policy", "platform"}
REGIONS = {"US", "EU", "UK", "Other"}
RISK_LEVELS = {"low", "medium", "high"}
CONFIDENCE_LEVELS = {"low", "medium", "high"}
IMPACT_DIMENSIONS = {"cost", "pricing", "inventory", "compliance", "supply_chain", "demand"}


def signal_in_text(signal: str, text: str) -> bool:
    normalized = signal.strip()
    if not normalized:
        return False
    if any("\u4e00" <= ch <= "\u9fff" for ch in normalized):
        return normalized in text
    pattern = rf"(?<![a-z0-9-]){re.escape(normalized.lower())}(?![a-z0-9-])"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def validate_input(input_data: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(input_data, dict):
        raise ValueError("input must be a JSON object")

    content = input_data.get("content")
    if not isinstance(content, str) or not content.strip():
        raise ValueError("content is required and must be a non-empty string")

    url = input_data.get("url")
    if url is not None and not isinstance(url, str):
        raise ValueError("url must be a string when provided")

    region_hint = input_data.get("region_hint")
    if region_hint is not None:
        if not isinstance(region_hint, str):
            raise ValueError("region_hint must be a string when provided")
        region_hint = region_hint.strip() or None
        if region_hint and region_hint not in REGIONS:
            raise ValueError(f"region_hint must be one of {sorted(REGIONS)}")

    seller_profile = input_data.get("seller_profile") or {}
    if not isinstance(seller_profile, dict):
        raise ValueError("seller_profile must be an object when provided")

    return {
        "content": clean_content(content),
        "url": url.strip() if isinstance(url, str) and url.strip() else None,
        "region_hint": region_hint,
        "seller_profile": seller_profile,
    }


def clean_content(content: str) -> str:
    return re.sub(r"\s+", " ", content).strip()


def detect_event_type(text: str) -> str:
    lower = text.lower()
    scores: dict[str, int] = {}
    for event_type, words in EVENT_TYPE_KEYWORDS.items():
        scores[event_type] = sum(1 for word in words if signal_in_text(word, lower))
    best = max(scores, key=lambda k: scores[k])
    # 无关键词命中时兜底为 policy（通用经营信号），而非 platform
    return best if scores[best] > 0 else "policy"


def detect_region(text: str, region_hint: str | None = None) -> str:
    if region_hint:
        return region_hint
    lower = text.lower()
    if "美国" in lower or "united states" in lower or re.search(r"\b(u\.?s\.?a?|america)\b", lower):
        return "US"
    if "欧盟" in lower or "european union" in lower or "european commission" in lower or re.search(r"\beu\b", lower) or "europe" in lower or any(k in lower for k in ["德国", "法国", "意大利", "西班牙"]):
        return "EU"
    if "英国" in lower or "united kingdom" in lower or re.search(r"\buk\b", lower):
        return "UK"
    return "Other"


def _load_signal_config() -> dict[str, list[str]]:
    """从 JSON 配置文件加载信号规则，失败时返回空 dict（回退到硬编码）。"""
    config_path = SCRIPT_DIR.parent / "configs" / "relevance_signals.json"
    try:
        if config_path.exists():
            data = json.loads(config_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                return {k: v for k, v in data.items() if isinstance(v, list) and not k.startswith("_")}
    except Exception:
        pass
    return {}


# 缓存配置加载结果
_signal_config: dict[str, list[str]] | None = None


def _get_signals(key: str, fallback: list[str]) -> list[str]:
    """获取信号列表：优先从 JSON 配置读取，回退到硬编码。"""
    global _signal_config
    if _signal_config is None:
        _signal_config = _load_signal_config()
    return _signal_config.get(key, fallback)


def classify_relevance(text: str) -> tuple[bool, str, str]:
    lower = text.lower()
    direct_operational_signals = _get_signals("direct_operational_signals", [
        "关税", "tariff", "税费", "duty", "税收", "征税", "加税", "免税",
        "成本", "cost", "定价", "pricing", "费用", "fee", "fees", "surcharge",
        "库存", "inventory", "物流", "shipping", "延误", "delay", "履约", "fulfillment", "补货", "replenishment",
        "中断", "outage", "暂停", "suspend", "suspension", "service alert",
        "合规", "regulation", "认证", "标签要求", "进口", "import", "清关", "clearance", "报关",
        "低价值包裹", "parcel fee", "de minimis", "包装法", "包装合规", "包装要求",
        "product standards", "epr", "cbam", "征收额外费用",
        "退款", "refund", "refunds", "退货", "return", "returns", "退件", "索赔", "claim", "claims",
        "赔付", "reimbursement", "safe-t", "seller assurance", "return label", "prepaid return",
        "seller-fulfilled", "fbm", "buy shipping", "restocking fee",
        "封号", "deactivate", "关店", "冻结", "资金冻结", "frozen", "下架", "remove", "take down", "诉讼", "lawsuit", "被起诉", "罚款", "penalty", "fined"
    ])
    environmental_signals = _get_signals("environmental_signals", [
        "包装", "packaging", "可回收", "plastic", "sustainability", "环保",
    ])
    contextual_signals = _get_signals("contextual_signals", [
        "cbp", "customs", "海关", "卖家", "merchant", "seller", "marketplace seller",
    ])
    policy_context_signals = _get_signals("policy_context_signals", ["政策", "policy", "公告", "规则", "措施", "notice", "guidance"])
    regulatory_environment_context_signals = _get_signals("regulatory_environment_context_signals", [
        "compliance", "timeline", "timelines", "requirement", "requirements", "mandatory", "directive",
        "law", "regulation", "official", "官方", "commission", "platform rule", "规则",
        "标签要求", "要求", "更严格", "发布", "包装法", "包装合规", "product standards", "epr", "cbam",
    ])
    weak_or_uncertain_signals = _get_signals("weak_or_uncertain_signals", ["讨论", "可能", "传闻", "rumor", "拟", "投票"])
    pr_or_non_risk_signals = _get_signals("pr_or_non_risk_signals", [
        "品牌形象", "消费者好感度", "营销", "推荐算法", "内容权重",
        "品牌宣布", "品牌升级", "算法更新", "首页推荐",
    ])
    corporate_operational_noise_signals = _get_signals("corporate_operational_noise_signals", [
        "reusable packaging",
        "reusable shipping boxes",
        "closed-loop shipping",
        "closed loop shipping",
        "distribution operations",
        "between facilities",
        "handling efficiency",
        "returnity",
        "b2b shipments",
        "introduced a design",
    ])
    trade_system_maintenance_signals = _get_signals("trade_system_maintenance_signals", [
        "ace",
        "automated commercial environment",
        "carnet",
        "manifest",
        "container seal",
        "data elements",
        "transmission",
        "portal trade users",
    ])

    direct_matched = [signal for signal in direct_operational_signals if signal_in_text(signal, lower)]
    contextual_matched = [signal for signal in contextual_signals if signal_in_text(signal, lower)]
    policy_matched = [signal for signal in policy_context_signals if signal_in_text(signal, lower)]
    environmental_matched = [signal for signal in environmental_signals if signal_in_text(signal, lower)]
    regulatory_environment_matched = [signal for signal in regulatory_environment_context_signals if signal_in_text(signal, lower)]
    uncertain = [signal for signal in weak_or_uncertain_signals if signal_in_text(signal, lower)]
    pr_signals = [signal for signal in pr_or_non_risk_signals if signal_in_text(signal, lower)]
    corporate_noise_matched = [signal for signal in corporate_operational_noise_signals if signal_in_text(signal, lower)]
    trade_system_matched = [signal for signal in trade_system_maintenance_signals if signal_in_text(signal, lower)]

    if trade_system_matched and not direct_matched:
        return False, "Detected customs/trade-system maintenance wording without clear seller-operational action.", "low"

    if corporate_noise_matched and not (policy_matched or regulatory_environment_matched):
        return False, "Detected enterprise packaging/operations coverage without a regulatory or seller-action trigger.", "low"

    if environmental_matched and not direct_matched and not (policy_matched or regulatory_environment_matched):
        return False, "Detected packaging/environment wording without a concrete compliance, rule, or seller-action trigger.", "low"

    if pr_signals and not direct_matched and not policy_matched:
        return False, "Detected brand/marketing-style signals without clear seller-operational impact.", "low"

    if direct_matched:
        reason_parts = [", ".join(direct_matched[:5])]
        if contextual_matched:
            reason_parts.append(", ".join(contextual_matched[:2]))
        if environmental_matched and regulatory_environment_matched:
            reason_parts.append(", ".join((environmental_matched[:2] + regulatory_environment_matched[:2])[:3]))
        reason = f"Detected seller-operational signals: {'; '.join(reason_parts)}"
        confidence = "medium"
        if uncertain:
            reason += f"; uncertainty signals: {', '.join(uncertain[:2])}"
            confidence = "low"
        return True, reason, confidence

    if environmental_matched and (policy_matched or regulatory_environment_matched):
        return True, "Detected packaging/environment wording with compliance or regulatory execution signals.", "medium"

    if policy_matched and (environmental_matched or contextual_matched):
        return False, "Policy-style wording found, but no direct seller-operational trigger was identified.", "low"

    return False, "No direct seller-operational impact identified.", "low"


def summarize_title(text: str, max_len: int = 80) -> str:
    """按语义边界（句号、逗号等）截断标题，保留完整语义。"""
    text = text.strip()
    if len(text) <= max_len:
        return text
    # 按优先级尝试在语义边界截断
    for sep in ["。", ". ", "；", "; ", "，", ", ", "—", " - "]:
        pos = text.rfind(sep, 0, max_len)
        if pos > max_len // 3:  # 至少保留 1/3 内容
            return text[: pos + len(sep)].rstrip()
    # 回退：在空格处截断（避免切割单词）
    space_pos = text.rfind(" ", 0, max_len)
    if space_pos > max_len // 2:
        return text[:space_pos].rstrip()
    return text[:max_len]


def summarize_event(text: str, event_type: str, region: str, relevant: bool) -> str:
    prefix = "潜在" if any(k in text.lower() for k in ["可能", "拟", "讨论", "rumor", "传闻"]) else "已监测到"
    region_zh = {"US": "美国", "EU": "欧洲", "UK": "英国", "Other": "其他地区"}.get(region, "相关区域")
    event_type_zh = {"tariff": "关税", "environment": "环保", "compliance": "合规", "logistics": "物流", "holiday": "节假日", "policy": "政策", "platform": "平台动态"}.get(event_type, "行业")
    if not relevant:
        return f"{prefix} {region_zh} {event_type_zh} 动态，但目前尚未解析出对跨境经营核心链路的实质性风险。"
    return f"{prefix} {region_zh} {event_type_zh} 事件，可能会影响当前的跨境履约、利润或合规操作。"


def build_sources(url: str | None) -> list[dict[str, str]]:
    if not url:
        return []
    return [{"name": "user-provided", "url": url}]


def infer_affected_sellers(seller_profile: dict[str, Any], relevant: bool) -> list[str]:
    if not relevant:
        return []
    labels: list[str] = []
    platform = seller_profile.get("platform")
    market = seller_profile.get("market")
    fulfillment_model = seller_profile.get("fulfillment_model")
    risk_profile = seller_profile.get("risk_profile")

    if platform and fulfillment_model and market:
        labels.append(f"布局 {market} 市场的 {platform} {fulfillment_model} 卖家")
    elif platform and market:
        labels.append(f"定位 {market} 市场的 {platform} 卖家")
    elif platform:
        labels.append(f"{platform} 卖家群体")
    elif market:
        labels.append(f"深耕 {market} 市场的跨境卖家")

    if risk_profile == "margin-sensitive":
        labels.append("对利润和客单价极度敏感的低客单卖家")
    if risk_profile == "compliance-sensitive":
        labels.append("主营涉电、带磁、母婴等强合规品类卖家")

    return labels


def infer_affected_categories(seller_profile: dict[str, Any], event_type: str) -> list[str]:
    category = seller_profile.get("category")
    if category:
        return [str(category)]
    if event_type in {"environment", "compliance"}:
        return []
    return []


def is_eu_small_parcel_tariff_event(event_type: str, region: str, text: str) -> bool:
    if event_type != "tariff" or region != "EU":
        return False
    lower = text.lower()
    return any(
        keyword in lower
        for keyword in [
            "小包税",
            "低价值包裹",
            "parcel",
            "de minimis",
            "customs",
            "免税",
            "税费",
            "duty",
        ]
    )


def is_europe_market(market: Any) -> bool:
    if not market:
        return False
    normalized = str(market).strip().upper()
    return normalized in {"EU", "DE", "FR", "IT", "ES", "NL", "BE", "PL"}


def infer_risk_level(event_type: str, confidence: str, text: str, relevant: bool, seller_profile: dict[str, Any], region: str) -> str:
    if not relevant:
        return "low"
    lower = text.lower()
    fulfillment_model = seller_profile.get("fulfillment_model")
    price_band = seller_profile.get("price_band")
    risk_profile = seller_profile.get("risk_profile")
    market = seller_profile.get("market")

    if confidence == "low":
        base = "medium"
    elif event_type in {"tariff", "environment"} and not any(k in lower for k in ["讨论", "可能", "rumor", "传闻", "投票"]):
        base = "high"
    elif any(k in lower for k in ["封号", "deactivate", "关店", "冻结", "资金冻结", "frozen", "下架", "remove", "take down", "诉讼", "lawsuit", "被起诉", "罚款", "penalty", "fined", "熔断", "爆仓"]):
        base = "high"
    else:
        base = "medium"

    if is_eu_small_parcel_tariff_event(event_type, region, text):
        if not is_europe_market(market):
            return "low"
        if fulfillment_model == "direct-mail":
            return "high"
        if fulfillment_model in {"fba", "overseas-warehouse", "platform-fulfillment"}:
            return "medium"
        return "low"

    if any(k in lower for k in ["封号", "deactivate", "关店", "冻结", "资金冻结", "frozen", "下架", "remove", "take down", "诉讼", "lawsuit", "被起诉", "罚款", "penalty", "fined", "驳回", "拒收"]):
        return "high"

    if event_type == "tariff" and fulfillment_model == "direct-mail" and price_band == "low":
        return "high"
    if event_type == "tariff" and risk_profile == "margin-sensitive":
        return "high"
    return base


def build_low_confidence_actions(event_type: str, seller_profile: dict[str, Any], text: str) -> list[str]:
    fulfillment_model = seller_profile.get("fulfillment_model")
    platform = seller_profile.get("platform")
    price_band = seller_profile.get("price_band")
    lower = text.lower()

    if event_type == "tariff":
        if platform == "independent-site" and fulfillment_model == "direct-mail":
            return [
                "今天先把 EU 直邮价卡、运费模板和优惠券别乱动，先算清税后到手价还有没有利润",
                "本周继续盯正式税费口径、购物车转化和退件率，必要时再拆分国家调价",
                "暂时别急着硬上低价冲量，细则没出来前别让广告把亏损放大",
            ]
        if fulfillment_model == "direct-mail" and price_band == "low":
            return [
                "今天先把低客单直邮 SKU 按税后毛利重排一遍，先圈出一批可能直接转负的货",
                "本周继续看执行时间、适用品类和竞品提价动作，再决定要不要切仓",
                "暂时别急着加预算冲单，规则还没坐实前先把亏损口堵住",
            ]
        if fulfillment_model == "fba":
            return [
                "今天先把 EU 站内主力 SKU 的到手价和 FBA 成本重算一遍，确认还有没有安全垫",
                "本周继续看税费是否外溢到清关和尾程，再判断提价还是控量",
                "暂时别急着大规模调仓，先别把本来能扛的库存节奏打乱",
            ]
        if fulfillment_model == "overseas-warehouse":
            return [
                "今天先把海外仓现货和在途补货拆开看，确认哪批货还能继续扛住税费波动",
                "本周继续盯清关、尾程和仓租有没有跟着抬头，再决定要不要调价格带",
                "暂时别急着一把切全量备货计划，先留出补货和承运商切换的余地",
            ]

    if event_type == "logistics":
        if fulfillment_model in {"fba", "overseas-warehouse"}:
            return [
                "今天先把未来 2-3 周补货批次和安全库存拉出来，看看哪几个站点最容易先断",
                "本周继续看港口/承运商后续通知，再决定是否前置补货或换线",
                "暂时别急着全盘改路由，先锁住最容易掉排名的核心 SKU",
            ]
        return [
            "今天先盘点承诺时效最紧的订单和 SKU，别让延误先炸差评",
            "本周继续看港口投票和物流商通知，再判断是否上调运费或延长时效承诺",
            "暂时别急着全面切换物流商，先验证高风险线路的真实波动",
        ]

    if event_type in {"environment", "compliance"}:
        if platform == "independent-site":
            return [
                "今天先圈出 EU 在售 SKU 里最可能碰包装/标签要求的货，别等客户投诉才回头改",
                "本周继续看正式生效时间、适用品类和替代材料报价，再决定分批切换",
                "暂时别急着全店换包材，先把高销量和高退货风险的 SKU 优先处理",
            ]
        return [
            "今天先把 EU 在售 SKU 的包装、标签和合规资料拉个短清单，先找明显缺口",
            "本周继续看正式口径和平台侧执行要求，再排补料和改版节奏",
            "暂时别急着全量改包装，先确认高风险品类和最早生效节点",
        ]

    if any(k in lower for k in ["讨论", "可能", "rumor", "传闻", "投票"]):
        return [
            "今天先确认这事是不是已经进到正式流程，别把传闻当成执行令",
            "本周继续盯官方更新和高可信来源，再决定是否升级成经营动作",
            "暂时别急着做大动作，先让团队知道哪里可能要变就够了",
        ]

    return [
        "今天先补执行时间、适用品类和影响对象，先把模糊信息补齐",
        "本周继续看官方口径和平台跟进，再决定是否升级动作",
        "暂时别急着拍板，信息没坐实前先别把资源打散",
    ]


def generate_actions(event_type: str, confidence: str, relevant: bool, seller_profile: dict[str, Any], text: str, region: str) -> list[str]:
    if not relevant:
        return []

    fulfillment_model = seller_profile.get("fulfillment_model")
    platform = seller_profile.get("platform")
    price_band = seller_profile.get("price_band")
    market = seller_profile.get("market")
    lower = text.lower()

    # 特殊处理 counterfeit/知识产权侵权/海关扣押类事件
    if event_type == "compliance" and any(k in lower for k in ["counterfeit", "假冒", "fake", "伪冒", "seized", "扣押", "trademark", "知识产权", "品牌侵权", "走私", "违禁品"]):
        return [
            "核查在售商品是否有品牌侵权风险，确认商品来源和授权链条",
            "检查目标市场海关政策和知识产权保护力度，避免高风险商品",
            "对涉及品牌的 SKU 做合规自查，必要时下架或调整库存",
        ]

    if is_eu_small_parcel_tariff_event(event_type, region, text):
        if not is_europe_market(market):
            return [
                "这条先记成欧洲区域性风险信号，不要按全市场统一改价或改库存",
                "只检查你是否还有 EU 直发或欧洲清关链路暴露，没有就先降级观察",
                "继续等正式细则，避免把不相关市场也卷进同一波动作",
            ]
        if fulfillment_model in {"fba", "overseas-warehouse", "platform-fulfillment"}:
            return build_low_confidence_actions(event_type, seller_profile, text)

    if event_type == "tariff" and any(k in lower for k in ["小包", "低价值包裹", "免税", "税费"]):
        if platform == "independent-site" and fulfillment_model == "direct-mail":
            return [
                "今天先盘点 EU 直邮订单占比和最脆弱的低毛利 SKU",
                "本周评估定价、运费模板和仓配重构方案",
                "持续监控税费细则、退件率和转化率波动",
            ]
        if fulfillment_model == "direct-mail" and price_band == "low":
            return [
                "今天先复核低客单 SKU 的税后毛利率和到手利润",
                "本周评估是否需要把高风险 SKU 切到海外仓或本地履约",
                "持续监控正式执行时间、适用品类和竞品是否提价",
            ]
        if fulfillment_model == "fba":
            return [
                "今天先把 EU 站内主力 SKU 的到手价、FBA 成本和提价空间重算一遍",
                "本周复核 EU 市场价格带和利润空间是否需要微调",
                "持续监控政策是否外溢影响清关和尾程成本",
            ]
        if fulfillment_model == "overseas-warehouse":
            return [
                "今天先拆开看海外仓现货、在途补货和尾程成本，确认哪段最先吃掉利润",
                "本周复核 EU 市场价格带、仓租和周转结构是否需要微调",
                "持续监控政策是否外溢影响清关和尾程成本",
            ]

    if confidence == "low":
        return build_low_confidence_actions(event_type, seller_profile, text)
    return ACTIONS_MAP.get(event_type, ACTIONS_MAP["platform"])[:3]


def build_output(input_data: dict[str, Any]) -> dict[str, Any]:
    validated = validate_input(input_data)
    content = validated["content"]
    seller_profile = validated["seller_profile"]
    event_type = detect_event_type(content)
    region = detect_region(content, validated.get("region_hint"))
    is_relevant, relevance_reason, relevance_confidence = classify_relevance(content)
    title = summarize_title(content)
    summary = summarize_event(content, event_type, region, is_relevant)
    impact_dimensions = IMPACT_MAP.get(event_type, ["cost"]) if is_relevant else []
    affected_sellers = infer_affected_sellers(seller_profile, is_relevant)
    affected_categories = infer_affected_categories(seller_profile, event_type) if is_relevant else []
    risk_level = infer_risk_level(event_type, relevance_confidence, content, is_relevant, seller_profile, region)
    suggested_actions = generate_actions(event_type, relevance_confidence, is_relevant, seller_profile, content, region)
    IMPACT_TEXT_ZH = {
        "cost": "硬性运营与履约成本攀升",
        "pricing": "前端售价与利润空间压缩",
        "inventory": "在库积压或库容流转断裂",
        "compliance": "强合规门槛导致商品无预警下架",
        "supply_chain": "全链路清关与尾程交付受阻",
        "demand": "目标市场消费端转化率下挫",
    }
    
    impact_zh_list = [IMPACT_TEXT_ZH.get(d, "业务链路") for d in impact_dimensions]
    
    # 商业化深度解析：优先使用 LLM，失败回退到模板拼接
    if not is_relevant:
        impact_reasoning = "该动态暂未解析出足以阻断跨境核心链路的实质性风险，建议作为常态背景信息保持关注。"
    else:
        platform_hint = seller_profile.get("platform", "全平台")
        model_hint = seller_profile.get("fulfillment_model", "跨境")
        impact_reasoning = ""  # 先初始化，LLM 成功后覆盖，否则走 fallback
        _llm_sop_data: dict[str, Any] = {}  # 提前初始化，避免 dir() hack
        # 尝试 LLM 深度分析
        llm_analysis = llm_client.generate_risk_analysis(
            event_content=content,
            event_type=event_type,
            region=region,
            platform=str(platform_hint),
            fulfillment_model=str(model_hint),
        )
        if llm_analysis:
            # LLM 成功：使用 AI 生成的研判和建议
            impact_reasoning = str(llm_analysis.get("impact", "")).strip()
            llm_actions = llm_analysis.get("actions", [])
            if isinstance(llm_actions, list) and llm_actions:
                suggested_actions = [str(a) for a in llm_actions[:5]]
            llm_title = str(llm_analysis.get("title", "")).strip()
            if llm_title:
                title = llm_title
            # 提取 LLM 生成的路径级 SOP
            llm_sop = llm_analysis.get("sop")
            if isinstance(llm_sop, dict):
                _llm_sop_data = llm_sop
            else:
                logger.warning("LLM 返回的 sop 字段不是 dict，类型：%s", type(llm_sop).__name__)
            logger.debug("LLM 深度分析成功")
        if not impact_reasoning or "暂未解析" in impact_reasoning:
            # Fallback：模板拼接
            summary_hint = summary[:120].strip("。").strip() + "..." if len(summary) > 120 else summary.strip("。")
            impact_reasoning = f"【雷达研判】该事件将从 {', '.join(impact_zh_list)} 维度冲击 {platform_hint} 业务。关键细节提示：{summary_hint}。这将直接导致 {model_hint} 链路的稳定性受挫，建议立即启动 SOP 响应。"
    # 收集 LLM SOP
    _llm_sop_result = _llm_sop_data
    return {
        "event_title": title,
        "event_summary": summary,
        "event_type": event_type,
        "region": region,
        "is_relevant": is_relevant,
        "relevance_reason": relevance_reason,
        "affected_sellers": affected_sellers,
        "affected_categories": affected_categories,
        "impact_dimensions": impact_dimensions,
        "risk_level": risk_level,
        "impact_reasoning": impact_reasoning,
        "suggested_actions": suggested_actions,
        "confidence": relevance_confidence,
        "sources": build_sources(validated.get("url")),
        "llm_sop": _llm_sop_result,
    }


def normalize_output(result: dict[str, Any]) -> dict[str, Any]:
    result["event_type"] = result["event_type"] if result["event_type"] in EVENT_TYPES else "platform"
    result["region"] = result["region"] if result["region"] in REGIONS else "Other"
    result["risk_level"] = result["risk_level"] if result["risk_level"] in RISK_LEVELS else "medium"
    result["confidence"] = result["confidence"] if result["confidence"] in CONFIDENCE_LEVELS else "low"
    result["impact_dimensions"] = [d for d in result.get("impact_dimensions", []) if d in IMPACT_DIMENSIONS][:3]
    result["suggested_actions"] = [str(x) for x in result.get("suggested_actions", [])][:5]
    result["affected_sellers"] = [str(x) for x in result.get("affected_sellers", [])]
    result["affected_categories"] = [str(x) for x in result.get("affected_categories", [])]
    result["sources"] = [s for s in result.get("sources", []) if isinstance(s, dict) and s.get("url")]
    return result


def render_human_summary(result: dict[str, Any]) -> str:
    lines = [
        f"相关性：{'相关' if result.get('is_relevant') else '不相关'}",
        f"事件类型：{result.get('event_type', 'policy')}",
        f"区域：{result.get('region', 'Other')}",
        f"风险等级：{result.get('risk_level', 'medium')}",
        f"置信度：{result.get('confidence', 'low')}",
        f"摘要：{result.get('event_summary', '')}",
        f"原因：{result.get('relevance_reason', '')}",
    ]
    impact_dimensions = result.get("impact_dimensions", [])
    if impact_dimensions:
        lines.append(f"主要影响维度：{', '.join(impact_dimensions)}")
    suggested_actions = result.get("suggested_actions", [])
    if suggested_actions:
        lines.append("建议动作：")
        lines.extend([f"- {action}" for action in suggested_actions])
    return "\n".join(lines)


def read_input() -> dict[str, Any]:
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        maybe_path = Path(arg)
        if maybe_path.exists():
            return json.loads(maybe_path.read_text(encoding="utf-8"))
        return json.loads(arg)
    raw = sys.stdin.read().strip()
    if not raw:
        raise ValueError("Provide JSON via file path, CLI string, or stdin")
    return json.loads(raw)


def main() -> None:
    try:
        input_data = read_input()
        result = normalize_output(build_output(input_data))
        if "--human" in sys.argv:
            print(render_human_summary(result))
        else:
            print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as exc:
        print(json.dumps({"error": str(exc)}, ensure_ascii=False, indent=2), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
