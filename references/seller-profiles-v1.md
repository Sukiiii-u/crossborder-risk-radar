# Seller Profiles v1

## 目标
让同一事件对不同卖家画像产生不同判断，而不是所有人拿到同一种泛建议。

## 最小画像维度

### 1. 履约主轴（第一层）
- `direct-mail`：跨境直发 / 小包直发
- `fba`：本地履约-平台主导（Amazon FBA）
- `platform-fulfillment`：本地履约-平台主导（平台托管 / 半托管）
- `overseas-warehouse`：本地履约-3PL/商家主导（海外仓）

### 2. 平台修正项（第二层）
- `amazon`
- `tiktok-shop`
- `independent-site`
- `temu`
- `other`

### 3. 市场修正项
- `US`
- `EU`
- `UK`
- `Other`

### 4. 客单价带
- `low`
- `medium`
- `high`

### 5. 风险画像
- `general`
- `margin-sensitive`：低毛利、价格敏感
- `compliance-sensitive`：强合规品类

## 使用原则
- 同一事件至少应先看：履约主轴 + 市场；平台只作为第二层修正项
- 没有画像时允许输出通用建议，但必须降低精度和置信度
- 有画像时，动作建议应优先命中最脆弱链路

## 示例
### 欧洲小包税 / 小包免税取消
更高优先级受影响画像：
- `direct-mail + EU + low + margin-sensitive`（平台修正：TikTok Shop）
- `direct-mail + EU + low + margin-sensitive`（平台修正：独立站）

相对次一级：
- `fba + EU`（平台修正：Amazon）
- `overseas-warehouse + EU`
