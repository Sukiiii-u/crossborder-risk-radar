# Integrity 执行清单（方案 A）

> 目标：把 `Cross-border Risk Radar` 的监控底座接起来。先做 changedetection.io，再接 RSSHub。

## A. changedetection.io

### 1) 拉起服务
优先方案：Docker / Docker Compose
- 服务名：`changedetection`
- 建议端口：`5000`
- 数据目录：`swarm/skills/crossborder-risk-radar/monitoring/changedetection-data`

### 2) 导入监控清单
按以下文件逐条配置：
- `monitoring/changedetection-watchlist.md`

先只导入 P0 页面：
- CBP Trade / Newsroom
- EU Taxation & Customs
- EU Customs Reform
- Amazon Seller Announcements
- Amazon Seller Forums 公告流
- TikTok Shop Newsroom
- FreightWaves
- DHL Service Updates

### 3) 页面规则
- 能只盯公告列表区就不要盯整页
- 关键词过滤按 `changedetection-watchlist.md` 里的 P0 关键词
- P0 页面：有变化即告警
- P1 页面：每日汇总一次

### 4) 输出要求
- 每个监控页面有：名称、URL、监控目标、关键词、告警策略
- 变化结果能导出为 RSS 或 Webhook（任选其一先打通）

## B. RSSHub

### 1) 本机已完成的事情
- RSSHub 已本地安装
- 本地可用端口：`1210`
- 说明见：`monitoring/rsshub-local/README.md`

### 2) 先做的事
- 为项目确认第一批 RSS / RSSHub 路由
- 优先把这些源统一成可消费的信息流：
  - 平台政策
  - 海关 / 关税 / 税务
  - 物流 / 航运
  - 行业媒体

### 3) 参考文件
- `monitoring/rsshub-candidates.md`
- `scripts/source_configs.json`

## C. 接回雷达分析层
最终不是让用户直接看 changedetection / RSSHub，
而是把这些源回灌给 `Cross-border Risk Radar` 的分析层。

### 回灌原则
- 只保留“会改变卖家今天经营动作”的信号
- 过滤泛资讯 / 资本新闻 / AI 工具新闻 / 无动作含义信息

## 交付标准
1. changedetection.io 能访问
2. P0 监控页面已导入
3. RSSHub 本地能跑
4. 第一批 RSS / RSSHub 路由已确认
5. 输出能进入雷达分析层，而不是停留在阅读器阶段
