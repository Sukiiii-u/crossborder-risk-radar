# RSSHub / RSS 候选监控源（Cross-border Risk Radar）

> 目标：把可订阅的信息统一成 RSS 流，作为雷达采集层输入。

## 已有可直接接入项目分析层的源
这些已经在 `scripts/source_configs.json` 里：
- EcommerceBytes
- Digital Commerce 360
- FreightWaves
- CBP Newsroom
- EU Taxation & Customs Union News
- Amazon Seller Forums - News and Announcements

## RSSHub 候选扩展方向

### 平台政策 / 卖家规则
- Amazon Seller News / Announcements
- TikTok Shop Newsroom / Policy Center
- Temu seller rules / updates
- SHEIN seller policy / compliance notices
- AliExpress seller announcements

### 行业媒体
- 雨果跨境（cifnews）
- 亿恩网（ennews）
- Marketplace Pulse
- The Loadstar
- Journal of Commerce

### 官方 / 半官方
- CBP Newsroom
- EU Taxation & Customs
- 中国电子口岸 / 海关相关公告

## 接入优先级

### 第一优先级
- 平台政策
- 海关 / 关税 / 税务
- 物流 / 航运

### 第二优先级
- 行业媒体
- 合规 / 产品准入

### 第三优先级
- 泛电商资讯
- 资本 / 财报 / 行业八卦

## 过滤原则
只保留会改变卖家经营动作的内容：
- 是否影响价格 / 毛利 / 到手价
- 是否影响物流时效 / 清关 / 履约
- 是否影响店铺安全 / Listing / 违规
- 是否影响产品能否继续卖

不建议直接进雷达的：
- 融资新闻
- 宏观八卦
- 泛 AI 工具新闻
- 无明确卖家动作含义的媒体热闹
