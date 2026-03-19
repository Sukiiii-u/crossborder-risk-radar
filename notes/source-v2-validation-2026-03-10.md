# Source v2 验证记录 · 2026-03-10

目标：对 source v2 补源后的真实抓取链路做一次“真抓取 + 噪音评估”验证，不改产品输出结构，只看能不能抓到、会不会明显加噪、有没有兼容问题。

## 执行范围

已运行：

- `python3 tests/validate_source_configs.py`
- `python3 tests/validate_fetch_real_events.py`
- `python3 tests/validate_run_radar.py`
- `python3 tests/validate_today_radar_entry.py`
- `python3 scripts/fetch_real_events.py`
- `python3 scripts/today_radar.py tiktok --refresh --json`
- `python3 scripts/run_radar.py amazon --mode evening --source auto --format json`

结果：**全部通过 / 可运行**。

## 本轮最小修补

只做了 source filter 的最小降噪，不改产品结构：

- `scripts/source_configs.json`
  - 给 `ecommercebytes` 增加 `outage`
  - 给 `ecommercebytes` 增加 `webinar` / `youtube` / `streaming`

原因：真实抓取里先后出现两个明显不该进入“跨境风险雷达”的噪音：

1. `Sellers Say Amazon Charged Ad Fees throughout Thursday’s Outage`
2. `eBay Ad Strategies Webinar Now Streaming on YouTube`

这两条都说明源是通的，但关键词命中太宽，容易把平台杂讯/宣传内容带进来。

## 真实抓取结果（修补后）

- `event_count = 8`
- kept 分布：
  - EcommerceBytes：2
  - Digital Commerce 360：2
  - FreightWaves：2
  - CBP Newsroom：2
- dropped 汇总：
  - `noise = 13`
  - `stale = 10`
  - `low_relevance = 2`
- failures：无
- 兼容性：无抓取报错、无 schema 崩溃、today/run smoke 均正常

## 各新增源表现

### 1) EcommerceBytes

抓取到：

- `USPS Suspends Mail to Middle East and Numerous Military Post Offices`
- `Etsy Displays Price Plus Shipping in UK Search Results`

判断：**能抓到，且有卖家运营相关性；但最容易带噪音。**

观察：

- 优点：能抓到平台/邮政侧、和卖家履约/转化相关的变化。
- 风险：同源里杂讯很多，容易混入 outage、webinar、YouTube 这类内容。
- 处理：补了最小 exclude 后，明显好一些。

结论：**建议保留，但要继续严控过滤词。**

### 2) Digital Commerce 360

抓取到：

- `How $100 oil forces B2B sellers to rethink delivery`
- `How Costco is addressing tariff changes in early 2026`

判断：**能抓到，但信号偏“泛行业/B2B/大公司视角”，不是最纯的中国跨境卖家操作信号。**

观察：

- 优点：确实能提供 tariff / delivery / macro-cost 方向的变化。
- 风险：容易把“大公司财报口径”抬成 top signal，例如 Costco 这条虽然相关，但 seller-operational 纯度一般。
- smoke 结果：两轮输出里它都占据 top1 / top3，说明这路源对排序影响较大。

结论：**建议保留，但属于“有用但偏宏观”的源，后续最好继续压宏观企业新闻权重。**

### 3) FreightWaves

抓取到：

- `Iran war leads largest shipping line to terminate Mideast Gulf voyages, levy $800 charge`
- `Kelly: U.S. maritime ‘critical’ to national, economic security`

判断：**能抓到，物流风险信号最真；但也会混入部分偏行业政治叙事。**

观察：

- 优点：`Iran war... levy $800 charge` 这类运价/航线冲击非常适合雷达场景。
- 风险：`Kelly: U.S. maritime 'critical'...` 这种更像行业政策表态，运营动作含义偏弱。
- dropped 中 `stale` 和 `noise` 都比较高，说明源量足，但筛选压力大。

结论：**建议保留。它是目前最有价值的物流源之一。**

### 4) CBP Newsroom

抓取到：

- `Trade Information Notice: New Carnet Data Elements`
- `Trade Information Notice: Automated Transmission of Container Seal Changes to ACE Manifest`

判断：**能抓到，官方源稳定；但当前抓到的条目偏美国贸易系统细则，离普通跨境卖家较远。**

观察：

- 优点：官方、可信、格式稳定、兼容性好。
- 风险：内容容易偏报关系统/ACE 细节，可能更适合大卖/报关/货代，而不是泛卖家晨报。
- 当前未造成 top3 污染，说明排序层暂时把它压住了。

结论：**建议保留，但它更像“低频高置信度补充源”，不是主力内容源。**

## Smoke 观察

### today_radar.py

Top 3：

1. `How Costco is addressing tariff changes in early 2026`
2. `Iran war leads largest shipping line to terminate Mideast Gulf voyages, levy $800 charge`
3. `How $100 oil forces B2B sellers to rethink delivery`

### run_radar.py

Top 3 与 today_radar 一致。

判断：

- 链路是通的，真实源已进入产品输出。
- 没有抓取兼容问题、格式异常或运行错误。
- 噪音问题主要不在“抓不到”，而在“抓到了以后有些源偏宏观/偏行业，不够 seller-specific”。

## 最终判断

### 新增源表现如何？

**整体是有效补源，不是空补。四个源都真实抓到了内容，链路通。**

### 噪音是否更高？

**有变高，但属于可控变高。**

- 最明显的噪音来自 `EcommerceBytes`
- 次明显的是 `Digital Commerce 360` / `FreightWaves` 的宏观行业稿
- `CBP` 噪音不高，但相关性更窄

### 是否建议保留全部新增源？

**建议保留全部新增源，但要接受一个现实：现在是“信息覆盖更全了，同时筛选负担也更大了”。**

如果只看这轮验证：

- **保留** `FreightWaves`
- **保留** `CBP Newsroom`
- **保留** `Digital Commerce 360`
- **保留但重点盯过滤** `EcommerceBytes`

一句话：**补源是值的，没炸；但 source v2 现在更像“抓得到”，还不是“已经非常干净”。**
