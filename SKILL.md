---
name: crossborder-risk-radar
description: "Scan and analyze global news, policy, tariff, compliance, logistics, and holiday-related risk signals for Chinese cross-border ecommerce sellers, then turn them into seller-facing impact assessments and action suggestions. Use when a user wants to: (1) scan recent risks in the US/EU/global markets, (2) analyze a specific news item or policy for seller impact, (3) generate a weekly or periodic risk brief for sellers across direct-mail, local-fulfillment, and mixed operating paths, with platform only as a modifier, or (4) assess how external changes affect pricing, inventory, compliance, supply chain, or demand."
---

# Crossborder Risk Radar

## Overview

Use this skill to turn external news and policy changes into seller-relevant risk judgments and suggested actions. Focus on relevance, impact, and action — not generic news summarization.

## v1 Positioning

Current v1 has two usable entry shapes:
- **Analyze-first** for single-event analysis
- **Morning brief demo** for a lightweight `今日雷达` style output

That means:
- Prioritize single-event analysis when the user gives a specific event.
- Use the morning brief flow when the user asks for `今日雷达` / daily radar / morning brief.
- Treat fully automated scanning as a later-stage enhancement, not the current promise.

When the user provides a news excerpt, policy summary, or event description, prefer running the analyze flow.
When the user asks for a daily radar brief, use `scripts/morning_brief.py` as the current demo entry.

## Core Capabilities

### 1. Impact Analyze (primary v1 capability)

Use for requests like:
- “分析这条新闻对跨境卖家的影响”
- “这个欧盟环保政策会影响哪些品类？”
- “这次关税变化对 TikTok 卖家意味着什么？”

Default workflow:
1. Read the article text, summary, or event description.
2. Normalize it into the analyze input object when needed.
3. Decide whether it is relevant to the priority users and markets.
4. Identify affected sellers, categories, and impact dimensions.
5. Assign a simple risk level: low / medium / high.
6. Give concrete next-step suggestions or check items, not vague “建议关注”.

For deterministic v1 behavior, use `scripts/analyze_event.py` as the structured analyzer when you need stable JSON or a local fallback.

### 2. Risk Brief / 今日雷达 (light v1 supporting capability)

Use for requests like:
- “给我一份本周跨境风险简报”
- “把这几条风险整理成适合运营负责人看的总结”
- “做一个适合团队负责人看的风险周报”
- “今日雷达”
- “今天的跨境风险雷达”

Current demo workflow:
1. Use a small set of already-selected, high-signal seed events.
2. Run them through the analyzer with a seller profile.
3. Rank the events by practical business relevance.
4. Produce a short brief with top risks, impact summary, suggested actions, and one overall takeaway.

Current preferred local entry for manually trying `今日雷达`:
```bash
python3 scripts/today_radar.py
python3 scripts/today_radar.py tiktok
python3 scripts/today_radar.py --preset independent-site --market FR
python3 scripts/today_radar.py tiktok --seed-only --json
```

For non-interactive / future scheduled delivery preparation, use the thin runner entry:
```bash
python3 scripts/run_radar.py --mode morning --source auto --format human amazon
python3 scripts/run_radar.py --mode evening --source seed --format json tiktok
python3 scripts/run_radar.py --mode morning --source auto --preset independent-site --market FR --output tmp/radar/morning.txt
```

- `--mode`: currently `morning` / `evening`; used to make scheduled jobs explicit and future push hooks easier to attach.
- `--source`: `auto` = prefer `real_events.json` and fall back to seed, `seed` = force demo seed for smoke tests.
- `--format`: `human` or `json`.
- `--output`: optional output file path, useful for cron / launchd / workflow chaining.

Low-level fallback entry is still available when you want to call the brief renderer directly:
```bash
python3 scripts/morning_brief.py --human
python3 scripts/morning_brief.py 'tiktok direct-mail' --human
python3 scripts/morning_brief.py '{"profile":"independent-site-direct-mail","market":"FR"}' --human
```

