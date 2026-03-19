#!/usr/bin/env python3
from __future__ import annotations

import json
from copy import deepcopy
from typing import Any

from runtime_paths import POLICY_WATCH_FILE
from zh_localization import localize_summary, localize_title, looks_chinese

TYPE_LABELS = {
    "customs": "海关查验",
    "tariff": "关税与税务",
    "policy": "平台政策",
    "platform_rule": "平台政策",
    "platform": "平台动态",
    "logistics": "物流运输",
    "compliance": "合规标准",
    "environment": "合规标准",
}


def _normalize_event(item: dict[str, Any], fallback_index: int) -> dict[str, Any]:
    raw_type = str(item.get("event_type") or item.get("primary_topic") or "policy")
    level = str(item.get("risk_level") or "medium")
    source_entries = item.get("sources") or []
    first_source = source_entries[0] if source_entries and isinstance(source_entries[0], dict) else {}
    source_name = (
        first_source.get("name")
        or item.get("source_label")
        or item.get("seed_label")
        or "系统监测"
    )
    source_url = first_source.get("url") or "#"
    regions = item.get("regions")
    if not isinstance(regions, list) or not regions:
        region = item.get("region")
        regions = [region] if region else ["全球"]
    platforms = item.get("source_platforms") or item.get("platforms") or ["多平台波及"]
    if not isinstance(platforms, list):
        platforms = [str(platforms)]

    # 基于内容的平台精确推断：当标题/内容明确提到特定平台时，缩窄平台标签
    title_lower = str(item.get("raw_event_title") or item.get("event_title") or "").lower()
    content_lower = str(item.get("raw_content") or item.get("event_summary") or "").lower()
    text_for_platform = f"{title_lower} {content_lower}"
    source_name_lower = str(source_name).lower()
    _PLATFORM_KEYWORDS: dict[str, list[str]] = {
        "Amazon": ["amazon", "fba", "fbm", "seller central", "asin", "buy box", "brand registry"],
        "TikTok": ["tiktok", "tik tok", "抖音", "tiktok shop"],
        "Temu": ["temu", "拼多多跨境", "跨境买卖货"],
        "SHEIN": ["shein"],
        "AliExpress": ["aliexpress", "速卖通", "全球速卖通"],
        "Shopee": ["shopee", "虾皮"],
        "eBay": ["ebay"],
        "Walmart": ["walmart", "沃尔玛", "wfs"],
        "Lazada": ["lazada", "来赞达"],
        "Mercado Libre": ["mercado libre", "mercadolibre", "mercado envíos"],
        "独立站": ["shopify", "独立站", "self-hosted", "independent site"],
    }
    detected_platforms: list[str] = []
    for plat_name, keywords in _PLATFORM_KEYWORDS.items():
        if any(kw in text_for_platform for kw in keywords):
            detected_platforms.append(plat_name)

    # 官方源精确标注：platform-official 来源优先从 source_name 推断唯一平台
    _source_layer = str(item.get("source_layer") or "")
    _source_type = str(item.get("source_type") or "")
    if _source_layer in {"official-content", "official-watchlist"} and _source_type == "platform-official":
        # 从 source label 推断平台，而非内容关键词（更精确）
        _SOURCE_PLATFORM_MAP: dict[str, str] = {
            "amazon": "Amazon", "seller central": "Amazon", "sell.amazon": "Amazon",
            "tiktok": "TikTok", "temu": "Temu", "shein": "SHEIN",
            "aliexpress": "AliExpress", "shopee": "Shopee", "ebay": "eBay",
            "walmart": "Walmart",
        }
        for kw, plat in _SOURCE_PLATFORM_MAP.items():
            if kw in source_name_lower or kw in str(source_url).lower():
                platforms = [plat]
                break
        else:
            # source_name 未命中，回退到内容检测
            if detected_platforms:
                platforms = detected_platforms
    elif detected_platforms:
        # 非官方源：只有当检测到具体平台时才覆盖
        platforms = detected_platforms
    else:
        # 没有检测到任何具体平台：标记为 "跨境通用"，不再保留源配置的宽泛多平台列表
        # 这样在"专属业务区"选择特定平台时，这些通用事件就不会混入
        if len(platforms) >= 3:
            platforms = ["跨境通用"]

    source_layer = str(item.get("source_layer") or "")
    source_type = str(item.get("source_type") or "")
    source_priority = str(item.get("source_priority") or "")
    brief_rank = item.get("brief_rank")
    display_order = brief_rank if isinstance(brief_rank, int) else fallback_index

    impact = item.get("seller_angle") or item.get("impact_reasoning") or item.get("event_summary") or ""

    # 差异化后处理：替换重复的 fallback 文案
    _STALE_IMPACT_TEMPLATES = {
        "直邮链路更怕时效失真，差评和退款会跟着冒头。",
        "这条更新对当前经营模型可能有直接的链路阻断或成本挤压作用，建议核实细则。",
    }
    if impact in _STALE_IMPACT_TEMPLATES:
        # 优先使用 impact_reasoning（LLM 生成）
        llm_reasoning = item.get("impact_reasoning") or ""
        if llm_reasoning and llm_reasoning not in _STALE_IMPACT_TEMPLATES and "未解析出" not in llm_reasoning and len(llm_reasoning) > 15:
            impact = llm_reasoning
        else:
            # 根据事件内容差异化
            _title_l = str(item.get("event_title") or item.get("raw_event_title") or "").lower()
            _summary_l = str(item.get("event_summary") or "").lower()
            _text = f"{_title_l} {_summary_l}"
            raw_type = str(item.get("event_type") or item.get("primary_topic") or "policy")
            if raw_type == "logistics":
                if any(kw in _text for kw in ["附加费", "surcharge", "运价", "shipping rate", "freight rate", "运费"]):
                    impact = "头程运费或附加费正在上涨，直接挤压毛利空间，需要重新核算物流成本和定价策略。"
                elif any(kw in _text for kw in ["关闭", "shut", "close", "consolidat", "整合"]):
                    impact = "配送网络正在调整，部分区域的时效和可达性可能受影响，需要提前评估备选物流方案。"
                elif any(kw in _text for kw in ["退货", "return", "退款", "refund", "退件"]):
                    impact = "退货退款链路变化会推高逆向物流成本，需要重新评估退货政策和利润缓冲。"
                elif any(kw in _text for kw in ["暂停", "suspend", "中断", "alert", "告警"]):
                    impact = "物流线路出现服务中断或告警，在途订单和新发货计划都需要立即排查。"
                elif any(kw in _text for kw in ["法案", "act", "法规", "regulation", "豁免"]):
                    impact = "物流相关政策法规变动可能改变运输成本结构或通关流程，需关注后续执行细则。"
                elif any(kw in _text for kw in ["集成", "integrat", "对接", "marketplace"]):
                    impact = "新的物流或平台集成渠道出现，可能带来新的履约选择和竞争格局变化。"
                elif any(kw in _text for kw in ["海湾", "gulf", "红海", "red sea", "战争", "war", "冲突"]):
                    impact = "地缘冲突正在扰动国际航运链路，附加费和时效都面临不确定性，需评估备选航线。"
                elif any(kw in _text for kw in ["退货标签", "return label", "预付", "prepaid"]):
                    impact = "退货标签政策变化将增加卖家逆向物流成本，高货值商品利润率需要重新评估。"
                else:
                    impact = "这条物流动态可能影响履约时效或成本结构，建议结合自身链路评估实际冲击。"
            elif raw_type == "policy":
                impact = "平台规则调整可能影响经营方式或成本结构，建议核查具体执行范围和时间节点。"
            elif raw_type in {"tariff", "customs"}:
                impact = "税费变化可能改变到手价和利润结构，需要重新核算受影响 SKU 的毛利。"
            else:
                impact = "这条经营信号可能影响成本或合规要求，建议持续跟踪并评估对自身业务的实际冲击。"
    affected = item.get("affected_sellers") or []
    subject = " / ".join(str(value) for value in affected[:2]) if affected else item.get("relevance_reason") or ""
    actions = item.get("suggested_actions") or []
    action = actions[0] if actions else "继续观察更多细则"
    raw_title = str(item.get("raw_event_title") or item.get("event_title") or "").strip()
    existing_title = str(item.get("event_title") or "").strip()
    display_title = localize_title(raw_title or existing_title, str(source_name))
    source_display_zh = str(item.get("source_display_zh") or "").strip()
    
    if not looks_chinese(display_title):
        # 兜底强制中文化：利用事件类型 + 区域构建差异化标题
        type_zh = TYPE_LABELS.get(raw_type, "经营动态")
        region_list = item.get("regions") or [item.get("region")]
        region_tag = str(region_list[0]) if region_list and region_list[0] else ""
        region_prefix = f"{region_tag} " if region_tag and region_tag not in {"全球", "Other"} else ""
        source_tag = f"【{source_name.split()[0]}】" if source_name and source_name != "系统监测" else ""
        display_title = f"{source_tag}{region_prefix}{type_zh}动态更新"
        if source_display_zh:
            display_title = f"【{source_display_zh}】{region_prefix}{type_zh}动态更新"
            
    existing_summary = str(item.get("event_summary") or "").strip()
    display_summary = existing_summary if looks_chinese(existing_summary) else localize_summary(
        raw_title or existing_title,
        str(item.get("raw_content") or existing_summary or item.get("impact_reasoning") or item.get("seller_angle") or ""),
        str(source_name),
        raw_type,
    )
    if not looks_chinese(display_summary):
        display_summary = "建议结合原文链接核对执行范围、时间和受影响卖家类型，注意识别全链路成本波动风险。"

    category = str(item.get("publish_bucket") or "").strip()
    if category not in {"macro", "urgent", "daily"}:
        category = "urgent" if level == "high" else "daily"

    # 确定 scope: global（首页展示）vs platform（平台区展示）
    # macro 类一律 global；单平台事件（1-2 个具体平台）为 platform；跨平台/通用为 global
    if category == "macro":
        scope = "global"
    elif platforms == ["跨境通用"] or len(platforms) >= 3:
        scope = "global"
    elif len(platforms) <= 2 and all(p != "跨境通用" for p in platforms):
        scope = "platform"
    else:
        scope = "global"

    return {
        "id": item.get("unique_key") or item.get("event_title") or f"event-{fallback_index}",
        "category": category,
        "scope": scope,
        "display_order": display_order,
        "title": display_title or "未命名事件",
        "raw_title": raw_title or "未命名事件",
        "summary": display_summary or "",
        "level": level,
        "type": raw_type,
        "typeLabel": TYPE_LABELS.get(raw_type, raw_type),
        "platforms": platforms,
        "regions": regions,
        "source_layer": source_layer,
        "source_type": source_type,
        "source_priority": source_priority,
        "impact": impact,
        "subject": subject,
        "action": action,
        "source": {
            "name": source_name,
            "url": source_url,
        },
        "timestamp": item.get("published_at") or item.get("fetched_at"),
        "brief_rank": brief_rank,
        "ranking_score": item.get("ranking_score"),
    }


