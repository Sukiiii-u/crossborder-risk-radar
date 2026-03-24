#!/usr/bin/env python3
from __future__ import annotations

import logging
import re
from typing import Any

import llm_client

logger = logging.getLogger("zh_localization")


def looks_chinese(text: str | None) -> bool:
    if not text:
        return False
    return any("\u4e00" <= ch <= "\u9fff" for ch in text)


def normalize_space(text: str | None) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip()


def localize_title(raw_title: str, source_label: str = "") -> str:
    title = normalize_space(raw_title)
    # 去掉播客/节目编号前缀（如 E636:、EP123:、#456: 等）
    title = re.sub(r'^(?:E|EP|Ep|ep|#)\d+[：:]\s*', '', title)
    lower = title.lower()
    source_lower = normalize_space(source_label).lower()

    # 中文标题二次优化：修复机翻痕迹
    zh_cleanup: list[tuple[str, str]] = [
        (r"获取关税退款你需要做什么", "美国关税退款：卖家如何申请退还已缴关税"),
        (r"如何获取关税退款", "美国关税退款：卖家如何申请退还已缴关税"),
    ]
    for pattern, zh in zh_cleanup:
        if re.search(pattern, title):
            return zh

    if looks_chinese(title) and "公告更新" not in title and "规则更新" not in title:
        # 中文标题质量后处理
        # 1. 去掉编辑标注（如 '+ 链接'、'+ 原文'）
        title = re.sub(r'\s*[+＋]\s*(链接|原文|来源|详情|link).*$', '', title, flags=re.IGNORECASE)
        # 2. 去掉冗余后缀（如 '通知公告'、'变更通知'—保留括号内的日期信息）
        title = re.sub(r'通知公告$', '', title)
        # 3. 截断超长标题（保持语义完整）
        if len(title) > 40:
            for sep in ["，", "；", "—", "：", " - "]:
                pos = title.rfind(sep, 0, 40)
                if pos > 15:
                    title = title[:pos]
                    break
            else:
                if len(title) > 45:
                    title = title[:42] + "…"
        return title

    patterns: list[tuple[str, str]] = [
        (r"sellers say amazon charged ad fees throughout thursday.?s outage", "亚马逊故障期间仍向卖家收取广告费"),
        (r"file safe-t claims with these 7 tips", "Amazon 发布 SAFE-T 索赔提交流程与要点"),
        (r"update to seller-fulfilled refund process", "Amazon 调整卖家自发货退款处理流程"),
        (r"prepaid return labels required for high-value items", "Amazon 要求高货值商品使用预付退货标签"),
        (r"fba donations?.*donation certificates", "Amazon FBA 捐赠计划开放捐赠凭证下载"),
        (r"usps suspends mail to middle east and numerous military post offices", "USPS 暂停部分中东及军邮线路"),
        (r"speed, trust and certainty are rewriting the rules of cross-border ecommerce", "跨境电商竞争转向“时效、信任与确定性”"),
        (r"fmc monitoring war.?s effect on ocean shipping rates", "美国海事监管机构监测战争对海运运价的影响"),
        (r"one vessel in u\.s\. service attacked in persian gulf", "波斯湾袭击波及挂靠美国服务的集装箱船"),
        (r"iran war leads largest shipping line to terminate mideast gulf voyages, levy \$?800 charge", "中东冲突导致航司停止部分海湾航线并加收 800 美元费用"),
        (r"us navy won.?t escort strait shipping", "美军暂不护航海峡商船，航运风险上升"),
        (r"norfolk southern to upgrade dozens of locomotives", "Norfolk Southern 升级机车运力"),
        (r"kelly: u\.s\. maritime .*critical.*", "美国海事安全法案再次被强调"),
        (r"eu.*150.*eur.*threshold.*removed", "欧盟取消 150 欧元跨境包裹免税门槛"),
        (r"eu.*150.*eur.*customs duty exemption", "欧盟取消 150 欧元跨境包裹免税门槛"),
        (r"eu.*parcel.*duty.*removed", "欧盟拟全面取消小额包裹免税制度"),
        (r"red sea.*threat", "红海航运威胁持续，头程时效普遍延误 10-14 天"),
        (r"panama canal.*restriction", "巴拿马运河吃水限制，美东航线附加费上涨预期"),
        (r"eu packaging compliance timeline", "欧盟包装合规时间线继续推进"),
        (r"clear excess inventory.*big spring sale", "Amazon Big Spring Sale 清库存窗口期即将开启"),
        (r"spring sale", "Amazon 春季促销活动更新"),
        (r"supplyhouse.*fulfillment|supplyhouse.*distribution|supplyhouse.*expand", "SupplyHouse 扩建仓储中心，物流版图扩张"),
        (r"samsara.*motive|motive.*samsara|marketing claims.*arbitration", "物流科技公司广告合规纠纷"),
        (r"international service alert", "USPS 国际线路服务告警"),
        (r"international return.*surge|return.*e-?commerce.*merchant", "国际退货潮涌动，电商卖家面临成本攀升"),
        (r"liner.*charge.*gulf.*container|free.*gulf.*container.*storage", "海湾航线集装箱附加费上涨"),
        (r"marad.*maritime|u\.?s\.?.*must.*build.*maritime", "美国海事安全与航运战略重构"),
        (r"ai.*(?:ad|advertising|arbitration|lawsuit|patent)", "AI 相关广告/专利纠纷动态"),
        (r"locomotive|railroad|rail.*upgrade", "北美铁路运力与物流基础设施更新"),
        (r"tariff.*refund|refund.*tariff|get.*tariff.*back", "美国关税退款：卖家如何申请退还已缴关税"),
        (r"importer.of.record|ior.*rule|customs.*importer", "美国海关收紧进口商资质规则"),
        (r"fedex.*close.*package|fedex.*shut.*center", "FedEx 关闭部分包裹处理中心"),
    ]
    for pattern, zh in patterns:
        if re.search(pattern, lower):
            return zh

    if "amazon" in lower and "outage" in lower and "fee" in lower:
        return "平台故障期间仍继续计费，卖家成本异常上升"
    if ("safe-t" in lower or "seller assurance" in lower) and ("claim" in lower or "reimbursement" in lower):
        return "Amazon 发布 SAFE-T 索赔与赔付规则更新"
    if "refund" in lower and ("seller-fulfilled" in lower or "fbm" in lower):
        return "Amazon 调整卖家自发货退款处理规则"
    if "return label" in lower or ("prepaid return" in lower):
        return "Amazon 更新退货标签与退件处理要求"
    if "donation certificate" in lower or ("fba donation" in lower):
        return "Amazon 更新 FBA 捐赠凭证与申报支持"
    if "shipping" in lower and ("attack" in lower or "war" in lower or "escort" in lower):
        return "地缘冲突扰动国际航运与承运稳定性"
    if "inventory" in lower and ("sale" in lower or "clearance" in lower or "excess" in lower):
        return "平台库存清仓与促销节奏变化"
    if "cross-border ecommerce" in lower:
        return "跨境电商竞争逻辑正在发生变化"
    if "parcel" in lower and ("fee" in lower or "duty" in lower or "tax" in lower):
        return "低货值包裹税费与附加费风险上升"
    # 正则未命中 → 尝试 LLM 翻译
    llm_result = llm_client.translate_to_chinese(title, context="跨境电商新闻标题", max_tokens=1024)
    # 防护：过滤 LLM 拒绝响应或无意义输出
    _LLM_REFUSAL_MARKERS = ["该链接", "请提供", "无法翻译", "我无法", "未提供", "您未提供", "抱歉"]
    if llm_result and looks_chinese(llm_result):
        if not any(marker in llm_result for marker in _LLM_REFUSAL_MARKERS) and len(llm_result) < 80:
            logger.debug("LLM 翻译标题成功：%s → %s", title[:50], llm_result[:50])
            return llm_result
        else:
            logger.warning("LLM 翻译结果异常或过长，丢弃：%s", llm_result[:60])
    # 兜底：返回原标题（交给 publish_guard 统一处理）
    return title


