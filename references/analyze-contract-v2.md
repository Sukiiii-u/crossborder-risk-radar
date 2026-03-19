# Analyze Contract v2

## 设计目标
把单条外部变化，稳定翻译成跨境卖家的经营影响判断和动作建议，而不是只做新闻总结。

---

## 输入对象

```json
{
  "event": {
    "title": "string, optional",
    "content": "string, required",
    "source_url": "string | null, optional",
    "published_at": "string | null, optional",
    "region_hint": "US | EU | UK | Other | null, optional",
    "event_type_hint": "tariff | policy | compliance | environment | logistics | holiday | market-shock | null, optional"
  },
  "seller_profile": {
    "platform": "amazon | tiktok-shop | independent-site | temu | other | optional",
    "fulfillment_model": "direct-mail | overseas-warehouse | fba | platform-fulfillment | optional",
    "market": "string, optional",
    "price_band": "low | medium | high | optional",
    "category": "string, optional",
    "risk_profile": "general | compliance-sensitive | margin-sensitive | optional"
  }
}
```

---

## 输出对象

```json
{
  "event_summary": "string",
  "confirmed_facts": ["string"],
  "uncertainties": ["string"],
  "seller_profiles_affected": ["string"],
  "impact_assessment": {
    "profit_structure": "low | medium | high | unknown",
    "fulfillment_chain": "low | medium | high | unknown",
    "compliance_exposure": "low | medium | high | unknown",
    "traffic_and_conversion": "low | medium | high | unknown",
    "inventory_and_cashflow": "low | medium | high | unknown",
    "channel_and_market_layout": "low | medium | high | unknown"
  },
  "risk_level": "low | medium | high",
  "urgency_level": "monitor | this-week | immediate",
  "recommended_actions": {
    "do_now": ["string"],
    "do_this_week": ["string"],
    "monitor": ["string"]
  },
  "not_recommended_actions": ["string"],
  "reasoning_basis": ["string"],
  "missing_info": ["string"],
  "confidence": "low | medium | high",
  "sources": [{"name": "string", "url": "string"}]
}
```

---

## 输出原则
1. 先交付经营影响，再交付动作建议。
2. 动作建议必须尽量可执行，而不是“建议关注”。
3. 允许明确输出 `unknown` 和 `missing_info`，不要伪精确。
4. 同一事件对不同 seller profile 可有不同结论。
