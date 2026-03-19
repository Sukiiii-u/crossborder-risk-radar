# Analyze Contract v1

## 输入对象

```json
{
  "content": "string, required",
  "url": "string | null, optional",
  "region_hint": "US | EU | UK | Other | null, optional",
  "seller_profile": {
    "platform": "string, optional",
    "market": "string, optional",
    "category": "string, optional"
  }
}
```

## 输出对象

```json
{
  "event_title": "string",
  "event_summary": "string",
  "event_type": "tariff | environment | compliance | logistics | holiday | policy",
  "region": "US | EU | UK | Other",
  "is_relevant": true,
  "relevance_reason": "string",
  "affected_sellers": ["string"],
  "affected_categories": ["string"],
  "impact_dimensions": ["cost | pricing | inventory | compliance | supply_chain | demand"],
  "risk_level": "low | medium | high",
  "impact_reasoning": "string",
  "suggested_actions": ["string"],
  "confidence": "low | medium | high",
  "sources": [{"name": "string", "url": "string"}]
}
```

## v1 保守规则
- 不确定时宁可保守留空，不伪精确
- `affected_categories` 判不出就返回空数组
- `affected_sellers` 仅在输入给出足够 seller profile 时补充
- `suggested_actions` 最多 5 条，低置信时以观察 / 补信息为主
