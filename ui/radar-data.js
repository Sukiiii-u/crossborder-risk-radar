window.RADAR_UI_DATA = {
  "meta": {
    "run_id": "radar-20260322-235613-779469e9",
    "generated_at": "2026-03-22T23:56:13Z",
    "source_mode": "seed",
    "snapshot_reason": "stale",
    "snapshot_usable": false,
    "event_count": 10,
    "profile_label": "通用雷达首页（事件驱动 / 不绑定默认画像）",
    "brief_type": "morning_radar_general"
  },
  "overview": {
    "headline": "通用雷达先盯 environment：欧盟收紧包装可回收要求，卖家或需更换材料与标签",
    "why_it_matters": "这条 environment 事件已经不是某个单一画像的小波动，而是所有卖家都该先扫一眼的首页信号；先看事件本身，再按高相关 / 中相关 / 低相关分层动作。",
    "source_mode": "seed",
    "top_risk": {
      "event_title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
      "event_type": "environment",
      "risk_level": "medium",
      "seller_angle": "欧盟新规将强制要求包装材料达到更高可回收比例，违规商品面临入境拦截或强制下架风险。更换合规材料将推高采购成本5%-15%，在售库存若使用不合规包装可能产生大规模召回损失。部分平台已同步更新入仓标准，未及时调整的listing将影响评级与流量分配。"
    },
    "active_profile_modifier": {
      "platform": "全平台扫描",
      "seller_profile": "通用雷达首页"
    }
  },
  "dashboard": {
    "high_priority_count": 0,
    "top_story": {
      "title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
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
        "title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
        "risk_type": "environment",
        "priority": "medium",
        "who_to_watch": "本地履约-平台主导（平台修正：全平台扫描 / 市场修正：EU / 重点看定价、补货、平台仓规则）",
        "action": "盘点和审计现有库存包装材料的合规状态"
      },
      {
        "rank": 2,
        "title": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
        "risk_type": "tariff",
        "priority": "low",
        "who_to_watch": "跨境直发（平台修正：全平台扫描 / 市场修正：EU / 税后到手价与毛利最敏感）",
        "action": "重新测算含税成本模型，测试价格弹性临界点"
      },
      {
        "rank": 3,
        "title": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
        "risk_type": "logistics",
        "priority": "medium",
        "who_to_watch": "跨境直发（平台修正：全平台扫描 / 市场修正：EU / 时效、签收、退款链路最敏感）",
        "action": "启动港口罢工应急预案，联系货代确认替代航线及备用清关口岸"
      }
    ]
  },
  "today_actions": [
    "盘点和审计现有库存包装材料的合规状态",
    "重新测算含税成本模型，测试价格弹性临界点",
    "启动港口罢工应急预案，联系货代确认替代航线及备用清关口岸"
  ],
  "watch_items": [
    "联系供应商获取可回收材料认证文件",
    "建立多国VAT合规矩阵，评估各站点申报义务",
    "排查近30天入欧在途货物，预判滞留风险并提前通知买家延长预期"
  ],
  "hold_line": "先别一上来就把首页绑定成某个默认画像；先看事件级别，再决定切去哪个画像深挖。",
  "fulfillment_actions": [
    {
      "path_key": "crossborder-direct-mail",
      "path_label": "跨境直发",
      "path_description": "包裹从境外直发到目标市场，先看税费、到手价、签收和退款链路。",
      "actions": [
        "批量发运前抽检包装合规性，保留检测报告备查",
        "提前通知买家因材料更换可能产生的包装外观差异"
      ],
      "watchouts": [
        "小包直发在清关时面临更高抽检概率，合规证明缺失将直接导致扣货或退运"
      ],
      "modifier": "平台修正：general / 市场修正：EU"
    },
    {
      "path_key": "local-fulfillment-platform-led",
      "path_label": "本地履约-平台主导",
      "path_description": "平台托管/半托管/FBA 一类，本地仓配能缓冲一部分冲击，但要盯价格带、补货和平台规则。",
      "actions": [
        "登录卖家后台核查FBA/全托管库存的入仓合规状态",
        "向平台申请非合规库存的缓冲处理窗口期"
      ],
      "watchouts": [
        "平台仓对包装材料的准入门槛实时更新，存量库存可能因规则追溯被强制移出仓"
      ],
      "modifier": "平台修正：general / 市场修正：EU"
    },
    {
      "path_key": "local-fulfillment-merchant-led",
      "path_label": "本地履约-3PL/商家主导",
      "path_description": "商家自控海外仓或 3PL，本地履约更稳，但仓储、清关和尾程协同压力更高。",
      "actions": [
        "通知海外仓3PL服务商同步执行新包装材料标准",
        "制定非合规库存的折价清仓或销毁处置预算"
      ],
      "watchouts": [
        "自发货与海外仓模式下合规成本由卖家全额承担，非标材料库存滞销将直接侵蚀利润。"
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
      "id": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
      "category": "daily",
      "scope": "platform",
      "display_order": 1,
      "title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
      "raw_title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
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
      "impact": "欧盟新规将强制要求包装材料达到更高可回收比例，违规商品面临入境拦截或强制下架风险。更换合规材料将推高采购成本5%-15%，在售库存若使用不合规包装可能产生大规模召回损失。部分平台已同步更新入仓标准，未及时调整的listing将影响评级与流量分配。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "盘点和审计现有库存包装材料的合规状态",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-packaging-rule"
      },
      "timestamp": null,
      "brief_rank": 1,
      "ranking_score": 114
    },
    {
      "id": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
      "category": "daily",
      "scope": "platform",
      "display_order": 2,
      "title": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
      "raw_title": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
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
      "impact": "欧盟取消低价值包裹免税后，直邮小包成本将增加15-30欧元/件，低客单价（＜30欧）商品利润空间面临腰斩风险。合规成本上升将倒逼卖家重构定价体系，原有的低价直邮竞争优势将大幅削弱。海关申报复杂度提升，合规风险从被动抽检转向主动审查机制。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "重新测算含税成本模型，测试价格弹性临界点",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-small-parcel-tax"
      },
      "timestamp": null,
      "brief_rank": 2,
      "ranking_score": 94
    },
    {
      "id": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
      "category": "daily",
      "scope": "platform",
      "display_order": 3,
      "title": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
      "raw_title": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
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
      "impact": "罢工投票可能导致港口装卸作业停滞，欧洲跨境物流平均时效预计延误3-7个工作日。对于依赖即时补货的卖家，高周转SKU断货风险上升约25%。物流成本将因改港绕行和临时仓储需求上涨15%-30%，直接压缩品类利润率。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "启动港口罢工应急预案，联系货代确认替代航线及备用清关口岸",
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
      "id": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
      "category": "daily",
      "scope": "platform",
      "display_order": 1,
      "title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
      "raw_title": "欧盟收紧包装可回收要求，卖家或需更换材料与标签",
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
      "impact": "欧盟新规将强制要求包装材料达到更高可回收比例，违规商品面临入境拦截或强制下架风险。更换合规材料将推高采购成本5%-15%，在售库存若使用不合规包装可能产生大规模召回损失。部分平台已同步更新入仓标准，未及时调整的listing将影响评级与流量分配。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "盘点和审计现有库存包装材料的合规状态",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-packaging-rule"
      },
      "timestamp": null,
      "brief_rank": 1,
      "ranking_score": 114
    },
    {
      "id": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
      "category": "daily",
      "scope": "platform",
      "display_order": 2,
      "title": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
      "raw_title": "欧盟取消直邮免税政策：低客单价卖家利润空间或被腰斩",
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
      "impact": "欧盟取消低价值包裹免税后，直邮小包成本将增加15-30欧元/件，低客单价（＜30欧）商品利润空间面临腰斩风险。合规成本上升将倒逼卖家重构定价体系，原有的低价直邮竞争优势将大幅削弱。海关申报复杂度提升，合规风险从被动抽检转向主动审查机制。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "重新测算含税成本模型，测试价格弹性临界点",
      "source": {
        "name": "user-provided",
        "url": "https://example.com/eu-small-parcel-tax"
      },
      "timestamp": null,
      "brief_rank": 2,
      "ranking_score": 94
    },
    {
      "id": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
      "category": "daily",
      "scope": "platform",
      "display_order": 3,
      "title": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
      "raw_title": "欧盟港口工会罢工投票预警：物流时效与库存风险上升",
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
      "impact": "罢工投票可能导致港口装卸作业停滞，欧洲跨境物流平均时效预计延误3-7个工作日。对于依赖即时补货的卖家，高周转SKU断货风险上升约25%。物流成本将因改港绕行和临时仓储需求上涨15%-30%，直接压缩品类利润率。",
      "subject": "布局 EU 市场的 general mixed 卖家",
      "action": "启动港口罢工应急预案，联系货代确认替代航线及备用清关口岸",
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
