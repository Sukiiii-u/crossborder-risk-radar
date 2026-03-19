# changedetection.io 本地运行（Python 方案）

## 当前状态
- 已本地安装到：`monitoring/changedetection-venv`
- 数据目录：`monitoring/changedetection-data`
- 本地端口：`5002`（稳定可用）

## 稳定启动命令
```bash
ALLOW_IANA_RESTRICTED_ADDRESSES=true \
/Users/lisiqi/.openclaw/workspace/swarm/skills/crossborder-risk-radar/monitoring/changedetection-venv/bin/changedetection.py \
  -d /Users/lisiqi/.openclaw/workspace/swarm/skills/crossborder-risk-radar/monitoring/changedetection-data \
  -p 5002
```

## 访问
- 本地 UI：`http://127.0.0.1:5002/`
- RSS Feed：`http://127.0.0.1:5002/rss?token=f8698465ca99910c04faa35a4f6a0f04`

## 现状说明
- 服务本身已经能启动
- 数据目录初始化成功
- 当前环境里外部站点会被解析到 `198.18.x.x`，默认会被 changedetection 当作 private/reserved host 拦截
- 通过设置 `ALLOW_IANA_RESTRICTED_ADDRESSES=true`，本地验证环境已经可以继续抓取外网页面

## P0 监控源（已导入）
| 源 | URL | 状态 |
|---|---|---|
| CBP Trade | https://www.cbp.gov/newsroom/media-releases/trade | ✅ 正常 |
| EU Taxation & Customs | https://taxation-customs.ec.europa.eu/index_en | ✅ 正常 |
| EU Customs Reform | https://taxation-customs.ec.europa.eu/customs/eu-customs-reform_en | ✅ 正常 |
| Amazon Seller Announcements | https://sell.amazon.com/blog/announcements | ✅ 正常 |
| Amazon Seller Forums | https://sellercentral.amazon.com/seller-forums/discussions?categories%5B0%5D=amzn1.spce.category.8b1ad9d2 | ✅ 正常 |
| TikTok Shop Newsroom | https://newsroom.tiktok.com/ | ✅ 正常 |
| FreightWaves | https://www.freightwaves.com/news | ⚠️ 403 访问被拒绝 |
| DHL Service Updates | https://www.dhl.com/global-en/home/our-divisions/express/customer-service/important-information.html | ✅ 正常 |

## 结论
- 本地验证层面：changedetection.io 已接上
- 当前这套本地方案已经能继续往"导入 P0 监控页并做闭环验证"推进