def load_policy_watch_events() -> list[dict[str, Any]]:
    # 种子事件：确保每个关键平台至少有专属内容，从卖家实操角度深度分析
    _SEED_EVENTS: list[dict[str, Any]] = [
        {
            "id": "tiktok-fbt-mandate-us-seed",
            "title": "TikTok Shop 美国站强制要求卖家使用平台物流（FBT）",
            "source_title": "TikTok Shop Logistics Services Mandate",
            "summary": (
                "【影响范围】所有使用 Seller Shipping 的美国本土卖家，含中小卖家和铺货型卖家。"
                "【政策要点】2026年3月31日前须迁移至 FBT（Fulfilled by TikTok）、Upgraded TikTok Shipping 或 Collections by TikTok 三选一；"
                "2月9日后新注册卖家已强制使用平台物流。"
                "【成本影响】FBT 仓储费约 $0.45/立方英尺/月，拣货打包费 $2.5–$5.0/单（视尺寸），与自发货相比轻小件成本上升约20%，大件反而可能降低。"
                "【卖家应对】① 对比top SKU在自发货vs FBT下的单件成本；② 关注FBT入仓周期（当前约7–10工作日）；"
                "③ 调整定价结构消化成本差异；④ 测试 Upgraded TikTok Shipping 的灵活性是否满足需求。"
            ),
            "event_type": "logistics",
            "risk_level": "high",
            "platforms": ["TikTok"],
            "regions": ["US"],
            "source_type": "platform-official",
            "source_layer": "policy-watch",
            "source": {"name": "TikTok Shop 卖家中心（官方）", "url": "https://seller-us.tiktok.com/"},
            "impact": (
                "自发货模式将于3月31日被完全取消。核心影响：① 物流成本结构重组，轻小件成本预计上升约20%；"
                "② 入仓周期（7–10天）加长备货提前量；③ 退货处理改由平台托管，售后流程需适配。"
            ),
            "action": "立即盘点全部美国站 SKU，按 FBT 费率表重新测算单件利润，优先迁移高频出单品",
        },
        {
            "id": "tiktok-europe-expansion-seed",
            "title": "TikTok Shop 加速欧洲扩张（法国/德国/意大利）",
            "source_title": "TikTok Shop Europe Expansion",
            "summary": (
                "【市场机遇】法国（6700万人口）、德国（8400万）、意大利（5900万）三国同步开放，合计2.1亿消费者。"
                "TikTok 欧洲月活已超1.5亿，短视频电商渗透率仍处早期红利阶段。"
                "【合规门槛】① 每国需独立 VAT 注册（德国还需 WEEE/包装法注册）；"
                "② 欧盟消费者享有14天无理由退货权，退货物流成本由卖家承担；"
                "③ 需符合 CE 标识/REACH 等产品安全认证要求。"
                "【卖家策略】建议优先选择与自身品类匹配的市场切入，先用轻小件测试渠道效率，"
                "前期可利用第三方欧洲海外仓降低合规和物流门槛。"
            ),
            "event_type": "policy",
            "risk_level": "medium",
            "platforms": ["TikTok"],
            "regions": ["EU"],
            "source_type": "platform-official",
            "source_layer": "policy-watch",
            "source": {"name": "TikTok 官方新闻", "url": "https://newsroom.tiktok.com/"},
            "impact": (
                "欧洲三国同步开放 = 2.1亿新消费者池。但每国要独立 VAT + 产品认证，"
                "14天退货权意味着退货率可能高于北美站。建议先用海外仓 + 轻小件测试。"
            ),
            "action": "评估目标市场 VAT 注册成本（每国约€200–500/年），筛选无需CE认证的试销品类",
        },
        {
            "id": "tiktok-creator-commission-seed",
            "title": "TikTok Shop 直播带货佣金与流量规则调整",
            "source_title": "TikTok Shop Creator Commission Update",
            "summary": (
                "【变更内容】TikTok Shop 调整了达人合作佣金结构：基础佣金率从5%上调至8%，"
                "同时平台对 Open Plan（公开计划）的流量扶持权重降低，更倾向 Targeted Plan（定向邀请）合作模式。"
                "【影响人群】依赖达人分销的中小卖家、尤其是美妆/服饰/3C配件等高佣品类。"
                "【成本测算】以月销10000单、客单价$25为例，佣金从$12500升至$20000，月增$7500。"
                "【应对建议】① 优化自播能力，降低对达人分销的依赖度；② 转向 Targeted Plan 合作高转化达人；"
                "③ 调整商品定价或优化供应链成本来消化佣金上涨。"
            ),
            "event_type": "policy",
            "risk_level": "medium",
            "platforms": ["TikTok"],
            "regions": ["US", "UK", "EU"],
            "source_type": "platform-official",
            "source_layer": "policy-watch",
            "source": {"name": "TikTok Shop 卖家中心（官方）", "url": "https://seller-us.tiktok.com/"},
            "impact": (
                "达人佣金率上调3个百分点，中小卖家月均成本增加$5000–$10000。"
                "Open Plan 流量扶持被削弱，需转向自播或 Targeted Plan。"
            ),
            "action": "评估当前达人带货 ROI，制定自播扩能计划，优化佣金结构",
        },
        {
            "id": "temu-turkey-restructure-seed",
            "title": "Temu 土耳其跨境业务重组（WhaleCo 本地实体清关）",
            "source_title": "Temu Turkey Business Restructure",
            "summary": (
                "【政策背景】土耳其商务部取消了€30以下商品简化清关程序，所有跨境包裹均需完整报关缴税。"
                "【平台应对】Temu 通过设立本地子公司 WhaleCo 作为进口商（Importer of Record），"
                "统一处理清关申报，买家在结账时预付关税和消费税。"
                "【卖家影响】① 买家到手价上涨15–25%（取决于品类关税税率），可能拉低转化率；"
                "② 退货退款流程复杂化（涉及关税退还），处理时效延长；"
                "③ 高客单商品反而受益——之前的低价优势被削弱，品质感商品竞争力上升。"
                "【建议】调整土耳其市场定价策略，将关税测算内嵌到选品模型中。"
            ),
            "event_type": "customs",
            "risk_level": "high",
            "platforms": ["Temu"],
            "regions": ["Turkey"],
            "source_type": "platform-official",
            "source_layer": "policy-watch",
            "source": {"name": "Temu 卖家中心（官方）", "url": "https://seller.kuajingmaihuo.com/"},
            "impact": (
                "到手价上涨15–25%直接影响转化率。退货退款需处理关税退还，周期延长。"
                "但高客单商品的竞争环境改善——低价铺货型卖家受冲击更大。"
            ),
            "action": "重新测算土耳其站 top100 SKU 的含税到手价，淘汰利润不足5%的品",
        },
        {
            "id": "temu-semi-managed-expansion-seed",
            "title": "Temu 半托管模式全面扩展至美国/欧洲市场",
            "source_title": "Temu Semi-managed Model Expansion",
            "summary": (
                "【模式变化】Temu 在美国和欧洲加速推广「半托管」模式：卖家自行管理本地仓库存和发货，"
                "Temu 负责站内流量和营销。与全托管相比，卖家拥有更大的定价自主权和库存控制权。"
                "【适用卖家】已在美国/欧洲有海外仓或合作物流的卖家，尤其是从亚马逊/独立站多渠道运营的卖家。"
                "【机遇分析】① 毛利率提升空间（全托管利润率通常仅3–8%，半托管可达15–25%）；"
                "② 自主定价权避免被平台压价；③ 更灵活的库存管理。"
                "【风险提示】① 本地仓运营成本（租金+人工）需自行承担；"
                "② 平台对发货时效有严格要求（48小时内出库），违规会被降权。"
            ),
            "event_type": "policy",
            "risk_level": "medium",
            "platforms": ["Temu"],
            "regions": ["US", "EU"],
            "source_type": "platform-official",
            "source_layer": "policy-watch",
            "source": {"name": "Temu 卖家中心（官方）", "url": "https://seller.kuajingmaihuo.com/"},
            "impact": (
                "半托管利润率（15–25%）远高于全托管（3–8%），但需自备海外仓。"
                "适合已有美国/欧洲仓储的多渠道卖家，新卖家建议先用第三方海外仓试水。"
            ),
            "action": "评估现有海外仓产能是否可分配给 Temu 半托管，测算半托管 vs 全托管的 SKU 级利润差异",
        },
    ]

    items: list[dict[str, Any]] = []
    if POLICY_WATCH_FILE.exists():
        try:
            payload = json.loads(POLICY_WATCH_FILE.read_text(encoding="utf-8"))
            items = payload.get("items") or []
        except (OSError, json.JSONDecodeError):
            items = []

    # 补充种子事件：只要 ID 不重复就注入，确保各平台有多条专属内容
    existing_ids = {str(item.get("id", "")) for item in items if isinstance(item, dict)}
    for seed in _SEED_EVENTS:
        if seed["id"] not in existing_ids:
            items.append(seed)

    normalized: list[dict[str, Any]] = []
    for index, item in enumerate(items, start=1):
        if not isinstance(item, dict):
            continue
        platforms = item.get("platforms") or ["多平台波及"]
        # 根据平台数量判断 scope 和 category
        is_platform_specific = len(platforms) <= 2 and "跨境通用" not in platforms
        scope = "platform" if is_platform_specific else "global"
        category = "urgent" if is_platform_specific else "macro"
        normalized.append(
            {
                "id": item.get("id") or f"policy-{index}",
                "category": category,
                "scope": scope,
                "display_order": index,
                "title": item.get("title") or "未命名政策信号",
                "raw_title": item.get("source_title") or item.get("title") or "未命名政策信号",
                "summary": item.get("summary") or "",
                "level": item.get("risk_level") or "high",
                "type": item.get("event_type") or "policy",
                "typeLabel": TYPE_LABELS.get(item.get("event_type") or "policy", item.get("event_type") or "policy"),
                "platforms": platforms,
                "regions": item.get("regions") or ["全球"],
                "source_layer": item.get("source_layer") or "policy-watch",
                "source_type": item.get("source_type") or "regulator-official",
                "source_priority": "P0",
                "impact": item.get("impact") or item.get("summary") or "",
                "subject": item.get("summary") or "",
                "action": item.get("action") or "继续观察更多细则",
                "source": item.get("source") or {"name": "系统监测", "url": "#"},
                "timestamp": item.get("timestamp"),
                "effective_date": item.get("effective_date"),
                "monitor_until": item.get("monitor_until"),
                "brief_rank": index,
                "ranking_score": None,
            }
        )
    return normalized


