# 监控源配置（方案 A）

本目录是 `Cross-border Risk Radar` 的监控源骨架。

## 设计思路
- **changedetection.io**：盯固定页面变化（更像雷达）
- **RSSHub / RSS**：把可订阅内容统一成信息流
- **雷达分析层**：从这些源里筛出真正会影响卖家经营动作的信号

## 文件
- `changedetection-watchlist.md`：changedetection.io 第一批监控页面清单
- `rsshub-candidates.md`：RSS / RSSHub 候选扩展源
- `changedetection_feed.xml`：项目固定读取的 changedetection RSS 快照文件
- `../configs/changedetection_source.json`：项目默认的 changedetection 上游来源

## 当前项目内已有分析层源
见：
- `scripts/source_configs.json`

## 固定接入方式

项目现在把 changedetection 的输入约定死成一条固定链路：

1. 先把 feed 同步到：
   - `monitoring/changedetection_feed.xml`
2. 然后 Python 主链路会自动把它当成官方监控源输入

标准同步命令：

```bash
python3 scripts/sync_changedetection_feed.py --from-file /path/to/feed.xml
```

如果你手里拿到的是 RSS URL，也可以：

```bash
python3 scripts/sync_changedetection_feed.py --from-url https://...
```

如果你已经把默认来源写进 `configs/changedetection_source.json`，也可以直接无参数执行：

```bash
python3 scripts/sync_changedetection_feed.py
```

同步完成后，正常跑抓取即可：

```bash
python3 scripts/ingest_sources.py
```

如果你想一条命令走完整链路，现在可以直接用：

```bash
python3 scripts/refresh_radar_pipeline.py --changedetection-file /path/to/feed.xml --profile tiktok --json
```

它会顺序执行：
- 独立采集：同步 changedetection feed + 抓取真实事件
- 生成最新 `today_radar` 运行结果
- 刷新 `ui/radar-data.js`

## 自动化骨架

项目内已经提供了 `launchd` 模板生成器：

```bash
python3 scripts/generate_launchd_templates.py
```

它会生成：
- `automation/launchd/ai.crossborder-risk-radar.ingest.plist`
- `automation/launchd/ai.crossborder-risk-radar.render.plist`

默认约定：
- `ingest` 任务只负责采集外部源
- `render` 任务只负责读取本地快照并刷新 UI

## 现状说明
- 这套项目已经不再依赖旧 Node backend
- changedetection 源现在走 Python 主链路
- `rss_or_html` 官方源可直接抓
- `changedetection` 官方源只要 feed 文件同步到固定位置，就会自动纳入抓取