For the current morning brief profile presets, aliases, and manual trigger patterns, read `examples/morning_brief_profiles.md`.


### 3. Risk Scan (later-stage enhancement)

Use when the user explicitly asks for broad scanning, but treat it as a later-stage capability rather than the main MVP promise.

## Input Handling

Preferred analyze input object:

```json
{
  "content": "event text or article summary",
  "url": "optional source url",
  "region_hint": "US | EU | UK | Other",
  "seller_profile": {
    "platform": "optional",
    "market": "optional",
    "category": "optional"
  }
}
```

User requests do not need to be phrased in JSON. If the user gives plain text, a pasted article excerpt, or a short policy summary, convert it into this object yourself.

For field semantics and enum values, read `references/output-schema.md` and the workspace contract when needed.

## Output Rules

Always optimize for seller decision-making.

### Must include when applicable
- Event summary
- Event type
- Region
- Affected sellers
- Affected categories
- Impact dimensions
- Risk level
- Suggested actions
- Confidence or uncertainty note
- Source links

### Default response shape for v1 analyze
Prefer a **human-readable summary first**, then include structured fields when useful.

Suggested order:
1. Is it relevant?
2. What operationally changes?
3. Who is most affected?
4. What should the seller do now?
5. What is uncertain?

When a stable structured output is needed, use the analyzer script and surface the JSON result.

### Style rules
- Be concrete.
- Prefer action verbs: audit, reprice, delay, monitor, substitute, diversify, verify.
- Avoid generic “keep an eye on this” unless no stronger action is justified.
- Separate signal from noise.
- If confidence is low, say so clearly.

Read `references/output-schema.md` when you need the structured field list or enum guidance.
Read `references/analyze-usage.md` when you need the v1 analyze input pattern, local script entry, or default response behavior.
Read `references/analyze-contract-v1.md` when you need the legacy v1 contract.
Read `references/analyze-contract-v2.md` when you need the current target contract focused on business impact and action guidance.
Read `references/product-logic-v2.md` when you need the updated product logic for capture / brief / analyze / action.
Read `references/demo-suite.md` when you need the current v1 demo coverage and boundary cases.
Read `references/call-examples.md` when you need natural-language analyze examples or v1 call patterns.
Read `references/seller-profiles-v1.md` when you need the minimum seller profile framework.
Read `references/risk-taxonomy-v1.md` when you need the current risk classification structure.
Read `references/action-templates-v1.md` when you need the current action template structure.

## Scope Guardrails

### Prioritize
- Chinese cross-border sellers
- Sellers running direct-mail, local-fulfillment, or mixed operating paths
- Platform modifier examples: Amazon, independent-site, TikTok Shop, Shopee, Temu, AliExpress
- Operations leads, small-business owners, and team leads

### MVP focus
- Regions: US and EU
- Topics: tariff, policy, compliance, environment, logistics, holiday, market shock

### Do not do by default
- Do not become a generic global news summarizer.
- Do not try to cover every country or platform at once.
- Do not give financial certainty where only directional risk exists.
- Do not over-personalize recommendations unless seller profile details are explicitly provided.

Read `references/source-guidelines.md` when selecting or explaining source strategy.

## Decision Heuristics

### When something is likely high relevance
- It changes tariff, customs, trade, or import/export economics.
- It affects packaging, environment, or compliance rules.
- It changes logistics capacity, cost, or lead time.
- It changes demand timing through holidays or shocks.
- It directly affects a major seller platform or target market.

### When something is likely low relevance
- It is broad geopolitical noise with no clear seller link.
- It is old news with no new operational consequence.
- It is opinion coverage without policy, logistics, compliance, or market implications.

## Good Response Patterns

### Scan pattern
- Top risks
- Why each matters
- Who is affected
- What to do next

### Analyze pattern
- Is it relevant?
- Who is affected?
- What changes operationally?
- What should the seller do now?

### Brief pattern
- 3–5 top risks
- Summary of likely business impact
- Clear short action list
- One closing judgment

## One-line principle

Translate global uncertainty into concrete seller actions.
