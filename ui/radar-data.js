window.RADAR_UI_DATA = {
  "meta": {
    "run_id": "radar-20260324-011127-dfeb6030",
    "generated_at": "2026-03-24T01:11:27Z",
    "source_mode": "seed",
    "snapshot_reason": "stale",
    "snapshot_usable": false,
    "event_count": 10,
    "profile_label": "通用雷达首页（事件驱动 / 不绑定默认画像）",
    "brief_type": "morning_radar_general"
  },
  "overview": {
    "headline": "通用雷达先盯 environment：欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
    "why_it_matters": "这条 environment 事件已经不是某个单一画像的小波动，而是所有卖家都该先扫一眼的首页信号；先看事件本身，再按高相关 / 中相关 / 低相关分层动作。",
    "source_mode": "seed",
    "top_risk": {
      "event_title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "event_type": "environment",
      "risk_level": "medium",
      "seller_angle": "新规强制要求可回收材料将直接推高包材采购成本10%-30%，利润空间受挤压；现有非合规库存面临滞销或报废风险，现金流压力加剧；违规商品面临强制下架、罚款甚至店铺关闭处分，合规成本骤增。"
    },
    "active_profile_modifier": {
      "platform": "全平台扫描",
      "seller_profile": "通用雷达首页"
    }
  },
  "dashboard": {
    "high_priority_count": 0,
    "top_story": {
      "title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "risk_type": "environment",
      "priority": "medium"
    },
    "risk_type_distribution": [
      "environment×1",
      "logistics×1",
      "tariff×1"
    ],
    "cards": [
      {
        "rank": 1,
        "title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
        "risk_type": "environment",
        "priority": "medium",
        "who_to_watch": "本地履约-平台主导（平台修正：全平台扫描 / 市场修正：EU / 重点看定价、补货、平台仓规则）",
        "action": "立即审计现有SKU包装材料，分类统计不合规品项数量与库存金额"
      },
      {
        "rank": 2,
        "title": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
        "risk_type": "tariff",
        "priority": "low",
        "who_to_watch": "跨境直发（平台修正：全平台扫描 / 市场修正：EU / 税后到手价与毛利最敏感）",
        "action": "立即清点€150以下SKU占比和利润贡献度，评估受影响订单规模"
      },
      {
        "rank": 3,
        "title": "欧洲港口工会罢工预警！物流时效延误风险上升",
        "risk_type": "logistics",
        "priority": "medium",
        "who_to_watch": "跨境直发（平台修正：全平台扫描 / 市场修正：EU / 时效、签收、退款链路最敏感）",
        "action": "启动海铁联运备选方案，绕开受影响港口"
      }
    ]
  },
  "today_actions": [
    "立即审计现有SKU包装材料，分类统计不合规品项数量与库存金额",
    "立即清点€150以下SKU占比和利润贡献度，评估受影响订单规模",
    "启动海铁联运备选方案，绕开受影响港口"
  ],
  "watch_items": [
    "紧急联系3-5家合规包材供应商获取报价，重新核算产品定价策略",
    "核算新增税费对各品类定价竞争力的影响，必要时启动调价预案",
    "紧急联系供应商补货，提前7-10天下单"
  ],
  "hold_line": "先别一上来就把首页绑定成某个默认画像；先看事件级别，再决定切去哪个画像深挖。",
  "fulfillment_actions": [
    {
      "path_key": "crossborder-direct-mail",
      "path_label": "跨境直发",
      "path_description": "包裹从境外直发到目标市场，先看税费、到手价、签收和退款链路。",
      "actions": [
        "逐个检查在售Listing的包装描述与实物，优先替换直邮产品包装",
        "与邮政小包服务商确认是否提供合规包材替代方案"
      ],
      "watchouts": [
        "直邮路径包装成本敏感度高，新规材料单价涨幅可能吞噬全部利润，需提前锁定供应商报价"
      ],
      "modifier": "平台修正：general / 市场修正：EU"
    },
    {
      "path_key": "local-fulfillment-platform-led",
      "path_label": "本地履约-平台主导",
      "path_description": "平台托管/半托管/FBA 一类，本地仓配能缓冲一部分冲击，但要盯价格带、补货和平台规则。",
      "actions": [
        "提前30天在卖家后台提交包装变更申请，预留平台审核时间",
        "分批次将FBA库存转运回仓重新包装，避免大批量报废"
      ],
      "watchouts": [
        "FBA入库商品须100%符合新规，旧库存可能因包装不合规被拒绝入仓产生高额退运费"
      ],
      "modifier": "平台修正：general / 市场修正：EU"
    },
    {
      "path_key": "local-fulfillment-merchant-led",
      "path_label": "本地履约-3PL/商家主导",
      "path_description": "商家自控海外仓或 3PL，本地履约更稳，但仓储、清关和尾程协同压力更高。",
      "actions": [
        "清点海外仓与自仓库存中非合规包装商品，制定促销清仓计划",
        "与海外仓运营商签署包材合规责任协议，明确违规损失分担"
      ],
      "watchouts": [
        "海外仓本地化包装更换周期长，需预留2-3个月缓冲期避免断货或违规在架销售"
      ],
      "modifier": "平台修正：general / 市场修正：EU"
    }
  ],
  "events": [
    {
      "id": "eu-150-eur-duty-threshold",
      "category": "macro",
      "scope": "global",
      "display_order": 1,
      "title": "欧盟取消 150 欧元跨境包裹免税额（2026年7月起征收每件€3关税）",
      "raw_title": "E-commerce: 150 EUR customs duty exemption threshold to be removed as of 2026",
      "summary": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "level": "high",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "独立站",
        "TikTok",
        "Amazon",
        "Temu",
        "AliExpress",
        "SHEIN"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "regulator-official",
      "source_priority": "P0",
      "impact": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "subject": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "action": "立即测算欧盟站低客单直邮商品在加征€3后的到手价和利润变化",
      "source": {
        "name": "欧盟委员会（European Commission）",
        "url": "https://taxation-customs.ec.europa.eu/news/e-commerce-150-eur-customs-duty-exemption-threshold-be-removed-2026-2025-11-13_en"
      },
      "timestamp": "2026-03-20T03:31:10.603799+00:00",
      "effective_date": "2026-07-01",
      "monitor_until": "2028-12-31",
      "brief_rank": 1,
      "ranking_score": null
    },
    {
      "id": "temu-us-deminimis-impact",
      "category": "urgent",
      "scope": "platform",
      "display_order": 2,
      "title": "美国取消小额包裹免税后 Temu 跨境物流成本上升 15-30%",
      "raw_title": "E-Commerce",
      "summary": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "level": "high",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "US"
      ],
      "source_layer": "policy-watch",
      "source_type": "regulator-official",
      "source_priority": "P0",
      "impact": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "subject": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "action": "重新测算美国站各 SKU 的含税成本，评估是否需要切换为本土仓发货",
      "source": {
        "name": "美国海关与边境保护局（CBP）",
        "url": "https://www.cbp.gov/trade/basic-import-export/e-commerce"
      },
      "timestamp": "2026-03-20T03:31:10.603799+00:00",
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 2,
      "ranking_score": null
    },
    {
      "id": "tiktok-fbt-mandate-us-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 3,
      "title": "TikTok Shop 美国站强制要求卖家使用平台物流（FBT）",
      "raw_title": "TikTok Shop Logistics Services Mandate",
      "summary": "【影响范围】所有使用 Seller Shipping 的美国本土卖家，含中小卖家和铺货型卖家。【政策要点】2026年3月31日前须迁移至 FBT（Fulfilled by TikTok）、Upgraded TikTok Shipping 或 Collections by TikTok 三选一；2月9日后新注册卖家已强制使用平台物流。【成本影响】FBT 仓储费约 $0.45/立方英尺/月，拣货打包费 $2.5–$5.0/单（视尺寸），与自发货相比轻小件成本上升约20%，大件反而可能降低。【卖家应对】① 对比top SKU在自发货vs FBT下的单件成本；② 关注FBT入仓周期（当前约7–10工作日）；③ 调整定价结构消化成本差异；④ 测试 Upgraded TikTok Shipping 的灵活性是否满足需求。",
      "level": "high",
      "type": "logistics",
      "typeLabel": "物流运输",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "US"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "自发货模式将于3月31日被完全取消。核心影响：① 物流成本结构重组，轻小件成本预计上升约20%；② 入仓周期（7–10天）加长备货提前量；③ 退货处理改由平台托管，售后流程需适配。",
      "subject": "【影响范围】所有使用 Seller Shipping 的美国本土卖家，含中小卖家和铺货型卖家。【政策要点】2026年3月31日前须迁移至 FBT（Fulfilled by TikTok）、Upgraded TikTok Shipping 或 Collections by TikTok 三选一；2月9日后新注册卖家已强制使用平台物流。【成本影响】FBT 仓储费约 $0.45/立方英尺/月，拣货打包费 $2.5–$5.0/单（视尺寸），与自发货相比轻小件成本上升约20%，大件反而可能降低。【卖家应对】① 对比top SKU在自发货vs FBT下的单件成本；② 关注FBT入仓周期（当前约7–10工作日）；③ 调整定价结构消化成本差异；④ 测试 Upgraded TikTok Shipping 的灵活性是否满足需求。",
      "action": "立即盘点全部美国站 SKU，按 FBT 费率表重新测算单件利润，优先迁移高频出单品",
      "source": {
        "name": "TikTok Shop 卖家中心（官方）",
        "url": "https://seller-us.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 3,
      "ranking_score": null
    },
    {
      "id": "tiktok-europe-expansion-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 4,
      "title": "TikTok Shop 加速欧洲扩张（法国/德国/意大利）",
      "raw_title": "TikTok Shop Europe Expansion",
      "summary": "【市场机遇】法国（6700万人口）、德国（8400万）、意大利（5900万）三国同步开放，合计2.1亿消费者。TikTok 欧洲月活已超1.5亿，短视频电商渗透率仍处早期红利阶段。【合规门槛】① 每国需独立 VAT 注册（德国还需 WEEE/包装法注册）；② 欧盟消费者享有14天无理由退货权，退货物流成本由卖家承担；③ 需符合 CE 标识/REACH 等产品安全认证要求。【卖家策略】建议优先选择与自身品类匹配的市场切入，先用轻小件测试渠道效率，前期可利用第三方欧洲海外仓降低合规和物流门槛。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "欧洲三国同步开放 = 2.1亿新消费者池。但每国要独立 VAT + 产品认证，14天退货权意味着退货率可能高于北美站。建议先用海外仓 + 轻小件测试。",
      "subject": "【市场机遇】法国（6700万人口）、德国（8400万）、意大利（5900万）三国同步开放，合计2.1亿消费者。TikTok 欧洲月活已超1.5亿，短视频电商渗透率仍处早期红利阶段。【合规门槛】① 每国需独立 VAT 注册（德国还需 WEEE/包装法注册）；② 欧盟消费者享有14天无理由退货权，退货物流成本由卖家承担；③ 需符合 CE 标识/REACH 等产品安全认证要求。【卖家策略】建议优先选择与自身品类匹配的市场切入，先用轻小件测试渠道效率，前期可利用第三方欧洲海外仓降低合规和物流门槛。",
      "action": "评估目标市场 VAT 注册成本（每国约€200–500/年），筛选无需CE认证的试销品类",
      "source": {
        "name": "TikTok 官方新闻",
        "url": "https://newsroom.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 4,
      "ranking_score": null
    },
    {
      "id": "tiktok-creator-commission-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 5,
      "title": "TikTok Shop 直播带货佣金与流量规则调整",
      "raw_title": "TikTok Shop Creator Commission Update",
      "summary": "【变更内容】TikTok Shop 调整了达人合作佣金结构：基础佣金率从5%上调至8%，同时平台对 Open Plan（公开计划）的流量扶持权重降低，更倾向 Targeted Plan（定向邀请）合作模式。【影响人群】依赖达人分销的中小卖家、尤其是美妆/服饰/3C配件等高佣品类。【成本测算】以月销10000单、客单价$25为例，佣金从$12500升至$20000，月增$7500。【应对建议】① 优化自播能力，降低对达人分销的依赖度；② 转向 Targeted Plan 合作高转化达人；③ 调整商品定价或优化供应链成本来消化佣金上涨。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "US",
        "UK",
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "达人佣金率上调3个百分点，中小卖家月均成本增加$5000–$10000。Open Plan 流量扶持被削弱，需转向自播或 Targeted Plan。",
      "subject": "【变更内容】TikTok Shop 调整了达人合作佣金结构：基础佣金率从5%上调至8%，同时平台对 Open Plan（公开计划）的流量扶持权重降低，更倾向 Targeted Plan（定向邀请）合作模式。【影响人群】依赖达人分销的中小卖家、尤其是美妆/服饰/3C配件等高佣品类。【成本测算】以月销10000单、客单价$25为例，佣金从$12500升至$20000，月增$7500。【应对建议】① 优化自播能力，降低对达人分销的依赖度；② 转向 Targeted Plan 合作高转化达人；③ 调整商品定价或优化供应链成本来消化佣金上涨。",
      "action": "评估当前达人带货 ROI，制定自播扩能计划，优化佣金结构",
      "source": {
        "name": "TikTok Shop 卖家中心（官方）",
        "url": "https://seller-us.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 5,
      "ranking_score": null
    },
    {
      "id": "temu-turkey-restructure-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 6,
      "title": "Temu 土耳其跨境业务重组（WhaleCo 本地实体清关）",
      "raw_title": "Temu Turkey Business Restructure",
      "summary": "【政策背景】土耳其商务部取消了€30以下商品简化清关程序，所有跨境包裹均需完整报关缴税。【平台应对】Temu 通过设立本地子公司 WhaleCo 作为进口商（Importer of Record），统一处理清关申报，买家在结账时预付关税和消费税。【卖家影响】① 买家到手价上涨15–25%（取决于品类关税税率），可能拉低转化率；② 退货退款流程复杂化（涉及关税退还），处理时效延长；③ 高客单商品反而受益——之前的低价优势被削弱，品质感商品竞争力上升。【建议】调整土耳其市场定价策略，将关税测算内嵌到选品模型中。",
      "level": "high",
      "type": "customs",
      "typeLabel": "海关查验",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "Turkey"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "到手价上涨15–25%直接影响转化率。退货退款需处理关税退还，周期延长。但高客单商品的竞争环境改善——低价铺货型卖家受冲击更大。",
      "subject": "【政策背景】土耳其商务部取消了€30以下商品简化清关程序，所有跨境包裹均需完整报关缴税。【平台应对】Temu 通过设立本地子公司 WhaleCo 作为进口商（Importer of Record），统一处理清关申报，买家在结账时预付关税和消费税。【卖家影响】① 买家到手价上涨15–25%（取决于品类关税税率），可能拉低转化率；② 退货退款流程复杂化（涉及关税退还），处理时效延长；③ 高客单商品反而受益——之前的低价优势被削弱，品质感商品竞争力上升。【建议】调整土耳其市场定价策略，将关税测算内嵌到选品模型中。",
      "action": "重新测算土耳其站 top100 SKU 的含税到手价，淘汰利润不足5%的品",
      "source": {
        "name": "Temu 卖家中心（官方）",
        "url": "https://seller.kuajingmaihuo.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 6,
      "ranking_score": null
    },
    {
      "id": "temu-semi-managed-expansion-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 7,
      "title": "Temu 半托管模式全面扩展至美国/欧洲市场",
      "raw_title": "Temu Semi-managed Model Expansion",
      "summary": "【模式变化】Temu 在美国和欧洲加速推广「半托管」模式：卖家自行管理本地仓库存和发货，Temu 负责站内流量和营销。与全托管相比，卖家拥有更大的定价自主权和库存控制权。【适用卖家】已在美国/欧洲有海外仓或合作物流的卖家，尤其是从亚马逊/独立站多渠道运营的卖家。【机遇分析】① 毛利率提升空间（全托管利润率通常仅3–8%，半托管可达15–25%）；② 自主定价权避免被平台压价；③ 更灵活的库存管理。【风险提示】① 本地仓运营成本（租金+人工）需自行承担；② 平台对发货时效有严格要求（48小时内出库），违规会被降权。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "US",
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "半托管利润率（15–25%）远高于全托管（3–8%），但需自备海外仓。适合已有美国/欧洲仓储的多渠道卖家，新卖家建议先用第三方海外仓试水。",
      "subject": "【模式变化】Temu 在美国和欧洲加速推广「半托管」模式：卖家自行管理本地仓库存和发货，Temu 负责站内流量和营销。与全托管相比，卖家拥有更大的定价自主权和库存控制权。【适用卖家】已在美国/欧洲有海外仓或合作物流的卖家，尤其是从亚马逊/独立站多渠道运营的卖家。【机遇分析】① 毛利率提升空间（全托管利润率通常仅3–8%，半托管可达15–25%）；② 自主定价权避免被平台压价；③ 更灵活的库存管理。【风险提示】① 本地仓运营成本（租金+人工）需自行承担；② 平台对发货时效有严格要求（48小时内出库），违规会被降权。",
      "action": "评估现有海外仓产能是否可分配给 Temu 半托管，测算半托管 vs 全托管的 SKU 级利润差异",
      "source": {
        "name": "Temu 卖家中心（官方）",
        "url": "https://seller.kuajingmaihuo.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 7,
      "ranking_score": null
    },
    {
      "id": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "category": "daily",
      "scope": "platform",
      "display_order": 1,
      "title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "raw_title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "summary": "潜在 欧洲 环保 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "medium",
      "type": "environment",
      "typeLabel": "合规标准",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "新规强制要求可回收材料将直接推高包材采购成本10%-30%，利润空间受挤压；现有非合规库存面临滞销或报废风险，现金流压力加剧；违规商品面临强制下架、罚款甚至店铺关闭处分，合规成本骤增。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "立即审计现有SKU包装材料，分类统计不合规品项数量与库存金额",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-packaging-rule"
      },
      "timestamp": null,
      "brief_rank": 1,
      "ranking_score": 114
    },
    {
      "id": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "category": "daily",
      "scope": "platform",
      "display_order": 2,
      "title": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "raw_title": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "summary": "潜在 欧洲 关税 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "low",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "欧盟若取消€150以下小额包裹免税，低客单价直邮卖家的物流成本将直接转嫁到商品价格，竞争力下降。直邮模式原本的价格优势可能被税费抵消30%-50%，部分品类可能被迫退出欧盟市场。合规成本也将从隐形成本变为显性支出，中小卖家现金流压力加大。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "立即清点€150以下SKU占比和利润贡献度，评估受影响订单规模",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-small-parcel-tax"
      },
      "timestamp": null,
      "brief_rank": 2,
      "ranking_score": 94
    },
    {
      "id": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "category": "daily",
      "scope": "platform",
      "display_order": 3,
      "title": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "raw_title": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "summary": "潜在 欧洲 物流 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "medium",
      "type": "logistics",
      "typeLabel": "物流运输",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "欧洲主要港口若发生罢工，跨境物流时效将延长3-7个工作日，配送延迟将直接挤压利润空间并引发客诉；旺季备货窗口收窄，库存周转压力剧增，仓储成本显著上升；平台绩效指标可能因物流原因受损，店铺搜索排名和账号安全面临风险。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "启动海铁联运备选方案，绕开受影响港口",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/port-union-vote"
      },
      "timestamp": null,
      "brief_rank": 3,
      "ranking_score": 71
    }
  ],
  "macro_events": [
    {
      "id": "eu-150-eur-duty-threshold",
      "category": "macro",
      "scope": "global",
      "display_order": 1,
      "title": "欧盟取消 150 欧元跨境包裹免税额（2026年7月起征收每件€3关税）",
      "raw_title": "E-commerce: 150 EUR customs duty exemption threshold to be removed as of 2026",
      "summary": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "level": "high",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "独立站",
        "TikTok",
        "Amazon",
        "Temu",
        "AliExpress",
        "SHEIN"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "regulator-official",
      "source_priority": "P0",
      "impact": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "subject": "欧盟确认取消 150 欧元跨境包裹免税额。2026年7月1日起，所有非欧盟电商包裹先征收每件€3的临时固定关税；2026年11月加收手续费；约2028年中欧盟海关数据中心上线后按正式税率征收。直邮小包的到手价、利润和清关成本都会被改写。",
      "action": "立即测算欧盟站低客单直邮商品在加征€3后的到手价和利润变化",
      "source": {
        "name": "欧盟委员会（European Commission）",
        "url": "https://taxation-customs.ec.europa.eu/news/e-commerce-150-eur-customs-duty-exemption-threshold-be-removed-2026-2025-11-13_en"
      },
      "timestamp": "2026-03-20T03:31:10.603799+00:00",
      "effective_date": "2026-07-01",
      "monitor_until": "2028-12-31",
      "brief_rank": 1,
      "ranking_score": null
    }
  ],
  "urgent_events": [
    {
      "id": "temu-us-deminimis-impact",
      "category": "urgent",
      "scope": "platform",
      "display_order": 2,
      "title": "美国取消小额包裹免税后 Temu 跨境物流成本上升 15-30%",
      "raw_title": "E-Commerce",
      "summary": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "level": "high",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "US"
      ],
      "source_layer": "policy-watch",
      "source_type": "regulator-official",
      "source_priority": "P0",
      "impact": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "subject": "美国取消 800 美元以下小额包裹免税后，Temu 跨境直邮小包成本预计上升 15-30%，所有进口商品不论金额都需要完整申报和缴税。平台曾因此短暂暂停中国到美国的发货。卖家需重新测算各商品的盈亏平衡点。",
      "action": "重新测算美国站各 SKU 的含税成本，评估是否需要切换为本土仓发货",
      "source": {
        "name": "美国海关与边境保护局（CBP）",
        "url": "https://www.cbp.gov/trade/basic-import-export/e-commerce"
      },
      "timestamp": "2026-03-20T03:31:10.603799+00:00",
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 2,
      "ranking_score": null
    },
    {
      "id": "tiktok-fbt-mandate-us-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 3,
      "title": "TikTok Shop 美国站强制要求卖家使用平台物流（FBT）",
      "raw_title": "TikTok Shop Logistics Services Mandate",
      "summary": "【影响范围】所有使用 Seller Shipping 的美国本土卖家，含中小卖家和铺货型卖家。【政策要点】2026年3月31日前须迁移至 FBT（Fulfilled by TikTok）、Upgraded TikTok Shipping 或 Collections by TikTok 三选一；2月9日后新注册卖家已强制使用平台物流。【成本影响】FBT 仓储费约 $0.45/立方英尺/月，拣货打包费 $2.5–$5.0/单（视尺寸），与自发货相比轻小件成本上升约20%，大件反而可能降低。【卖家应对】① 对比top SKU在自发货vs FBT下的单件成本；② 关注FBT入仓周期（当前约7–10工作日）；③ 调整定价结构消化成本差异；④ 测试 Upgraded TikTok Shipping 的灵活性是否满足需求。",
      "level": "high",
      "type": "logistics",
      "typeLabel": "物流运输",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "US"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "自发货模式将于3月31日被完全取消。核心影响：① 物流成本结构重组，轻小件成本预计上升约20%；② 入仓周期（7–10天）加长备货提前量；③ 退货处理改由平台托管，售后流程需适配。",
      "subject": "【影响范围】所有使用 Seller Shipping 的美国本土卖家，含中小卖家和铺货型卖家。【政策要点】2026年3月31日前须迁移至 FBT（Fulfilled by TikTok）、Upgraded TikTok Shipping 或 Collections by TikTok 三选一；2月9日后新注册卖家已强制使用平台物流。【成本影响】FBT 仓储费约 $0.45/立方英尺/月，拣货打包费 $2.5–$5.0/单（视尺寸），与自发货相比轻小件成本上升约20%，大件反而可能降低。【卖家应对】① 对比top SKU在自发货vs FBT下的单件成本；② 关注FBT入仓周期（当前约7–10工作日）；③ 调整定价结构消化成本差异；④ 测试 Upgraded TikTok Shipping 的灵活性是否满足需求。",
      "action": "立即盘点全部美国站 SKU，按 FBT 费率表重新测算单件利润，优先迁移高频出单品",
      "source": {
        "name": "TikTok Shop 卖家中心（官方）",
        "url": "https://seller-us.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 3,
      "ranking_score": null
    },
    {
      "id": "tiktok-europe-expansion-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 4,
      "title": "TikTok Shop 加速欧洲扩张（法国/德国/意大利）",
      "raw_title": "TikTok Shop Europe Expansion",
      "summary": "【市场机遇】法国（6700万人口）、德国（8400万）、意大利（5900万）三国同步开放，合计2.1亿消费者。TikTok 欧洲月活已超1.5亿，短视频电商渗透率仍处早期红利阶段。【合规门槛】① 每国需独立 VAT 注册（德国还需 WEEE/包装法注册）；② 欧盟消费者享有14天无理由退货权，退货物流成本由卖家承担；③ 需符合 CE 标识/REACH 等产品安全认证要求。【卖家策略】建议优先选择与自身品类匹配的市场切入，先用轻小件测试渠道效率，前期可利用第三方欧洲海外仓降低合规和物流门槛。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "欧洲三国同步开放 = 2.1亿新消费者池。但每国要独立 VAT + 产品认证，14天退货权意味着退货率可能高于北美站。建议先用海外仓 + 轻小件测试。",
      "subject": "【市场机遇】法国（6700万人口）、德国（8400万）、意大利（5900万）三国同步开放，合计2.1亿消费者。TikTok 欧洲月活已超1.5亿，短视频电商渗透率仍处早期红利阶段。【合规门槛】① 每国需独立 VAT 注册（德国还需 WEEE/包装法注册）；② 欧盟消费者享有14天无理由退货权，退货物流成本由卖家承担；③ 需符合 CE 标识/REACH 等产品安全认证要求。【卖家策略】建议优先选择与自身品类匹配的市场切入，先用轻小件测试渠道效率，前期可利用第三方欧洲海外仓降低合规和物流门槛。",
      "action": "评估目标市场 VAT 注册成本（每国约€200–500/年），筛选无需CE认证的试销品类",
      "source": {
        "name": "TikTok 官方新闻",
        "url": "https://newsroom.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 4,
      "ranking_score": null
    },
    {
      "id": "tiktok-creator-commission-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 5,
      "title": "TikTok Shop 直播带货佣金与流量规则调整",
      "raw_title": "TikTok Shop Creator Commission Update",
      "summary": "【变更内容】TikTok Shop 调整了达人合作佣金结构：基础佣金率从5%上调至8%，同时平台对 Open Plan（公开计划）的流量扶持权重降低，更倾向 Targeted Plan（定向邀请）合作模式。【影响人群】依赖达人分销的中小卖家、尤其是美妆/服饰/3C配件等高佣品类。【成本测算】以月销10000单、客单价$25为例，佣金从$12500升至$20000，月增$7500。【应对建议】① 优化自播能力，降低对达人分销的依赖度；② 转向 Targeted Plan 合作高转化达人；③ 调整商品定价或优化供应链成本来消化佣金上涨。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "TikTok"
      ],
      "regions": [
        "US",
        "UK",
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "达人佣金率上调3个百分点，中小卖家月均成本增加$5000–$10000。Open Plan 流量扶持被削弱，需转向自播或 Targeted Plan。",
      "subject": "【变更内容】TikTok Shop 调整了达人合作佣金结构：基础佣金率从5%上调至8%，同时平台对 Open Plan（公开计划）的流量扶持权重降低，更倾向 Targeted Plan（定向邀请）合作模式。【影响人群】依赖达人分销的中小卖家、尤其是美妆/服饰/3C配件等高佣品类。【成本测算】以月销10000单、客单价$25为例，佣金从$12500升至$20000，月增$7500。【应对建议】① 优化自播能力，降低对达人分销的依赖度；② 转向 Targeted Plan 合作高转化达人；③ 调整商品定价或优化供应链成本来消化佣金上涨。",
      "action": "评估当前达人带货 ROI，制定自播扩能计划，优化佣金结构",
      "source": {
        "name": "TikTok Shop 卖家中心（官方）",
        "url": "https://seller-us.tiktok.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 5,
      "ranking_score": null
    },
    {
      "id": "temu-turkey-restructure-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 6,
      "title": "Temu 土耳其跨境业务重组（WhaleCo 本地实体清关）",
      "raw_title": "Temu Turkey Business Restructure",
      "summary": "【政策背景】土耳其商务部取消了€30以下商品简化清关程序，所有跨境包裹均需完整报关缴税。【平台应对】Temu 通过设立本地子公司 WhaleCo 作为进口商（Importer of Record），统一处理清关申报，买家在结账时预付关税和消费税。【卖家影响】① 买家到手价上涨15–25%（取决于品类关税税率），可能拉低转化率；② 退货退款流程复杂化（涉及关税退还），处理时效延长；③ 高客单商品反而受益——之前的低价优势被削弱，品质感商品竞争力上升。【建议】调整土耳其市场定价策略，将关税测算内嵌到选品模型中。",
      "level": "high",
      "type": "customs",
      "typeLabel": "海关查验",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "Turkey"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "到手价上涨15–25%直接影响转化率。退货退款需处理关税退还，周期延长。但高客单商品的竞争环境改善——低价铺货型卖家受冲击更大。",
      "subject": "【政策背景】土耳其商务部取消了€30以下商品简化清关程序，所有跨境包裹均需完整报关缴税。【平台应对】Temu 通过设立本地子公司 WhaleCo 作为进口商（Importer of Record），统一处理清关申报，买家在结账时预付关税和消费税。【卖家影响】① 买家到手价上涨15–25%（取决于品类关税税率），可能拉低转化率；② 退货退款流程复杂化（涉及关税退还），处理时效延长；③ 高客单商品反而受益——之前的低价优势被削弱，品质感商品竞争力上升。【建议】调整土耳其市场定价策略，将关税测算内嵌到选品模型中。",
      "action": "重新测算土耳其站 top100 SKU 的含税到手价，淘汰利润不足5%的品",
      "source": {
        "name": "Temu 卖家中心（官方）",
        "url": "https://seller.kuajingmaihuo.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 6,
      "ranking_score": null
    },
    {
      "id": "temu-semi-managed-expansion-seed",
      "category": "urgent",
      "scope": "platform",
      "display_order": 7,
      "title": "Temu 半托管模式全面扩展至美国/欧洲市场",
      "raw_title": "Temu Semi-managed Model Expansion",
      "summary": "【模式变化】Temu 在美国和欧洲加速推广「半托管」模式：卖家自行管理本地仓库存和发货，Temu 负责站内流量和营销。与全托管相比，卖家拥有更大的定价自主权和库存控制权。【适用卖家】已在美国/欧洲有海外仓或合作物流的卖家，尤其是从亚马逊/独立站多渠道运营的卖家。【机遇分析】① 毛利率提升空间（全托管利润率通常仅3–8%，半托管可达15–25%）；② 自主定价权避免被平台压价；③ 更灵活的库存管理。【风险提示】① 本地仓运营成本（租金+人工）需自行承担；② 平台对发货时效有严格要求（48小时内出库），违规会被降权。",
      "level": "medium",
      "type": "policy",
      "typeLabel": "平台政策",
      "platforms": [
        "Temu"
      ],
      "regions": [
        "US",
        "EU"
      ],
      "source_layer": "policy-watch",
      "source_type": "platform-official",
      "source_priority": "P0",
      "impact": "半托管利润率（15–25%）远高于全托管（3–8%），但需自备海外仓。适合已有美国/欧洲仓储的多渠道卖家，新卖家建议先用第三方海外仓试水。",
      "subject": "【模式变化】Temu 在美国和欧洲加速推广「半托管」模式：卖家自行管理本地仓库存和发货，Temu 负责站内流量和营销。与全托管相比，卖家拥有更大的定价自主权和库存控制权。【适用卖家】已在美国/欧洲有海外仓或合作物流的卖家，尤其是从亚马逊/独立站多渠道运营的卖家。【机遇分析】① 毛利率提升空间（全托管利润率通常仅3–8%，半托管可达15–25%）；② 自主定价权避免被平台压价；③ 更灵活的库存管理。【风险提示】① 本地仓运营成本（租金+人工）需自行承担；② 平台对发货时效有严格要求（48小时内出库），违规会被降权。",
      "action": "评估现有海外仓产能是否可分配给 Temu 半托管，测算半托管 vs 全托管的 SKU 级利润差异",
      "source": {
        "name": "Temu 卖家中心（官方）",
        "url": "https://seller.kuajingmaihuo.com/"
      },
      "timestamp": null,
      "effective_date": null,
      "monitor_until": null,
      "brief_rank": 7,
      "ranking_score": null
    }
  ],
  "daily_events": [
    {
      "id": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "category": "daily",
      "scope": "platform",
      "display_order": 1,
      "title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "raw_title": "欧盟包装可回收新规：材料替换成本、库存报废与下架风险三重冲击",
      "summary": "潜在 欧洲 环保 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "medium",
      "type": "environment",
      "typeLabel": "合规标准",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "新规强制要求可回收材料将直接推高包材采购成本10%-30%，利润空间受挤压；现有非合规库存面临滞销或报废风险，现金流压力加剧；违规商品面临强制下架、罚款甚至店铺关闭处分，合规成本骤增。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "立即审计现有SKU包装材料，分类统计不合规品项数量与库存金额",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-packaging-rule"
      },
      "timestamp": null,
      "brief_rank": 1,
      "ranking_score": 114
    },
    {
      "id": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "category": "daily",
      "scope": "platform",
      "display_order": 2,
      "title": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "raw_title": "欧盟取消低价值包裹免税预警：直邮卖家成本压力骤增",
      "summary": "潜在 欧洲 关税 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "low",
      "type": "tariff",
      "typeLabel": "关税与税务",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "欧盟若取消€150以下小额包裹免税，低客单价直邮卖家的物流成本将直接转嫁到商品价格，竞争力下降。直邮模式原本的价格优势可能被税费抵消30%-50%，部分品类可能被迫退出欧盟市场。合规成本也将从隐形成本变为显性支出，中小卖家现金流压力加大。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "立即清点€150以下SKU占比和利润贡献度，评估受影响订单规模",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-small-parcel-tax"
      },
      "timestamp": null,
      "brief_rank": 2,
      "ranking_score": 94
    },
    {
      "id": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "category": "daily",
      "scope": "platform",
      "display_order": 3,
      "title": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "raw_title": "欧洲港口工会罢工预警！物流时效延误风险上升",
      "summary": "潜在 欧洲 物流 事件，可能会影响当前的跨境履约、利润或合规操作。",
      "level": "medium",
      "type": "logistics",
      "typeLabel": "物流运输",
      "platforms": [
        "多平台波及"
      ],
      "regions": [
        "EU"
      ],
      "source_layer": "",
      "source_type": "",
      "source_priority": "",
      "impact": "欧洲主要港口若发生罢工，跨境物流时效将延长3-7个工作日，配送延迟将直接挤压利润空间并引发客诉；旺季备货窗口收窄，库存周转压力剧增，仓储成本显著上升；平台绩效指标可能因物流原因受损，店铺搜索排名和账号安全面临风险。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "启动海铁联运备选方案，绕开受影响港口",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/port-union-vote"
      },
      "timestamp": null,
      "brief_rank": 3,
      "ranking_score": 71
    }
  ]
};
