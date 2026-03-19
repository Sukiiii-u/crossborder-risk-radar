# Applicability / presentation audit — 2026-03-10

范围：`crossborder-risk-radar` 的代码、tests、examples、references、SKILL 文案。
目标：检查 fulfillment-first + applicability-layered 收口后，是否还有明显漏项。

## 这次已直接修掉的极小漏项

1. `references/seller-profiles-v1.md`
   - 之前仍把“平台”放在最小画像维度第 1 位。
   - 现已改成：先写履约主轴，再写平台修正项 / 市场修正项。
   - 欧洲小包税示例也改成“履约主轴优先 + 平台修正”的写法。

2. `SKILL.md`
   - description 原本把 weekly/periodic brief 直接组织成平台名单。
   - Scope Guardrails 的 Prioritize 也主要按平台列用户。
   - 现已改成：先写 direct-mail / local-fulfillment / mixed operating paths，再把平台列成 modifier examples。

3. `scripts/morning_brief.py`
   - 代码注释里还保留了“当前 labels/presets 仍平台优先”的过时 TODO，和现状冲突。
   - 已改成兼容性说明：legacy key 继续保留，但 human-visible rendering 必须坚持 fulfillment-first。

## 这次确认基本已锁住的点

- human output 已有测试锁住：
  - `履约主视角：...`
  - `平台修正：...`
  - `## 分履约动作`
  - `### 履约路径｜跨境直发 / 本地履约-平台主导 / 本地履约-3PL/商家主导`
- `validate_morning_brief.py`
  - 已明确防回归：profile label 不能以 `Amazon / TikTok / 独立站` 开头。
- `validate_multi_profile_views.py`
  - 已锁多画像标题为 fulfillment-first 标签，而不是平台标题。
- `today_radar.py` / `run_radar.py`
  - 入口虽然允许 `amazon / tiktok / independent-site` 快捷别名，但展示层已转成 fulfillment-first。

## 仍然存在、但这次不宜顺手大改的项

1. **canonical preset key 仍是 legacy 平台命名**
   - 例如：`amazon-fba`、`tiktok-direct-mail`、`independent-site-direct-mail`
   - 这属于接口兼容层，不是这次“极小修补”该硬掰的；改它会波及 tests / CLI 调用 / runtime state。

2. **examples 里的手动入口仍主推平台别名**
   - `today_radar.py tiktok`
   - `today_radar.py --preset independent-site`
   - 这不是展示层错位，但会继续训练使用者从平台入口思考。
   - 如果下一轮要继续收口，建议补一组 fulfillment-first alias，再把 examples 顺序改成先履约、后平台快捷方式。

3. **source-list / call-examples 等 references 仍有较重的平台语义**
   - 例如 source 章节里会写“Amazon 官方平台公告视角”。
   - 这部分更多是 source strategy 文档，不直接决定用户可见主标题；本轮先不动。

## 一句话结论

这次没再发现“平台主标题压过履约路径”的明显实现级回归；当前残留主要在 **preset key / 入口心智 / 部分 source reference 叙事**，不是主渲染层。