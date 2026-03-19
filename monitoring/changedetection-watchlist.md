# changedetection.io 监控清单（Cross-border Risk Radar）

> 目标：先盯 **官方规则页 / 公告页 / 合规页 / 物流公告页**。
> 原则：优先监控“会直接改变卖家今天经营动作”的页面，而不是泛资讯。

## P0｜必须先盯

### 海关 / 关税 / 税务
- CBP Newsroom - Trade / Media Releases
  - URL: https://www.cbp.gov/newsroom/media-releases/trade
  - 监控点：trade information notice / tariff / de minimis / duties / import / customs
- EU Taxation & Customs Union
  - URL: https://taxation-customs.ec.europa.eu/index_en
  - 监控点：e-commerce / parcel / customs reform / VAT / ICS2 / tariff
- EU Customs Reform
  - URL: https://taxation-customs.ec.europa.eu/customs/eu-customs-reform_en
  - 监控点：customs reform / e-commerce regime / parcel / revenue / UCC

### 平台规则
- Amazon Seller News / Announcements
  - URL: https://sell.amazon.com/blog/announcements
  - 监控点：fee / reimbursement / account health / compliance / dangerous goods / returns
- Amazon Seller Forums - News and Announcements
  - URL: https://sellercentral.amazon.com/seller-forums/discussions?categories%5B0%5D=amzn1.spce.category.8b1ad9d2
  - 监控点：policy / fees / listing requirements / global selling / FBA / VAT
- TikTok Shop Newsroom
  - URL: https://newsroom.tiktok.com/
  - 监控点：shop / policy / fulfillment / compliance / seller / e-commerce

### 物流 / 航运
- FreightWaves News
  - URL: https://www.freightwaves.com/news
  - 监控点：port / freight / surcharge / container / customs / parcel / ocean / air cargo
- DHL Service Updates
  - URL: https://www.dhl.com/global-en/home/our-divisions/express/customer-service/important-information.html
  - 监控点：service update / surcharge / delay / customs / peak season

## P1｜第二批可加
- Marketplace Pulse
  - URL: https://www.marketplacepulse.com/
- Digital Commerce 360
  - URL: https://www.digitalcommerce360.com/
- 雨果跨境
  - URL: https://www.cifnews.com/
- 亿恩网
  - URL: https://www.ennews.com/
- The Loadstar
  - URL: https://theloadstar.com/

## changedetection.io 建议规则

### 页面选择策略
- 优先只盯：公告区、新闻列表区、规则更新区
- 避免盯：整页（噪音太大，容易误报）

### 关键词过滤建议
- tariff
- customs
- de minimis
- vat
- parcel
- cross-border
- fulfillment
- reimbursement
- account health
- dangerous goods
- compliance
- surcharge
- port
- delay

### 提醒策略
- P0 页面：有变化就提醒
- P1 页面：每日汇总一次

## 备注
- changedetection.io 更适合作为“页面变化雷达底座”
- 后续可以把告警统一喂给雷达分析层，而不是直接推给用户
