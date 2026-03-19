# Radar real-run acceptance · 2026-03-10

目标：对主链路 `fetch_real_events -> morning_brief -> today_radar/run_radar` 做连续真实试跑，确认现在是否已经达到“能演示、像产品、不太穿帮”的状态。

## 本次真实抓取基线

- 抓取命令：`python3 scripts/fetch_real_events.py`
- 结果：`event_count = 9`
- 来源分布：EcommerceBytes 3、Digital Commerce 360 2、FreightWaves 2、CBP Newsroom 2
- 质量报告：dropped = `noise 11 / stale 7 / low_relevance 2`
- 去重观察：本轮抓取结果里未见明显重复标题；抓取阶段全局 dedupe 生效。

## Trial 1 · morning / manual / refresh

命令：`python3 scripts/today_radar.py tiktok --refresh --json`

- 画像：TikTok Shop 直邮（欧盟低客单）
- 事件数：3
- real 优先：是，top3 全部 `brief_source_mode=real`
- duplicate：否，`delivery_metadata.is_duplicate_of_last = false`
- Top 3：
  1. `How Costco is addressing tariff changes in early 2026`
  2. `Iran war leads largest shipping line to terminate Mideast Gulf voyages, levy $800 charge`
  3. `How $100 oil forces B2B sellers to rethink delivery`
- 输出是否像产品：是。有人类化标题、画像提醒、履约路径动作、今日先做/继续观察/暂缓动作。
- 明显问题：
  - 真实源能进来，但 top1 / top3 仍偏“宏观/B2B/企业新闻”，有一点噪音，不够像为中国跨境卖家精挑过。
  - 跑前发现 human 输出里的来源字段会显示成 `user-provided`，像 demo 穿帮。

## Trial 2 · evening / scheduled / auto

命令：`python3 scripts/run_radar.py amazon --mode evening --source auto --format json`

- 画像：Amazon FBA（德国站）
- 事件数：3
- real 优先：是，top3 全部 `brief_source_mode=real`
- duplicate：否，`delivery_metadata.is_duplicate_of_last = false`
- Top 3：与 Trial 1 相同，但 seller angle / takeaway 已按 FBA 画像改写
- 输出是否像产品：基本是。runner / delivery metadata / state snapshot 都能落盘，适合后续定时触发。
- 明显问题：
  - 画像差异主要体现在解释和动作文案，不在事件集合本身；同一轮真实数据下，多画像看到的 top3 一致。
  - 对 evening 模式来说现在只是 metadata 区分，产品感还主要靠文案，不是一个独立晚报视角。

## Trial 3 · multi-profile / manual

命令：`python3 scripts/today_radar.py --preset amazon --preset tiktok --preset independent-site --json`

- 画像：Amazon FBA（德国站）/ TikTok Shop 直邮（欧盟低客单）/ 独立站直邮（欧盟低客单）
- 事件数：每个 view 都是 3
- real 优先：是，3 个 view 的 top3 全部来自 real
- duplicate：本次 run 不是 duplicate；视图内也未见重复事件
- Top 3：3 个画像共用同一组真实事件，但解释、提醒、动作列表随画像变化
- 输出是否像产品：是，作为“同一外部世界，拆给不同盘子看”已经成立。
- 明显问题：
  - 多画像虽然文案分化存在，但事件排序仍高度一致；产品层已能 demo，策略层还没真拉开。
  - 若后续要更像产品，应该继续压低泛行业新闻、提高 seller-operational 事件权重；这次先不扩功能。

## 本轮最小修补

### 1) 修正 real source 在 human 输出里被渲染成 `user-provided`

问题：真实抓取进入 `morning_brief` 后，`analyze_event.py` 先默认生成 `sources=[{name: user-provided, url: ...}]`；
如果不覆盖，人类输出会显示通用占位来源，而不是 Reuters / FreightWaves / Digital Commerce 360 之类的真实媒体名。

修补：在 `scripts/morning_brief.py` 的 `build_real_event_results()` 中，真实事件只要有 URL，就强制用 `source_label` 覆盖 `sources`。

效果：human 输出里的来源现在能正确显示 `Digital Commerce 360` / `FreightWaves` 等真实名，不再穿帮。

### 2) 同步修正 acceptance 测试文案预期

- `tests/validate_product_acceptance.py`
  - 增加断言：真实 human 输出必须保留真实 source label（fixture 中检查 `来源：Reuters`）
  - 把 section 文案预期更新到当前真实输出版本：
    - `画像标签：`
    - `一句话结论：`
    - `画像提醒：`
    - `## 重点事件`
    - `## 优先级解释`
    - `## 今日先做`
    - `## 继续观察`
    - `## 暂缓动作`

## 本轮最小检查

已通过：

- `python3 tests/validate_real_event_morning_brief.py`
- `python3 tests/validate_product_acceptance.py`
- `python3 tests/validate_run_radar.py`
- `python3 tests/validate_morning_brief.py`

## 最终判断

### 现在是否基本可用？

**是，已经基本可用，适合做 demo / 晨报试跑。**

### 当前状态怎么评价

- **真实链路通了**：fetch 能抓到 9 条真实事件，brief / today_radar / run_radar 都会优先吃 real。
- **产品形态成立**：human 输出已经不是 schema dump，而是能读的“晨报/雷达”。
- **没有明显重复灾难**：抓取层和 top3 展示层都没有肉眼可见的重复刷屏。
- **仍有轻中度噪音**：现在最主要问题不是 crash，而是“选题还不够狠”，偶尔会把 Costco/B2B 这类偏泛行业内容顶上来。
- **多画像已能演示但还没彻底拉开**：动作建议会变，但事件集合还比较像“同一世界共用一份新闻篮子”。

结论：**可演示、可试跑、不会明显穿帮；但若要更像成熟产品，下一步该继续压噪音而不是加新功能。**
