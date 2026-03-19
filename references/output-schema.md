# Crossborder Risk Radar 输出结构

所有命令尽量收敛到以下字段，便于后续做简报、看板和结构化输出。

## 通用字段
- `event_title`
- `event_summary`
- `event_type`
- `region`
- `affected_sellers`
- `affected_categories`
- `impact_dimensions`
- `risk_level`
- `suggested_actions`
- `confidence`
- `sources`
- `published_at`

## event_type 枚举
- `tariff`
- `policy`
- `compliance`
- `environment`
- `logistics`
- `holiday`
- `market-shock`

## impact_dimensions 枚举
- `supply_chain`
- `cost`
- `pricing`
- `inventory`
- `demand`
- `compliance`
- `advertising`

## risk_level
- `low`
- `medium`
- `high`

## scan 输出建议
每条事件至少包含：
- 标题
- 时间
- 风险类型
- 风险等级
- 影响对象
- 一句话影响
- 一句话建议
- 来源

## analyze 输出建议
- 事件摘要
- 是否与跨境卖家相关
- 影响对象
- 影响维度
- 风险等级
- 建议动作
- 置信度
- 来源

## brief 输出建议
- Top 风险事件
- 每条事件的风险摘要
- 潜在影响
- 建议动作
- 本期结论
