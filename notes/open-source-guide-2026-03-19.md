# 跨境风险雷达 — 开源指南

## 开源前检查清单

- [x] `.gitignore` 已排除敏感文件（API Key、代理配置、运行时数据）
- [x] 提供 `.example.json` 配置模板
- [x] 代码无硬编码密钥
- [x] LLM 依赖可选（有完整 fallback）
- [x] 无第三方 Python 依赖
- [x] README.md 已编写（含快速开始、架构、数据源清单）
- [ ] 创建 GitHub 仓库并推送

## 开源步骤

### 1. 创建 GitHub 仓库

```bash
# 在 GitHub 网页创建新仓库（名称建议：crossborder-risk-radar）
# 选择 Public，不勾选 Initialize with README（我们已经有了）
```

### 2. 推送代码

```bash
cd /Users/lisiqi/.openclaw/workspace/swarm/skills/crossborder-risk-radar

# 初始化 Git（如果还没有）
git init

# 添加远程仓库
git remote add origin https://github.com/你的用户名/crossborder-risk-radar.git

# 确认 .gitignore 生效
git status
# 确保以下文件不在列表中：
#   configs/llm_config.json（含 API Key）
#   configs/fetch_network.json（含代理地址）
#   runtime/data/*（运行时数据）
#   ui/radar-data.js（生成的前端数据）

# 提交并推送
git add .
git commit -m "初始提交：跨境风险雷达 v1.0"
git branch -M main
git push -u origin main
```

### 3. 推送前二次确认

```bash
# 搜索是否有遗漏的密钥
grep -r "sk-" --include="*.json" --include="*.py" . | grep -v ".example" | grep -v __pycache__
# 应该只在 configs/llm_config.json 中出现（已被 gitignore 排除）

# 确认 git 不会追踪敏感文件
git ls-files --cached | grep -E "llm_config|fetch_network|changedetection_source"
# 如果有输出，说明文件已被追踪，需要先移除：
# git rm --cached configs/llm_config.json
```

### 4. 添加 GitHub 仓库描述

建议描述：
> 面向跨境电商卖家的实时风险监测系统 | 45个数据源 | 11个平台覆盖 | AI智能分析 | 零依赖部署

建议 Topics 标签：
`crossborder` `ecommerce` `risk-monitoring` `amazon` `tiktok-shop` `temu` `rss` `python` `ai`

### 5. 发布 Release

```bash
git tag v1.0.0 -m "跨境风险雷达 v1.0.0 — 首次公开发布"
git push origin v1.0.0
```

然后在 GitHub 仓库页面 → Releases → Create release，选择 v1.0.0 标签。

## 许可证选择

推荐 **MIT License**（最宽松，允许商用）。已在项目根目录创建 `LICENSE` 文件。

## 后续维护建议

- 定期更新 `source_configs.json` 中失效的 RSS 源
- 关注新兴平台（Ozon 俄罗斯、Coupang 韩国等）
- 收集用户反馈优化评分规则（`event_scorer.py`）
- 考虑添加邮件/企业微信通知渠道
