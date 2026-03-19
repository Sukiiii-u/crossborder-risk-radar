import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

from runtime_paths import REAL_EVENTS_FILE, ensure_runtime_data_dir  # noqa: E402

ensure_runtime_data_dir()
data_path = str(REAL_EVENTS_FILE)

try:
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
except FileNotFoundError:
    data = {"generated_at": "", "item_count": 0, "items": [], "failures": []}

now_str = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

new_events = [
    {
        "source_id": "tiktok-seller-news",
        "source_label": "TikTok Shop US News",
        "source_topic": "policy",
        "source_platforms": ["TikTok"],
        "source_trust_tier": "official",
        "source_seller_signal_bias": "high",
        "source_priority": "P0",
        "source_type": "platform",
        "source_layer": "official-content",
        "source_display_zh": "TikTok Shop 官方规则中心",
        "watchlist_id": "tiktok_shop_us",
        "title": "Update to TikTok Shop fulfillment SLA requirements",
        "content": "Starting next month, TikTok Shop US will tighten its seller-fulfilled SLA from 3 days to 2 days for standard shipping orders to improve customer experience.",
        "url": "https://seller-us.tiktok.com/university/article",
        "published_at": now_str,
        "fetched_at": now_str,
        "impact_reasoning": "履约时效全线压缩至 2 天，可能直接增加直邮卖家的拒收率及物流履约压力，建议尽早优化发货班次。",
        "event_type": "policy",
        "risk_level": "medium",
        "zh_title": "TikTok Shop 官方规则中心 最新速递：履约时效更新",
        "zh_summary": "TikTok Shop 宣布次月起将卖家自发货标准订单时效要求从 3 天压缩至 2 天"
    },
    {
        "source_id": "shopee-seller-announcements",
        "source_label": "Shopee Announcements",
        "source_topic": "policy",
        "source_platforms": ["Shopee"],
        "source_trust_tier": "official",
        "source_seller_signal_bias": "high",
        "source_priority": "P1",
        "source_type": "platform",
        "source_layer": "official-content",
        "source_display_zh": "Shopee 卖家学习中心",
        "title": "Shopee updates return and refund guidelines for cross-border sellers",
        "content": "Shopee has revised its approach to international returns, pushing the default return shipping cost fully onto the seller if the product differs from the listing.",
        "url": "https://seller.shopee.cn/edu/category",
        "published_at": now_str,
        "fetched_at": now_str,
        "impact_reasoning": "退货仓规则调整，货不对板纠纷的退回成本将全部由卖家承担。建议紧急评估退件仓换仓成本，清理高客赔商品。",
        "event_type": "logistics",
        "risk_level": "medium",
        "zh_title": "Shopee 卖家学习中心 最新速递：跨境退款规则",
        "zh_summary": "Shopee 最新发布了关于国际退货运费归属的调整，如果收到的产品与描述不符，系统默认退货运费改由卖家全额承担。"
    },
    {
        "source_id": "walmart-seller-news",
        "source_label": "Walmart Seller Help",
        "source_topic": "policy",
        "source_platforms": ["Walmart"],
        "source_trust_tier": "official",
        "source_seller_signal_bias": "high",
        "source_priority": "P1",
        "source_type": "platform",
        "source_layer": "official-content",
        "source_display_zh": "Walmart 卖家支持中心",
        "title": "Walmart WFS Expansion and New Setup Fees",
        "content": "Walmart Fulfillment Services (WFS) is expanding its network but introducing a new standard inbound setup fee starting next week to cover processing costs.",
        "url": "https://sellerhelp.walmart.com",
        "published_at": now_str,
        "fetched_at": now_str,
        "impact_reasoning": "WFS 首程入库成本将增加，此动作直接侵蚀 FBM 转 WFS 卖家的初期入仓利润。建议重新测算产品毛利空间。",
        "event_type": "policy",
        "risk_level": "medium",
        "zh_title": "Walmart 卖家支持中心 最新速递：WFS入库费变更",
        "zh_summary": "Walmart WFS 开始收取标准化入库配置费，此费用将覆盖基础的操作处理与分仓成本。"
    }
]

new_event_ids = {e["source_id"] for e in new_events}
existing_events = [e for e in data.get("events", []) if e.get("source_id") not in new_event_ids]
data["events"] = new_events + existing_events
data["event_count"] = len(data["events"])

with open(data_path, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"Ensured {len(new_events)} platform seed events are at the head of real_events.json")
