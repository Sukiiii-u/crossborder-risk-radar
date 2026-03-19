# Crossborder Risk Radar Prompt Templates v1

> 用途：为 skill 的核心 AI 分析流程提供统一 prompt 模板。先保证输出稳定、结构化，再谈花活。

---

## Prompt A — Relevance Classification

### Goal
判断一条新闻、政策、论坛信息或事件摘要，是否与中国跨境卖家相关，并提取基础标签。

### Template
你是一个面向中国跨境卖家的风险识别助手。

请阅读下面的内容，判断它是否与中国跨境卖家的经营决策相关。

请输出以下内容：
1. `is_relevant`：true / false
2. `relevance_reason`：一句话说明为什么相关或不相关
3. `event_type`：从以下枚举中选一个最合适的
   - tariff
   - policy
   - compliance
   - environment
   - logistics
   - holiday
   - market-shock
4. `region`：US / EU / UK / Global / Other
5. `affected_sellers`：可能受到影响的卖家类型
6. `confidence`：low / medium / high

判断标准：
- 如果内容会影响卖家的成本、定价、库存、履约、合规或需求，则倾向于相关。
- 如果只是泛国际新闻、观点评论或无明确经营影响的噪音，则判为不相关。
- 不要因为内容“很大”就默认相关，必须和卖家经营动作有连接。

内容如下：
{{content}}

### Output style
优先输出 JSON 或结构化 bullet，不写长篇解释。

---

## Prompt B — Impact Analysis

### Goal
对已判定相关的事件做结构化影响分析。

### Template
你是一个面向中国跨境卖家的风险分析助手。

请基于下面事件内容，分析它会如何影响跨境卖家。

请输出以下字段：
1. `event_summary`：一句话概括事件
2. `affected_sellers`：哪些卖家最受影响
3. `affected_categories`：哪些品类/场景最受影响
4. `impact_dimensions`：从以下枚举中选 1~4 个
   - supply_chain
   - cost
   - pricing
   - inventory
   - demand
   - compliance
   - advertising
5. `risk_level`：low / medium / high
6. `impact_reasoning`：简要说明影响逻辑
7. `confidence`：low / medium / high

要求：
- 聚焦经营层面的影响，不做泛泛而谈。
- 如果影响不明确，要明确写出不确定性来源。
- 不要把所有维度都勾上，只选真正相关的。

事件内容如下：
{{content}}

补充上下文（如果有）：
- region: {{region}}
- seller_profile: {{seller_profile}}
- category: {{category}}

### Output style
结构化输出，优先 JSON；说明部分保持简洁。

---

## Prompt C — Action Suggestions

### Goal
把影响分析转成卖家可以执行的动作建议。

### Template
你是一个面向中国跨境卖家的经营建议助手。

请根据下面的事件分析结果，给出可执行的下一步建议。

输出要求：
1. `suggested_actions`：给出 3~5 条建议动作
2. 每条建议都要是卖家能执行的动作，不要空话
3. 优先使用动词开头，例如：检查、评估、调整、延后、替换、复核、监控
4. 如果当前最合理的动作是“先观察”，也要明确观察什么、观察多久
5. 避免只说“建议关注”或“持续观察”这种废话

可参考的动作类型：
- 定价调整
- 库存策略调整
- 供应链备选方案
- 合规/包装/资质检查
- 广告/投放节奏调整
- SKU 优先级调整
- 市场切换或观望

事件分析如下：
{{analysis}}

### Output style
输出 3~5 条清晰动作，每条不超过两行。

---

## Combined Use Pattern

### scan
A → B → C（对筛出的高相关事件逐条执行）

### analyze
A → B → C（聚焦单条内容）

### brief
A → B（批量）→ C（汇总动作）→ 生成简报

---

## One-line principle

先判断是否相关，再判断影响有多大，最后给具体动作。