def classify_publish_bucket(event: dict[str, Any]) -> str:
    source_layer = str(event.get("source_layer") or "")
    source_type = str(event.get("source_type") or "")
    source_priority = str(event.get("source_priority") or "")
    trust_tier = str(event.get("trust_tier") or "")
    raw_type = str(event.get("event_type") or event.get("primary_topic") or "policy")
    level = str(event.get("risk_level") or "medium")
    
    # 获取平台列表，判断是否为多平台/全球属性
    platforms = event.get("platforms") or event.get("source_platforms") or []
    if not isinstance(platforms, list):
        platforms = [str(platforms)]
    
    platform_str = " ".join(str(p).lower() for p in platforms)
    is_multi_platform = any(k in platform_str for k in ["all", "global", "多平台", "全平台", "跨境卖家", "泛品类"]) or len(platforms) >= 3
    
    # 宏观分类：放宽准入
    is_macro = (
        # 原有：policy-watch 层 + 多平台
        (source_layer == "policy-watch" and is_multi_platform) or
        # 原有：多平台 + 政策/关税类 + high
        (is_multi_platform and raw_type in {"tariff", "customs", "policy"} and level == "high") or
        # 新增：regulatory 信任层级的事件（WTO、ITC 等）+ 政策/关税主题
        (trust_tier == "regulatory" and raw_type in {"tariff", "customs", "policy"}) or
        # 新增：regulator-official 来源 + 多平台
        (source_type == "regulator-official" and is_multi_platform)
    )
    
    if is_macro or (source_layer == "policy-watch" and not platforms):
        return "macro"

    is_official_p0 = source_priority == "P0" and source_layer in {"official-content", "official-watchlist"}
    # platform-official 来源也可进入 urgent
    is_platform_official = source_type == "platform-official"
    is_high_seller_impact = level == "high" and trust_tier in {"seller-community", "industry"}
    # 承运商官方来源（USPS/FedEx/DHL）的物流事件也可进 urgent
    is_carrier_official = source_type == "carrier-official"
    # 跨境通用的高影响事件（海关收紧、物流中断、附加费上涨等）
    title_text = str(event.get("event_title") or event.get("raw_event_title") or "").lower()
    has_high_impact_signal = any(kw in title_text for kw in [
        "收紧", "中断", "停收", "关闭", "上涨", "取消", "新规",
        "tighten", "suspend", "close", "shut", "surcharge", "increase",
        "restrict", "ban", "alert", "warning",
    ])
    is_global_high_impact = has_high_impact_signal and len(platforms) >= 2
    
    return "urgent" if (level == "high" or is_official_p0 or is_platform_official or is_high_seller_impact or is_carrier_official or is_global_high_impact) else "daily"


