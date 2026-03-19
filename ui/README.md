# Radar Dashboard UI v2

一个可直接本地打开的轻量静态首页，用来展示 `crossborder-risk-radar` 的客户可读版首页。

这版收口后的原则很简单：首页只保留三类信息：

1. **结果**：今天最该先看什么
2. **动作**：今天先做什么
3. **入口**：按风险类别 / 履约路径继续深挖

不再在首页解释产品逻辑、排序方法、当前视角或方法论。

## 页面入口

- `swarm/skills/crossborder-risk-radar/ui/index.html`

## 首页现在有哪些板块

1. **结果**
   - 只保留头号风险、谁最该注意、今天先做
   - 如有来源，可直接点源链接
2. **动作**
   - 首页只放最优先的 2~3 条动作
   - 补一组继续观察项，避免文字过密
3. **入口**
   - 按履约路径进入：跨境直发 / 本地履约-平台主导 / 本地履约-3PL/商家主导
   - 按风险类别进入：物流风险 / 关税税务 / 合规包装等

## 怎么打开

### 方式 1：直接本地打开
直接用浏览器打开 `index.html` 即可。页面数据来自同目录下的 `radar-data.js`，因此 `file://` 方式也能直接预览。

### 方式 2：本地起静态服务（更稳）
在仓库根目录执行：

```bash
python3 -m http.server 8765
```

然后访问：

```text
http://127.0.0.1:8765/swarm/skills/crossborder-risk-radar/ui/
```

## 数据来源

当前页面只消费一份 Python 生成的静态数据：

- `swarm/skills/crossborder-risk-radar/runtime/latest_run.json`
- 经过 `ui/refresh_radar_data.py` 扁平化后导出到 `ui/radar-data.js`

前端不再依赖 Node backend，也不再直接读取整份运行态 JSON。

## 刷新数据

执行：

```bash
python3 swarm/skills/crossborder-risk-radar/ui/refresh_radar_data.py
```

会自动把最新的 `runtime/latest_run.json` 转成 UI 专用 payload 并刷新到 `ui/radar-data.js`。

## 最小验证方式

1. 打开页面，确认首页只有 **结果 / 动作 / 入口** 3 类信息
2. 确认首页不再出现“为什么首页这样排 / 当前视角 / 方法论说明”之类文案
3. 确认结果区能看到头号风险、谁最该注意、今天先做
4. 确认动作区能直接扫读 2~3 个优先动作
5. 确认入口区能分别点开履约路径和风险类别继续看
6. 在手机宽度或浏览器窄窗下确认布局变成单列，摘要仍易扫读
