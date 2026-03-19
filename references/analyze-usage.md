# Analyze 使用方式 v1

## 目标
让 `crossborder-risk-radar` 在 v1 阶段先把单条事件 analyze 做稳，而不是先追求全量 scan。

## 推荐输入
优先使用一个事件对象：

```json
{
  "content": "欧盟拟收紧包装与可回收要求，部分跨境卖家可能需要调整材料与标签。",
  "url": "https://example.com/eu-packaging",
  "region_hint": "EU",
  "seller_profile": {
    "platform": "amazon",
    "market": "DE",
    "category": "home"
  }
}
```

## 输入来源
用户不需要手动写 JSON。可由以下输入自动转成对象：
- 一段新闻/政策摘要
- 一条 pasted article excerpt
- 一个事件简述
- 一个 URL（后续再补抓取链路）

## 本地脚本
- `scripts/analyze_event.py`

### 输出模式
#### 1. JSON（默认）
```bash
python3 scripts/analyze_event.py '<json>'
```

#### 2. 人类可读摘要
```bash
python3 scripts/analyze_event.py '<json>' --human
```

## v1 输出原则
1. 先回答是否相关
2. 再回答影响什么
3. 再回答该做什么
4. 信息不足时明确低置信，不伪精确