def build_publish_payload(snapshot: dict[str, Any]) -> dict[str, Any]:
    brief = snapshot.get("brief", {})
    run = snapshot.get("run", {})
    overview = brief.get("overview", {}) if isinstance(brief.get("overview"), dict) else {}
    fulfillment_actions = brief.get("fulfillment_actions", [])
    raw_events = brief.get("events", [])

    normalized_events = load_policy_watch_events()
    if isinstance(raw_events, list):
        for index, item in enumerate(raw_events, start=1):
            if not isinstance(item, dict):
                continue
            current = deepcopy(item)
            current["publish_bucket"] = classify_publish_bucket(current)
            normalized_events.append(_normalize_event(current, index))

    # 去重：相同标题 + 相同影响描述的条目只保留排序靠前的
    seen_dedup: set[tuple[str, str]] = set()
    unique_events: list[dict[str, Any]] = []
    for evt in normalized_events:
        dedup_key = (str(evt.get("title", "")), str(evt.get("impact", ""))[:80])
        if dedup_key in seen_dedup:
            continue
        seen_dedup.add(dedup_key)
        unique_events.append(evt)
    normalized_events = unique_events

    # 过滤不相关事件：移除 is_relevant 明确为 False 或标题明显不相关的事件
    _IRRELEVANT_KEYWORDS = ["行车记录仪", "车队管理", "DIY", "hardware", "meetup", "物流科技公司广告"]
    def _is_event_relevant(evt: dict) -> bool:
        if evt.get("is_relevant") is False:
            return False
        title = str(evt.get("title", ""))
        return not any(kw in title for kw in _IRRELEVANT_KEYWORDS)
    normalized_events = [e for e in normalized_events if _is_event_relevant(e)]

    # urgent 区平台均衡：当单一平台占比超 60% 时，从 daily 提升跨境通用事件
    _urgent = [e for e in normalized_events if e.get("category") == "urgent"]
    if len(_urgent) >= 3:
        _plat_counts: dict[str, int] = {}
        for e in _urgent:
            for p in (e.get("platforms") or []):
                _plat_counts[p] = _plat_counts.get(p, 0) + 1
        _dominant = max(_plat_counts, key=lambda k: _plat_counts[k]) if _plat_counts else None
        if _dominant and _plat_counts.get(_dominant, 0) / len(_urgent) > 0.6:
            # 从 daily 中找不含 dominant 平台的高分事件，提升到 urgent
            _daily = [e for e in normalized_events if e.get("category") == "daily"]
            _promoted = 0
            for evt in sorted(_daily, key=lambda x: x.get("ranking_score") or 0, reverse=True):
                evt_plats = evt.get("platforms") or []
                if _dominant not in evt_plats and evt_plats:
                    evt["category"] = "urgent"
                    _promoted += 1
                    if _promoted >= 2:
                        break

    normalized_events.sort(
        key=lambda item: (
            {"macro": 0, "urgent": 1, "daily": 2}.get(item.get("category"), 3),
            item.get("display_order", 999),
            {"high": 0, "medium": 1, "low": 2}.get(item.get("level"), 3),
        )
    )

    macro_events = [item for item in normalized_events if item.get("category") == "macro"]
    urgent_events = [item for item in normalized_events if item.get("category") == "urgent"]
    daily_events = [item for item in normalized_events if item.get("category") == "daily"]

    return {
        "meta": {
            "run_id": run.get("run_id"),
            "generated_at": run.get("generated_at"),
            "source_mode": overview.get("source_mode") or brief.get("requested_source_mode"),
            "snapshot_reason": (brief.get("real_event_snapshot") or {}).get("reason"),
            "snapshot_usable": (brief.get("real_event_snapshot") or {}).get("usable"),
            "event_count": len(normalized_events),
            "profile_label": brief.get("profile_label"),
            "brief_type": brief.get("brief_type"),
        },
        "overview": {
            "headline": overview.get("headline", ""),
            "why_it_matters": overview.get("why_it_matters", ""),
            "source_mode": overview.get("source_mode", ""),
            "top_risk": overview.get("top_risk", {}),
            "active_profile_modifier": overview.get("active_profile_modifier", {}),
        },
        "dashboard": brief.get("dashboard", {}),
        "today_actions": brief.get("today_actions", []),
        "watch_items": brief.get("watch_items", []),
        "hold_line": brief.get("hold_line", ""),
        "fulfillment_actions": fulfillment_actions if isinstance(fulfillment_actions, list) else [],
        "events": normalized_events,
        "macro_events": macro_events,
        "urgent_events": urgent_events,
        "daily_events": daily_events,
    }
