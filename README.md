# 跨境风险雷达 (Crossborder Risk Radar)

> 面向跨境电商卖家的实时风险监测与智能预警系统

## 它能做什么？

每天自动从 **45 个数据源**（RSS 订阅 + 官方平台页面）抓取全球跨境电商领域的政策变化、关税调整、物流异动、合规新规和平台动态，通过 AI 分析生成中文风险研判，帮助卖家**提前预判经营风险**。

### 覆盖平台
Amazon · TikTok Shop · Temu · SHEIN · AliExpress · Shopee · eBay · Walmart · Lazada · Mercado Libre · Shopify(独立站)

### 监测维度
- 🔴 **政策风险** — 平台规则变更、封号政策、上架要求
- 🟠 **物流异动** — 航运延误、承运商费用、线路中断
- 🟣 **合规准入** — 认证要求、包装法规、知识产权
- 🟡 **税务关税** — 关税加征、de minimis 调整、VAT 变化
- 🔵 **平台动态** — 佣金调整、算法变化、新市场开放

---

## 快速开始

### 环境要求
- Python 3.11+（使用标准库，**无需安装任何第三方包**）
- Node.js（仅用于本地前端预览）

### 1. 克隆项目
```bash
git clone https://github.com/你的用户名/crossborder-risk-radar.git
cd crossborder-risk-radar
```

### 2. 配置（可选）

#### LLM 配置（可选，用于 AI 翻译和深度分析）
```bash
cp configs/llm_config.example.json configs/llm_config.json
# 编辑 llm_config.json，填入你的 API Key
```

> 不配置 LLM 时，系统会使用规则引擎 fallback，核心功能不受影响。

#### 网络代理配置（可选，墙内用户可能需要）
```bash
cp configs/fetch_network.example.json configs/fetch_network.json
# 编辑 fetch_network.json，填入你的代理地址
```

### 3. 抓取数据
```bash
# 一键抓取+分析+同步到前端
bash automation/daily_refresh.sh
```

### 4. 启动前端
```bash
cd ui
npx serve .
# 浏览器打开 http://localhost:3000
```

---

## 自动化抓取

### macOS (launchd)
```bash
# 安装定时任务（每天 8:00 和 18:00 自动执行）
cp automation/launchd/ai.crossborder-risk-radar.daily-refresh.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/ai.crossborder-risk-radar.daily-refresh.plist
```

### Linux (cron)
```bash
# 编辑 crontab
crontab -e

# 添加以下行（每天 8:00 和 18:00 执行）
0 8,18 * * * /bin/bash /path/to/crossborder-risk-radar/automation/daily_refresh.sh
```

---

## 项目架构

```
crossborder-risk-radar/
├── scripts/                    # 后台核心逻辑
│   ├── source_configs.json     # 22 个 RSS 数据源配置
│   ├── source_registry.py      # 数据源合并与注册
│   ├── fetch_real_events.py    # 数据抓取（RSS/HTML/页面快照）
│   ├── analyze_event.py        # AI 事件分类与风险评级
│   ├── event_scorer.py         # 评分排序引擎
│   ├── published_snapshot.py   # 数据规范化与中文化
│   ├── llm_client.py           # LLM 调用封装（支持 fallback）
│   ├── zh_localization.py      # 中英翻译（LLM + 规则兜底）
│   ├── publish_guard.py        # 发布前质量检查
│   ├── morning_brief.py        # 每日简报生成
│   └── run_radar.py            # CLI 入口
├── monitoring/
│   └── platform_official_watchlist.json  # 17 个官方平台监控源
├── configs/                    # 配置文件（敏感文件已 gitignore）
│   ├── llm_config.example.json
│   ├── fetch_network.example.json
│   ├── relevance_signals.json  # 相关性信号配置
│   └── policy_watch_sources.json
├── ui/                         # 前端界面
│   ├── index.html
│   ├── styles.css
│   ├── app.js
│   └── refresh_radar_data.py   # 数据同步到前端
├── automation/                 # 自动化脚本
│   ├── daily_refresh.sh        # 一键抓取脚本
│   └── launchd/                # macOS 定时任务模板
└── runtime/                    # 运行时数据（已 gitignore）
    ├── data/                   # 抓取结果和状态
    └── logs/                   # 运行日志
```

### 数据处理管线

```
数据源 (45个)
  ↓  fetch_real_events.py
  ├─ RSS 解析 / HTML 页面抓取 / 变更检测
  ├─ 7层过滤（空内容→太短→无URL→过期→噪音→不相关→重复）
  ├─ 域名级速率限制 + 指数退避重试
  ↓
AI 分析
  ↓  analyze_event.py + event_scorer.py
  ├─ 事件类型分类（关税/物流/合规/政策/平台）
  ├─ 风险等级评估（low/medium/high）
  ├─ 多维评分排序（来源权重+时效衰减+内容信号）
  ↓
中文化 + 发布
  ↓  published_snapshot.py + zh_localization.py
  ├─ LLM 翻译 + 规则兜底 + 模板 fallback
  ├─ 平台精确推断（9个平台关键词映射）
  ├─ 原子写入（temp → replace）
  ↓
前端展示
  ↓  radar-data.js → app.js
  ├─ 五维雷达图
  ├─ 分类新闻卡片 + 摘要
  └─ 响应式布局（PC + 移动端）
```

---

## 数据源清单

### RSS 订阅（22个）

| 数据源 | 覆盖 | 语言 |
|--------|------|------|
| EcommerceBytes | 多平台 | EN |
| Digital Commerce 360 | 多平台 | EN |
| FreightWaves | 物流 | EN |
| EcomCrew | Amazon/TikTok/Temu | EN |
| PYMNTS Cross-Border | 跨境支付 | EN |
| Supply Chain Dive | 供应链 | EN |
| Jungle Scout Blog | Amazon | EN |
| SellerApp Blog | Amazon | EN |
| Modern Retail | TikTok/Temu/Amazon | EN |
| Tamebay | Amazon/eBay/TikTok | EN |
| Retail Dive | 多平台 | EN |
| TechCrunch TikTok | TikTok | EN |
| The Verge TikTok | TikTok | EN |
| Cross-Border Magazine | 跨境综合 | EN |
| Ecommerce News EU | 欧洲电商 | EN |
| Practical Ecommerce | 多平台 | EN |
| Helium 10 Blog | Amazon | EN |
| Marketplace Pulse | 多平台 | EN |
| 36氪科技 | 多平台 | ZH |
| 白鲸出海 | TikTok/Temu/SHEIN | ZH |
| Pandaily | TikTok/Temu/SHEIN | EN |
| 雨果跨境 | 全平台 | ZH |

### 官方平台监控（17个）

Amazon · TikTok Shop · Temu · Shopee · AliExpress · Walmart · Shopify · eBay · Lazada · Mercado Libre + EU Customs · US CBP · DHL · USPS · USTR · UK HMRC

---

## 技术特点

- **零依赖** — 纯 Python 标准库，不需要 pip install
- **LLM 可选** — 不配置 API Key 也能正常运行
- **多层 fallback** — LLM → 规则引擎 → 模板 → 兜底文案
- **原子写入** — 数据文件先写临时文件再替换，不会因崩溃损坏
- **速率限制** — 自动域名级限速 + 指数退避重试，不会被封
- **响应式** — PC 和移动端都能正常浏览

---

## 许可证

MIT License
