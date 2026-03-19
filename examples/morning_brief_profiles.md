# Morning Brief Profile Presets

`morning_brief.py` 现在支持更顺手的 seller profile preset 输入，适合直接做晨报 demo。

## 可直接用的 preset

- `amazon-fba`
- `overseas-warehouse`
- `tiktok-direct-mail`
- `independent-site-direct-mail`

## 可用别名示例

- `"amazon fba"`
- `"overseas warehouse"`
- `"tiktok direct-mail"`
- `"independent-site direct-mail"`

## 最顺手的手动入口

现在更推荐直接用 `today_radar.py`，因为它把“手动试一下今日雷达”这件事收成了一个更薄的入口：

```bash
python3 scripts/today_radar.py
python3 scripts/today_radar.py tiktok
python3 scripts/today_radar.py --preset independent-site --market FR
python3 scripts/today_radar.py tiktok --refresh
python3 scripts/today_radar.py tiktok --seed-only --json
```

- 不加参数：默认先开“通用雷达首页（事件驱动 / 不绑定默认画像）”，不再偷偷落到 Amazon FBA
- `tiktok` / `amazon` / `independent-site`：只是输入快捷别名，不必记完整 preset；真正输出会统一改写成履约优先、平台修正
- `--refresh`：先抓一轮 real events，再生成今日雷达
- `--seed-only`：强制走 demo seed，适合 smoke test 或离线试跑
- 默认输出人类可读晨报；只有加 `--json` 才吐 JSON

## 定时 / 非交互入口（给未来 cron 用）

如果目标不是“手动看一眼”，而是未来让定时任务直接调，优先用这个薄封装：

```bash
python3 scripts/run_radar.py --mode morning --source auto --format human amazon
python3 scripts/run_radar.py --mode evening --source seed --format json tiktok
python3 scripts/run_radar.py --mode morning --source refresh --preset independent-site --market FR --output tmp/radar/morning.txt
```

它做的不是新逻辑，而是把调度侧需要的几个开关收顺：

- `--mode morning|evening`：显式区分早/晚投递场景
- `--source auto|refresh|seed`：适合正式跑、先抓后跑、或 smoke test
- `--format human|json`：适合直接读或接后续推送器
- `--output`：适合 cron/launchd/workflow 把结果落盘后继续处理

## 底层 brief 入口（保留）

```bash
python3 scripts/morning_brief.py "amazon-fba" --human
python3 scripts/morning_brief.py "tiktok direct-mail" --human
python3 scripts/morning_brief.py '{"profile":"independent-site-direct-mail","market":"FR"}' --human
```

## 输出意图

晨报默认会输出：

- 履约主视角（第一层）
- 平台修正 / 市场修正（第二层）
- 一句话判断
- 今早最该盯
- 每条事件的适用性分层：高相关 / 中相关 / 低相关/观察
- 分履约动作：跨境直发 / 本地履约-平台主导 / 本地履约-3PL/商家主导
- 你今天先做
- 本周继续看
- 现在别急着做

重点不是技术日志，而是更像运营负责人早上 30 秒能扫完的风险晨报：先把事件放进总雷达，再把谁最该动、谁先观察讲清楚。
