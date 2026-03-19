# Fulfillment-first alignment audit — 2026-03-10

范围：`scripts/morning_brief.py`、`scripts/today_radar.py`、相关 examples / tests / references / SKILL.md。
目标：只审计“履约优先纠偏”后，仍残留的平台优先 / 命名错位问题。

## 已对齐项

- `morning_brief.py` 的核心结构已经明显切到履约优先：
  - `FULFILLMENT_PATHS` 先按 `跨境直发 / 本地履约-平台主导 / 本地履约-3PL/商家主导` 输出。
  - `normalize_fulfillment_path()`、`build_overview()`、`build_fulfillment_actions()` 已把“履约路径”作为第一层。
  - `overview.why_it_matters` 已明确写出“platform 只是修正项，不该再抢第一层”。
- human output 主体结构也基本对齐：
  - `总览判断`、`分履约动作`、`重点事件` 这条主线是履约优先，不再是按 Amazon/TikTok/独立站分章节。
- `today_radar.py` 本身只是薄入口，没有额外把平台重新提到第一层；主要沿用 `morning_brief.py` 的输出。
- 多画像输出虽然仍叫“画像视角”，但至少已经先给统一总览，再分别展开，不是完全按平台频道拼盘。

## 未对齐项

### 1) preset 命名仍是平台优先遗留

位置：`scripts/morning_brief.py`

- `amazon-fba`
- `tiktok-direct-mail`
- `independent-site-direct-mail`

问题：
- 这些 canonical preset 名称把平台/渠道写在前面，履约模型写在后面。
- 当前语义上真正的一层应是 `direct-mail / local-fulfillment-platform-led / local-fulfillment-merchant-led` 一类，再让 `platform` 作为 modifier。
- `today_radar.py` 的 shortcut 也继承了这个问题：`amazon` / `tiktok` / `independent-site` 都是平台别名入口。

### 2) profile label / human heading 仍把平台名顶在最前面

位置：`scripts/morning_brief.py`

- `PROFILE_LABELS`
  - `Amazon FBA（德国站）`
  - `Amazon 海外仓（德国站）`
  - `TikTok Shop 直邮（欧盟低客单）`
  - `独立站直邮（欧盟低客单）`
- human output：`画像标签：...`
- multi-view heading：`画像视角 1｜Amazon FBA（德国站）` 等

问题：
- 虽然正文已在讲履约路径，但用户第一眼看到的 title / label 还是平台先入脑。
- “画像视角”这个词也更像 seller profile / platform profile，而不是“履约视角 / 经营模型视角”。

### 3) tests 仍在用平台优先字符串当正确答案

重点位置：
- `tests/validate_multi_profile_views.py`
- `tests/validate_today_radar_entry.py`
- `tests/validate_run_radar.py`
- `tests/validate_morning_brief.py`
- `tests/validate_product_acceptance.py`
- `tests/validate_seller_profile_regressions.py`

具体残留：
- 直接断言 `Amazon FBA（德国站）` / `TikTok Shop 直邮（欧盟低客单）` / `独立站直邮（欧盟低客单）`。
- 直接断言 `tiktok` / `amazon` / `independent-site` 这些平台 shortcut 行为。
- 多画像测试把“画像视角 1/2”与平台标签绑定，进一步固化了平台优先的人类可见输出。

结论：
- 现在 test suite 仍在给平台优先命名“上保险”。
- 只要不先改 tests，后续谁想真正改成履约优先标题，都会被回归测试拦住。

### 4) examples / SKILL / references 的使用文案仍把平台当主要入口

重点位置：
- `examples/morning_brief_profiles.md`
- `SKILL.md`
- `references/seller-profiles-v1.md`
- `references/source-list.md`
- `references/call-examples.md`
- `references/analyze-usage.md`
- `references/analyze-contract-v2.md`

具体表现：
- examples 里“可直接用的 preset”仍是平台前置名字。
- examples 里“最顺手的手动入口”仍主推 `today_radar.py tiktok / amazon / independent-site`。
- `SKILL.md` 的 description 和 Scope Guardrails 仍大量用 “Amazon sellers / TikTok Shop sellers / independent-site sellers” 组织范围。
- `seller-profiles-v1.md` 仍把“平台”放在最小画像维度第 1 位，并写“同一事件至少考虑：平台 + 履约模式 + 市场”。
- `source-list.md` 的“来源结构意图”仍强调“平台卖家媒体视角”“Amazon 官方平台公告视角”等，源设计上还是平台视角很重。

## 必须修改项

### P0 — 最危险的错位点

1. **`PROFILE_LABELS` + human headings**
   - 这是用户第一眼看到的文案。
   - 现在正文虽然说“platform 只是修正项”，但标题却先喊 `Amazon / TikTok / 独立站`，属于“嘴上履约优先，门头还是平台优先”。

2. **tests 对平台优先 label 的硬编码断言**
   - 这些断言会把 legacy naming 冻结成“正确行为”。
   - 不先解掉，后续任何真正的 fulfillment-first 命名升级都会被 CI 误伤。

3. **preset canonical name 仍平台前置**
   - 一旦这些名字继续外扩到 CLI、docs、runtime state、delivery key，就会把平台优先语义继续固化。
   - 兼容 alias 可以保留，但 canonical key 不该继续是 `amazon-fba / tiktok-direct-mail / independent-site-direct-mail`。

### P1 — 应跟进但不必今天大改

4. **`today_radar.py` 的快捷入口设计**
   - 现在主 shortcut 是 `amazon / tiktok / independent-site`。
   - 这会把用户心智继续训练成“选平台”，不是“选履约模型”。

5. **多画像标题 `画像视角`**
   - 它比平台名问题轻一点，但仍偏 seller-profile 视角，不够明确地告诉用户“这里是在比较不同履约模型”。

6. **SKILL/docs/reference 叙事顺序**
   - 文档层仍大量使用平台分组，会让后续协作者继续按平台写新增内容。

## 建议改法（非本次实施，只留 review 结论）

- canonical preset 改成履约优先命名；平台名只做 alias：
  - 例如 `direct-mail-eu-low-margin`、`local-platform-fulfillment-de`、`local-merchant-fulfillment-de` 这类方向。
- `profile_label` / 人类输出标题改成：
  - 先写履约模型，再写平台修正项。
  - 例如：`跨境直发｜TikTok Shop 修正（欧盟低客单）`，而不是 `TikTok Shop 直邮（欧盟低客单）`。
- 多画像标题从 `画像视角` 改成 `履约视角` 或 `经营模型视角`。
- tests 改为断言：
  - 履约路径关键词必须出现；
  - platform 只能作为修正项出现；
  - 不再硬编码 Amazon/TikTok/独立站作为一层标题。
- docs/reference 重新排序：
  - 先写 fulfillment model，再写 platform / market / category modifiers。

## 这次我实际补的最小标记

- 已在 `scripts/morning_brief.py` 给 `PROFILE_PRESETS` 和 `PROFILE_LABELS` 补了最小 TODO，标明它们仍是 legacy 的平台优先命名债。

## 一句话判断

现在这套实现**骨架已经偏向履约优先**，但**入口命名、标题命名、测试断言、文档心智**还在替平台优先站岗；最危险的不是逻辑层，而是**人类第一眼可见的 label + 被 tests 固化的 legacy naming**。