def localize_summary(raw_title: str, raw_content: str, source_label: str = "", topic: str = "") -> str:
    content = normalize_space(raw_content)
    title = normalize_space(raw_title)
    joined = f"{title} {content}".lower()
    if looks_chinese(content):
        return content[:140]

    rules: list[tuple[str, str]] = [
        (r"amazon charged ad fees.*outage", "亚马逊站点故障期间仍在计收广告费用，卖家不仅会遇到转化受损，还可能承受异常广告支出。"),
        (r"usps suspends mail", "USPS 暂停部分线路后，相关国家和军邮地址的可达性、时效和退件风险都会上升。"),
        (r"cross-border ecommerce", "跨境电商竞争正从低价导向转向履约确定性、时效体验和平台信任，这会直接影响卖家转化与复购。"),
        (r"shipping rates", "战争和航运风险正在推高运价与附加费预期，跨境卖家需要重新评估头程成本和发货承诺。"),
        (r"persian gulf", "波斯湾航运风险正在上升，相关海运链路的附加费、时效和舱位稳定性都可能受到影响。"),
        (r"levy \$?800 charge", "航司加收费用并调整中东航线后，相关海湾区域的头程成本和交付时效都会承压。"),
        (r"parcel fee|low-value parcel|de minimis", "低货值包裹税费变化会直接影响直邮卖家的到手价、毛利和清关成本。"),
        (r"packaging compliance", "包装合规时间线推进后，卖家需要重新检查材料、标签和相关合规成本。"),
    ]
    for pattern, zh in rules:
        if re.search(pattern, joined):
            return zh

    # 规则未命中 → 尝试 LLM 生成中文摘要
    combined = f"{title}。{content}" if content else title
    if combined.strip():
        llm_result = llm_client.translate_to_chinese(
            f"请为以下跨境电商资讯生成一句话中文摘要（≤120字），面向中国跨境卖家：\n{combined[:800]}",
            context="跨境电商资讯摘要",
            max_tokens=1024,
        )
        if llm_result and looks_chinese(llm_result):
            logger.debug("LLM 摘要生成成功")
            return llm_result[:140]

    # 兜底：按主题返回模板摘要
    if topic == "logistics":
        return "这条物流动态可能影响头程时效、附加费或承运稳定性，需要结合目标市场和履约链路继续判断。"
    if topic in {"policy", "tariff", "customs"}:
        return "这条政策变化可能影响税费、清关或平台经营规则，建议继续核对正式执行范围与时间。"
    if topic in {"environment", "compliance"}:
        return "这条合规变化可能影响包装、标签或材料要求，建议评估成本和适用品类。"
    return content[:140] if content else title[:140]


def localize_event_payload(event: dict[str, Any]) -> dict[str, Any]:
    localized = dict(event)
    raw_title = normalize_space(event.get("title"))
    raw_content = normalize_space(event.get("content"))
    localized["raw_title"] = raw_title
    localized["raw_content"] = raw_content
    localized["zh_title"] = localize_title(raw_title, str(event.get("source_label") or ""))
    localized["zh_summary"] = localize_summary(
        raw_title,
        raw_content,
        str(event.get("source_label") or ""),
        str(event.get("source_topic") or ""),
    )
    return localized
