# Demo Suite v1

## 目标
用固定 demo 验证 analyze v1 的 contract、边界和误报控制，而不是只展示正常例子。

## 覆盖范围
1. 强相关、强信号
2. 相关但低置信
3. 易误报 / 应判弱相关
4. 完整对象输入

## Demo 列表
- `demo_01_tariff_us.json`：美国关税上调，验证强相关高风险
- `demo_02_eu_packaging.json`：欧盟包装要求，验证环境 / 合规类风险
- `demo_03_tariff_rumor.json`：关税传闻，验证低置信处理
- `demo_04_port_vote.json`：港口罢工投票，验证物流不确定性
- `demo_05_generic_policy.json`：泛政策新闻，验证不相关或弱相关边界
- `demo_06_brand_packaging_pr.json`：品牌环保 PR，验证包装关键词误报
- `demo_07_algorithm_update.json`：平台算法更新，验证 risk radar 范围边界
- `demo_08_full_object.json`：完整输入对象，验证 `url + region_hint + seller_profile`
