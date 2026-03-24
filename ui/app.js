/**
 * Crossborder Risk Radar — Frontend (Python-only UI)
 *
 * 数据契约：
 * 页面只消费 ui/radar-data.js 里的 window.RADAR_UI_DATA。
 * 这份静态 payload 由 Python 刷新脚本生成，前端不再请求 Node backend。
 */

// ========== 全局状态 ==========
let events = [];           // 原始 RadarItem 数组
let normalizedEvents = []; // 排序后的显示数组
let fulfillmentActions = []; // 履约路径 SOP 建议数组
let currentLang = 'zh';
let currentPlatform = 'all';

// 双语字典
const i18nMap = {
  zh: {
    levelText: { high: '严重风险', medium: '警告', low: '提示' },
    riskTypeText: { policy: '政策风险', logistics: '物流异动', tariff: '税务关税', environment: '合规准入', compliance: '合规准入', platform_rule: '平台动态', platform: '平台动态', platform_policy: '平台政策', customs: '税务关税' },
    empty_global: '大盘平安，暂无宏观风险！',
    empty_platform: '该专属视角暂未命中相关风险，恭喜平安！',
    last_fetched: '最后抓取于：',
    assign: '@ 指派业务员',
    news_source: '新闻来源: ',
    impact: '⚡ 核心影响',
    group: '👤 波及群体',
    metrics_total: '预警总数',
    metrics_high: '需紧急响应'
  },
  en: {
    levelText: { high: 'Critical', medium: 'Warning', low: 'Notice' },
    riskTypeText: { policy: 'Policy Risk', logistics: 'Logistics', tariff: 'Tariff & Tax', environment: 'Compliance', compliance: 'Compliance', platform_rule: 'Platform Policy', platform: 'Platform News', platform_policy: 'Platform Policy' },
    empty_global: 'Dashboard clear. No macro risks detected!',
    empty_platform: 'No specific risks found in this lens. You are safe!',
    last_fetched: 'Last Fetched: ',
    assign: '@ Assign',
    news_source: 'Source: ',
    impact: '⚡ Core Impact',
    group: '👤 Affected Groups',
    metrics_total: 'Total Alerts',
    metrics_high: 'Needs Action'
  }
};

function getDict() { return i18nMap[currentLang]; }

// ========== 工具函数 ==========

function formatDate(value) {
  const date = value ? new Date(value) : new Date();
  return new Intl.DateTimeFormat('zh-CN', {
    month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit',
    timeZone: 'Asia/Shanghai'
  }).format(date);
}

function escapeHtml(value) {
  return String(value ?? '').replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}

/**
 * 将后端 RadarItem 映射为前端渲染所需的扁平字段
 * 这是前后端之间唯一的适配点，集中在一处，不散落在各处
 */
function toDisplayItem(item) {
  return {
    ...item,
    source: item.source || {},
    sourceName: item.source?.name || '系统监测',
    sourceUrl: item.source?.url || '#',
    platform: Array.isArray(item.platforms) ? item.platforms.join(' / ') : (item.platforms || '多平台波及'),
    type_raw: item.type,
    type: item.typeLabel || getDict().riskTypeText[item.type] || item.type || '未分类',
    region: Array.isArray(item.regions) ? item.regions.join(' / ') : (item.regions || '全球'),
    seller_angle: item.impact,
    display_order: item.display_order ?? item.brief_rank ?? 999,
  };
}

function summarizeRiskTypes() {
  const categories = [
    { key: 'logistics', label: '物流异动' },
    { key: 'compliance', label: '合规准入' },
    { key: 'tariff', label: '税务关税' },
    { key: 'platform', label: '平台动态' }
  ];
  const aggregatedMap = { logistics: 0, compliance: 0, tariff: 0, platform: 0 };
  
  if (!normalizedEvents || normalizedEvents.length === 0) {
    return categories.map(c => ({ ...c, count: 0 }));
  }

  normalizedEvents.forEach((item) => {
    const key = mapToDimension(item);
    aggregatedMap[key]++;
  });

  return categories.map(c => ({
    ...c,
    count: aggregatedMap[c.key] || 0
  }));
}

// 公共维度路由：将事件映射到5个雷达维度之一
// policy 类型包含：政府政策（归政策风险）和平台专属政策（归平台动态）
const PLATFORM_KEYWORDS = ['amazon', 'tiktok', 'temu', 'shopee', 'ebay', 'walmart', 'shein', 'lazada'];
function mapToDimension(item) {
  const type = item.type_raw || 'policy';
  if (['platform_rule'].includes(type)) return 'platform';
  if (['logistics'].includes(type)) return 'logistics';
  if (['compliance', 'environment'].includes(type)) return 'compliance';
  if (['tariff', 'customs'].includes(type)) return 'tariff';
  if (type === 'platform') return 'platform';
  // policy 类型：如果是特定平台专属事件，归为平台动态；否则归为政策风险
  if (type === 'policy') {
    const plat = (item.platform || '').toLowerCase();
    if (plat && plat !== '跨境通用' && PLATFORM_KEYWORDS.some(kw => plat.includes(kw))) {
      return 'platform';
    }
    return 'policy';
  }
  return 'policy';
}

// 全局筛选状态
const filterState = { platform: 'all', type: 'all', severity: 'all' };


// ==== UI Component Renderers ====

function getCardTags(item) {
  const tagColor = item.level === 'high' ? 'tag-red' : (item.level === 'medium' ? 'tag-orange' : 'tag-green');
  
  let timeStr = '';
  if (item.timestamp) {
     const t = new Date(item.timestamp);
     const dateStr = t.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', year: 'numeric' });
     if (item.category === 'macro') {
        let policyTimeInfo = `监测始于 ${dateStr}`;
        if (item.effective_date) {
          const effDate = new Date(item.effective_date);
          const effStr = effDate.toLocaleDateString('zh-CN', { year: 'numeric', month: 'short', day: 'numeric' });
          const now = new Date();
          if (effDate > now) {
            policyTimeInfo += ` → 政策将于 ${effStr} 生效`;
          } else {
            policyTimeInfo += ` → 已生效`;
          }
        }
        timeStr = `<span class="tag tag-gray" style="background:var(--state-blue-bg);color:var(--state-blue-text); border:1px solid var(--state-blue);">${policyTimeInfo}</span>`;
     } else {
        timeStr = `<span class="tag tag-gray">${dateStr} 发布</span>`;
     }
  }

  return `
    <div class="prop-tags">
      <span class="tag tag-gray">${escapeHtml(item.platform)}</span>
      <span class="tag ${tagColor}">${escapeHtml(getDict().levelText[item.level])}</span>
      <span class="tag tag-gray">${escapeHtml(item.type)}</span>
      <span class="tag tag-gray">${escapeHtml(item.region)}</span>
      ${timeStr}
    </div>
  `;
}

// 精简卡片：雷达页用（标题+风险级别+来源，紧凑布局）
function renderCompactCard(item) {
  const levelColors = { high: '#DC2626', medium: '#EA580C', low: '#6B7280' };
  const levelBgs = { high: 'rgba(220,38,38,0.08)', medium: 'rgba(234,88,12,0.08)', low: 'rgba(107,114,128,0.06)' };
  const levelLabel = getDict().levelText[item.level] || item.level;
  const color = levelColors[item.level] || '#6B7280';
  const bg = levelBgs[item.level] || 'rgba(107,114,128,0.06)';

  const impact = item.impact || item.summary || '';
  const shortImpact = impact.length > 80 ? impact.slice(0, 80) + '…' : impact;

  return `
    <div style="background:var(--glass);border:1px solid var(--border-light);border-radius:8px;padding:12px 16px;transition:box-shadow .15s;cursor:default;"
         onmouseover="this.style.boxShadow='0 2px 8px rgba(0,0,0,0.08)'" onmouseout="this.style.boxShadow='none'">
      <div style="display:flex;align-items:center;gap:12px;">
        <span style="display:inline-block;width:8px;height:8px;border-radius:50%;background:${color};flex-shrink:0;"></span>
        <div style="flex:1;min-width:0;">
          <a href="${item.sourceUrl || '#'}" target="_blank" rel="noopener noreferrer"
             style="font-size:0.875rem;font-weight:600;color:var(--text-main);text-decoration:none;display:block;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;"
             onmouseover="this.style.color='#2563EB'" onmouseout="this.style.color='var(--text-main)'"
             title="${escapeHtml(item.title)}">${escapeHtml(item.title)}</a>
          <div style="display:flex;align-items:center;gap:6px;margin-top:4px;flex-wrap:wrap;">
            <span style="font-size:0.7rem;background:${bg};color:${color};padding:1px 6px;border-radius:4px;font-weight:600;">${levelLabel}</span>
            <span style="font-size:0.7rem;color:var(--text-muted);">${escapeHtml(item.platform)}</span>
            <span style="font-size:0.7rem;color:var(--text-light);">· ${escapeHtml(item.sourceName || '')}</span>
          </div>
        </div>
      </div>
      ${shortImpact ? `<div style="font-size:0.78rem;color:var(--text-muted);margin-top:8px;padding-left:20px;line-height:1.5;">${escapeHtml(shortImpact)}</div>` : ''}
    </div>
  `;
}

// 纯净版：大盘专属（无 Checklist）
function renderBasicCard(item) {
  const icons = {
    high: '<svg class="issue-icon icon-high" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
    medium: '<svg class="issue-icon icon-medium" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    low: '<svg class="issue-icon icon-low" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
  };

  return `
    <div class="issue-card" data-level="${item.level}">
      <div class="issue-indicator">${icons[item.level] || icons.low}</div>
      <div class="issue-main">
        <div class="issue-head" style="display:flex; align-items:center; flex-wrap:wrap; gap:8px;">
          <h3 class="issue-title" style="margin:0;">
            <a href="${item.sourceUrl || '#'}" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${escapeHtml(item.title)}</a>
          </h3>
          <a href="${item.sourceUrl || '#'}" target="_blank" rel="noopener noreferrer" style="font-size:0.7rem; color:var(--text-muted); text-decoration:none; background:rgba(0,0,0,0.03); padding:2px 6px; border-radius:4px; white-space:nowrap; display:inline-flex; align-items:center; gap:4px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
            ${escapeHtml(item.sourceName)}
          </a>
          <button type="button" class="insight-trigger-link" data-title="${escapeHtml(item.title)}" data-angle="${escapeHtml(item.seller_angle || item.impact || '暂无详细评述')}" data-url="${item.sourceUrl || '#'}" data-source="${escapeHtml(item.sourceName || '')}" style="border:none;background:rgba(37,99,235,0.08);color:#2563EB;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:600;cursor:pointer;">
            AI解读
          </button>
        </div>
        ${getCardTags(item)}
        <div class="meta-table">
          <span class="meta-key impact-key">${getDict().impact}</span>
          <span class="meta-val font-medium text-orange">${escapeHtml(item.impact)}</span>
        </div>
      </div>
    </div>
  `;
}

// 行动版：专属视图（带 Checklist 和深入动作）
function renderActionCard(item) {
  const icons = {
    high: '<svg class="issue-icon icon-high" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>',
    medium: '<svg class="issue-icon icon-medium" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>',
    low: '<svg class="issue-icon icon-low" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>'
  };

  return `
    <div class="issue-card" data-level="${item.level}">
      <div class="issue-indicator">${icons[item.level] || icons.low}</div>
      <div class="issue-main">
        <div class="issue-head" style="display:flex; align-items:flex-start; justify-content:space-between; gap:12px;">
          <div style="display:flex; align-items:center; flex-wrap:wrap; gap:8px;">
            <h3 class="issue-title" style="margin:0;">
              <a href="${item.sourceUrl || '#'}" target="_blank" rel="noopener noreferrer" style="color:inherit;text-decoration:none;" onmouseover="this.style.textDecoration='underline'" onmouseout="this.style.textDecoration='none'">${escapeHtml(item.title)}</a>
            </h3>
            <a href="${item.sourceUrl || '#'}" target="_blank" rel="noopener noreferrer" style="font-size:0.7rem; color:var(--text-muted); text-decoration:none; background:rgba(0,0,0,0.03); padding:2px 6px; border-radius:4px; white-space:nowrap; display:inline-flex; align-items:center; gap:4px;">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="10" height="10"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
              ${escapeHtml(item.sourceName)}
            </a>
            <button type="button" class="insight-trigger-link" data-title="${escapeHtml(item.title)}" data-angle="${escapeHtml(item.seller_angle || item.impact || '暂无详细评述')}" data-url="${item.sourceUrl || '#'}" data-source="${escapeHtml(item.sourceName || '')}" style="border:none;background:rgba(37,99,235,0.08);color:#2563EB;padding:3px 8px;border-radius:999px;font-size:0.72rem;font-weight:600;cursor:pointer;">
              AI解读
            </button>
            ${item.level === 'high'
              ? '<span style="font-size:0.7rem; color: #DC2626; background: rgba(220, 38, 38, 0.1); padding: 2px 6px; border-radius: 4px; font-weight: 600;">SLA: 要求 4h 内响应</span>'
              : item.level === 'medium'
                ? '<span style="font-size:0.7rem; color: #D97706; background: rgba(217, 119, 6, 0.1); padding: 2px 6px; border-radius: 4px; font-weight: 600;">SLA: 建议 24h 内关注</span>'
                : ''}
          </div>
          <button class="btn btn-ghost" style="padding:4px 8px;font-size:0.75rem; white-space:nowrap; flex-shrink:0;">${getDict().assign}</button>
        </div>
        ${getCardTags(item)}
        
        <div class="meta-table" style="background: #F9FAFB; padding: 12px; border-radius: 8px; margin-top: 8px; border: 1px solid #F3F4F6;">
          <span class="meta-key">${getDict().group}</span>
          <span class="meta-val impact-subject" style="font-weight: 500;">${escapeHtml(item.subject)}</span>
          
          <span class="meta-key">风险研判</span>
          <span class="meta-val" style="color: #4B5563; font-size: 0.85rem;">${escapeHtml(item.impact || '该事件对当前经营模型可能有直接的链路阻断或成本挤压作用。')}</span>
        </div>

        <div class="action-box">
          <label class="checklist-item">
            <input type="checkbox" class="cb-input" />
            <span class="cb-custom"></span>
            <span class="cb-text">${escapeHtml(item.action || '核实该政策具体执行细则，评估对 SKU 成本的影响。')}</span>
          </label>
        </div>
      </div>
    </div>
  `;
}

function renderPathsSection() {
  const icons = {
    'crossborder-direct-mail': { emoji: '✈️', color: '#DC2626', label: '跨境直发' },
    'local-fulfillment-platform-led': { emoji: '🏬', color: '#2563EB', label: '平台仓配（FBA/半托管）' },
    'local-fulfillment-merchant-led': { emoji: '📦', color: '#EA580C', label: '自营仓配（3PL/海外仓）' }
  };

  return fulfillmentActions.map(path => {
    const key = path.path_key || '';
    const meta = icons[key] || { emoji: '📋', color: '#6B7280', label: '通用' };
    const desc = path.path_description || '';
    const actions = path.actions || [];
    const watchouts = path.watchouts || [];

    // 行动项列表
    const actionsHtml = actions.map((a, i) => `
      <li style="padding:6px 0; border-bottom:1px solid var(--border-light); display:flex; gap:8px; align-items:flex-start;">
        <span style="flex-shrink:0; width:18px; height:18px; border-radius:50%; background:${meta.color}12; color:${meta.color}; font-size:0.7rem; display:flex; align-items:center; justify-content:center; font-weight:700; margin-top:2px;">${i + 1}</span>
        <span style="font-size:0.8rem; color:var(--text-main); line-height:1.5;">${escapeHtml(a)}</span>
      </li>
    `).join('');

    // 注意事项
    const watchoutsHtml = watchouts.length > 0 ? `
      <div style="margin-top:12px; padding:10px 12px; background:rgba(234,179,8,0.06); border:1px solid rgba(234,179,8,0.2); border-radius:6px;">
        <div style="font-size:0.75rem; font-weight:600; color:#CA8A04; margin-bottom:6px; display:flex; align-items:center; gap:4px;">
          ⚠️ 关键注意事项
        </div>
        <ul style="list-style:none; padding:0; margin:0;">
          ${watchouts.map(w => `<li style="font-size:0.78rem; color:var(--text-main); padding:3px 0; display:flex; gap:6px; line-height:1.4;">
            <span style="color:#CA8A04; flex-shrink:0;">•</span>${escapeHtml(w)}
          </li>`).join('')}
        </ul>
      </div>
    ` : '';

    return `
      <details class="accordion-item" data-path="${escapeHtml(key)}" style="border:1px solid var(--border-light); border-radius:8px; margin-bottom:8px; overflow:hidden;">
        <summary class="accordion-summary" style="padding:12px 16px; cursor:pointer; display:flex; align-items:center; justify-content:space-between; gap:12px; background:var(--glass);">
          <div style="display:flex; align-items:center; gap:10px; flex:1;">
            <span style="font-size:1.2rem;">${meta.emoji}</span>
            <div>
              <div style="font-weight:600; font-size:0.875rem; color:${meta.color};">${escapeHtml(path.path_label || '未分类路径')}</div>
              <div style="font-size:0.75rem; color:var(--text-muted); margin-top:2px;">${escapeHtml(desc)}</div>
            </div>
          </div>
          <div style="display:flex; align-items:center; gap:8px;">
            <span style="font-size:0.7rem; background:${meta.color}12; color:${meta.color}; padding:2px 8px; border-radius:12px; font-weight:600;">${actions.length} 项行动</span>
            <svg class="acc-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M6 9l6 6 6-6"></path></svg>
          </div>
        </summary>
        <div class="accordion-content" style="padding:12px 16px; border-top:1px solid var(--border-light);">
          <div style="font-size:0.75rem; font-weight:600; color:var(--text-muted); margin-bottom:8px; text-transform:uppercase; letter-spacing:0.05em;">📋 行动清单</div>
          <ul style="list-style:none; padding:0; margin:0;">
            ${actionsHtml}
          </ul>
          ${watchoutsHtml}
        </div>
      </details>
    `;
  }).join('');
}

// Render "今日行动项" - Top 3 actions
function renderActionItems() {
  // Get top 3 events sorted by severity
  const topEvents = normalizedEvents.slice(0, 3);

  if (topEvents.length === 0) {
    document.getElementById('action-items-list').innerHTML = '<div class="action-item-empty">暂无待处理事项</div>';
    return;
  }

  const html = topEvents.map((item, index) => {
    const levelIcon = item.level === 'high' ? '🔴' : (item.level === 'medium' ? '🟠' : '🟢');
    return `
      <div class="action-item">
        <div class="action-item-number">${index + 1}</div>
        <div class="action-item-content">
          <div class="action-item-title">${escapeHtml(item.title)}</div>
          <div class="action-item-meta">
            <span class="action-level-badge ${item.level === 'high' ? 'level-high' : (item.level === 'medium' ? 'level-medium' : 'level-low')}">${levelIcon} ${getDict().levelText[item.level]}</span>
            <span class="action-item-subject">→ ${escapeHtml(item.subject)}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  document.getElementById('action-items-list').innerHTML = html;
}

let currentMacroFilter = null;

function applyMacroFilter(label) {
  currentMacroFilter = (currentMacroFilter === label) ? null : label;
  renderGlobalDashboard();

  // 视觉反馈
  document.querySelectorAll('.legend-item').forEach(el => el.style.opacity = '1');
  if (currentMacroFilter) {
    document.querySelectorAll('.legend-item').forEach(el => {
      if (!el.textContent.includes(currentMacroFilter)) el.style.opacity = '0.3';
    });

    // 平滑跳转到对应维度区域
    const labelToKey = {};
    const dict = getDict();
    Object.entries(dict.riskTypeText || {}).forEach(([k, v]) => { labelToKey[v] = k; });
    const dimKey = labelToKey[currentMacroFilter] || 'policy';
    const targetGrid = document.getElementById(`dim-${dimKey}-grid`);
    if (targetGrid) {
      targetGrid.closest('section')?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  }
}

// 渲染全局大盘视图 — 按雷达图5维度分拣（政策风险/物流异动/合规准入/税务关税/平台动态）
function renderGlobalDashboard() {
  const dimGrid = document.getElementById('dim-policy-grid');
  if (!dimGrid) return;

  // 排除宏观事件（宏观政策只在工作区展示）
  let filtered = normalizedEvents.filter(e => e.category !== 'macro');

  // 雷达图点击筛选
  if (currentMacroFilter) {
    filtered = filtered.filter(e => {
      const dimKey = mapToDimension(e);
      const label = getDict().riskTypeText[dimKey] || dimKey;
      return label === currentMacroFilter;
    });
  }

  // 按公共维度路由分拣到4个维度
  const buckets = { logistics: [], compliance: [], tariff: [], platform: [] };
  filtered.forEach(e => {
    const key = mapToDimension(e);
    if (buckets[key]) buckets[key].push(e);
  });

  // 每个维度内按风险级别排序
  const levelOrder = { high: 0, medium: 1, low: 2 };
  Object.values(buckets).forEach(arr => arr.sort((a, b) => (levelOrder[a.level] || 3) - (levelOrder[b.level] || 3)));

  const emptyMsg = '<div style="padding:24px; text-align:center; color:var(--text-light); font-size:0.875rem;">该维度暂无事件</div>';
  document.getElementById('dim-logistics-grid').innerHTML = buckets.logistics.map(e => renderCompactCard(e)).join('') || emptyMsg;
  document.getElementById('dim-compliance-grid').innerHTML = buckets.compliance.map(e => renderCompactCard(e)).join('') || emptyMsg;
  document.getElementById('dim-tariff-grid').innerHTML = buckets.tariff.map(e => renderCompactCard(e)).join('') || emptyMsg;
  document.getElementById('dim-platform-grid').innerHTML = buckets.platform.map(e => renderCompactCard(e)).join('') || emptyMsg;

  const totalRendered = filtered.length;
  const highCount = filtered.filter(e => e.level === 'high').length;
  const countBadge = document.getElementById('alert-count-badge');
  if (countBadge) countBadge.textContent = totalRendered;

  const isGlobalActive = document.getElementById('view-global')?.classList.contains('active-view');
  if (isGlobalActive) {
    const kpiTotal = document.getElementById('kpi-total-val');
    const kpiHigh = document.getElementById('kpi-high-val');
    if (kpiTotal) kpiTotal.textContent = totalRendered;
    if (kpiHigh) kpiHigh.textContent = highCount;
  }
}

// 渲染工作区视图：顶部宏观政策 + 平台专属事件
function applyPlatformFilters() {
  // 1. 宏观政策区域（独立于平台筛选）
  const macroEvents = normalizedEvents.filter(e => e.category === 'macro');
  const macroGrid = document.getElementById('workspace-macro-grid');
  if (macroGrid) {
    // 已生效的政策降至底部
    const now = new Date();
    const sorted = [...macroEvents].sort((a, b) => {
      const aEff = a.effective_date ? new Date(a.effective_date) : null;
      const bEff = b.effective_date ? new Date(b.effective_date) : null;
      const aActive = aEff && aEff <= now ? 1 : 0;
      const bActive = bEff && bEff <= now ? 1 : 0;
      return aActive - bActive;
    });
    macroGrid.innerHTML = sorted.map(e => renderBasicCard(e)).join('') ||
      '<div style="padding:24px; text-align:center; color:var(--text-light); font-size:0.875rem;">暂无宏观政策监控项</div>';
  }

  // 2. 平台专属事件（排除宏观）
  let filtered = normalizedEvents
    .filter(e => {
      if (e.category === 'macro') return false;
      if (currentPlatform === 'all') return true;
      const target = currentPlatform.toLowerCase();
      if (Array.isArray(e.platforms)) {
        return e.platforms.some(p => p.toLowerCase().includes(target));
      }
      return String(e.platform || '').toLowerCase().includes(target);
    });

  // 按风险级别排序
  const levelOrder = { high: 0, medium: 1, low: 2 };
  filtered.sort((a, b) => {
    const aScope = a.scope === 'platform' ? 0 : 1;
    const bScope = b.scope === 'platform' ? 0 : 1;
    if (aScope !== bScope) return aScope - bScope;
    return (levelOrder[a.level] || 3) - (levelOrder[b.level] || 3);
  });

  const eventsHtml = filtered.slice(0, 50).map(e => renderActionCard(e)).join('');
  const eventsGrid = document.getElementById('platform-events-grid');
  if (eventsGrid) {
    eventsGrid.innerHTML = eventsHtml || '<div style="padding:40px; text-align:center; color:var(--text-light)">该平台暂无专属事件</div>';
  }

  const badge = document.getElementById('alert-count-platform');
  if (badge) badge.textContent = filtered.length;

  // 注入全链路 SOP 急救包
  const sopContainer = document.getElementById('tk-deep-grid-container');
  if (sopContainer) {
    const sopHtml = renderPathsSection();
    sopContainer.innerHTML = sopHtml || '<div class="text-muted text-xs p-4">暂无针对当前视角的专项 SOP</div>';
  }
}

// ==== Chart & Layout Init ====

function initChart() {
  if (typeof Chart === 'undefined') {
    console.warn('Chart.js not loaded');
    return;
  }
  const dist = summarizeRiskTypes();
  const colors = { policy: '#DC2626', logistics: '#EA580C', compliance: '#8B5CF6', environment: '#8B5CF6', tariff: '#CA8A04', customs: '#CA8A04', platform: '#2563EB', platform_rule: '#2563EB' };

  // Custom Legend HTML
  const legendHtml = dist.map(d => {
    const c = colors[d.key] || '#9CA3AF';
    return `
      <div class="legend-item" style="cursor: pointer;" onclick="applyMacroFilter('${escapeHtml(d.label)}')">
        <div class="legend-key"><div class="legend-dot" style="background:${c}"></div>${escapeHtml(d.label)}</div>
        <div class="legend-val">${d.count}</div>
      </div>
    `;
  }).join('');
  document.getElementById('distribution-pills').innerHTML = legendHtml;

  // Chart
  const ctx = document.getElementById('macroRiskChart').getContext('2d');
  new Chart(ctx, {
    type: 'radar',
    data: {
      labels: dist.map(d => d.label),
      datasets: [{
        data: dist.map(d => d.count),
        backgroundColor: 'rgba(99, 102, 241, 0.15)',
        borderColor: 'rgba(99, 102, 241, 0.6)',
        borderWidth: 2,
        pointBackgroundColor: dist.map(d => colors[d.key] || '#9CA3AF'),
        pointBorderColor: '#fff',
        pointBorderWidth: 2,
        pointRadius: 5,
        pointHoverRadius: 7,
        hoverOffset: 4
      }]
    },
    options: {
      onClick: (e, elements) => {
        if (elements.length > 0) {
          const index = elements[0].index;
          const label = dist[index].label;
          applyMacroFilter(label);
        } else {
          // 点击空白区域清除筛选
          currentMacroFilter = null;
          renderGlobalDashboard();
          document.querySelectorAll('.legend-item').forEach(el => el.style.opacity = '1');
        }
      },
      onHover: (event, chartElement) => {
        event.native.target.style.cursor = chartElement[0] ? 'pointer' : 'default';
      },
      responsive: true, maintainAspectRatio: false,
      scales: {
        r: {
          angleLines: { display: true, color: 'rgba(0,0,0,0.05)' },
          grid: { color: 'rgba(0,0,0,0.05)' },
          suggestedMin: 0,
          ticks: { display: false }
        }
      },
      plugins: {
        legend: { display: false },
        tooltip: {
          backgroundColor: '#111827', titleColor: '#fff', bodyColor: '#F3F4F6',
          padding: 8, cornerRadius: 4, displayColors: true
        }
      }
    }
  });
}

function initMetrics() {
  const total = normalizedEvents.length || events.length;
  const highRisk = (normalizedEvents.length ? normalizedEvents : events).filter(e => (e.level || e.risk_level) === 'high').length;

  const html = `
    <div class="metric-item">
      <span class="metric-label">${getDict().metrics_total}</span>
      <span class="metric-val text-blue" id="kpi-total-val">${total}</span>
    </div>
    <div class="metric-item">
      <span class="metric-label">${getDict().metrics_high}</span>
      <span class="metric-val ${highRisk > 0 ? 'text-red' : ''}" id="kpi-high-val">${highRisk}</span>
    </div>
  `;
  document.getElementById('kpi-metrics-row').innerHTML = html;
  document.getElementById('alert-count-badge').textContent = total;
}

function applyLanguageUI() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (getDict()[key]) el.textContent = getDict()[key];
  });
}

/**
 * 初始化数据 - Python 静态产物唯一入口
 */
async function initData() {
  const payload = window.RADAR_UI_DATA;
  if (!payload || !Array.isArray(payload.events)) {
    throw new Error('RADAR_UI_DATA missing or invalid');
  }

  events = payload.events;
  fulfillmentActions = Array.isArray(payload.fulfillment_actions) ? payload.fulfillment_actions : [];

  const updEl = document.getElementById('last-updated-text');
  if (updEl) {
    const generatedAt = payload.meta?.generated_at;
    updEl.textContent = generatedAt ? `最新抓取于：${formatDate(generatedAt)}` : '已加载 Python 雷达快照';
  }

  applyLanguageUI();

  normalizedEvents = events
    .map(toDisplayItem)
    .sort((a, b) => {
      const catOrder = { macro: 0, urgent: 1, daily: 2 };
      const catDiff = (catOrder[a.category] ?? 3) - (catOrder[b.category] ?? 3);
      if (catDiff !== 0) return catDiff;
      const orderDiff = (a.display_order ?? 999) - (b.display_order ?? 999);
      if (orderDiff !== 0) return orderDiff;
      const levelOrder = { high: 0, medium: 1, low: 2 };
      return (levelOrder[a.level] ?? 3) - (levelOrder[b.level] ?? 3);
    });

  initMetrics();
  renderGlobalDashboard();
  if (document.getElementById('platform-front-door-grid')) applyPlatformFilters();
  initChart();
}

async function init() {
  await initData();
  document.getElementById('platform-switch')?.addEventListener('change', (e) => {
    currentPlatform = e.target.value;
    applyPlatformFilters();
  });
}

// -- Source View Modal Injection --
window.openNewsModal = function (title, angle, url, sourceName) {
  let modalDom = document.getElementById('globalNewsModal');
  if (!modalDom) {
    modalDom = document.createElement('div');
    modalDom.id = 'globalNewsModal';
    modalDom.style = 'position:fixed;top:0;left:0;width:100vw;height:100vh;background:rgba(0,0,0,0.5);display:flex;align-items:center;justify-content:center;z-index:9999;backdrop-filter:blur(4px);';
    document.body.appendChild(modalDom);
  }

  modalDom.innerHTML = `
    <div style="background:#fff; width:650px; max-height:85vh; border-radius:12px; box-shadow:0 20px 40px rgba(0,0,0,0.2); display:flex; flex-direction:column; overflow:hidden;">
      <div style="padding:20px 24px; border-bottom:1px solid #E5E7EB; display:flex; justify-content:space-between; align-items:center; background:#F9FAFB;">
        <div style="display:flex; align-items:center; gap:8px;">
          <span style="background:#2563EB; color:#fff; font-size:12px; font-weight:bold; padding:4px 8px; border-radius:4px;">内部溯源快照</span>
          <span style="color:#6B7280; font-size:13px;">信源解析完成</span>
        </div>
        <button onclick="document.getElementById('globalNewsModal').style.display='none'" style="border:none; background:none; font-size:24px; color:#9CA3AF; cursor:pointer; padding:0; line-height:1;">&times;</button>
      </div>
      <div style="padding:24px; overflow-y:auto; flex:1;">
        <h2 style="margin:0 0 16px 0; font-size:1.2rem; color:#111827; line-height:1.4;">${escapeHtml(title)}</h2>
        <div style="margin-bottom:24px; font-size:0.875rem; color:#6B7280; display:flex; gap:16px;">
          <span>抓取源: ${escapeHtml(sourceName)}</span>
          <a href="${escapeHtml(url)}" target="_blank" style="color:#2563EB; text-decoration:none;">查看原始页面 &nearr;</a>
        </div>
        
        <div style="background:#F3F4F6; border-left:4px solid #F59E0B; padding:16px; border-radius:4px; margin-bottom:24px;">
          <h4 style="margin:0 0 8px 0; color:#92400E; font-size:0.9rem; display:flex; align-items:center; gap:6px;">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            雷达智能洞察 (Seller Angle)
          </h4>
          <p style="margin:0; font-size:0.95rem; color:#374151; line-height:1.6;">${escapeHtml(angle)}</p>
        </div>
      </div>
    </div>
  `;
  modalDom.style.display = 'flex';
};

// Global Event Listeners for Checklist
document.addEventListener('change', (e) => {
  if (e.target.matches('.cb-input')) {
    const parent = e.target.closest('.issue-card');
    const chk = e.target.closest('.checklist-item');
    if (e.target.checked) {
      chk.classList.add('completed');
      if (parent) parent.style.opacity = '0.7'; // 弱化整个卡片
    } else {
      chk.classList.remove('completed');
      if (parent) parent.style.opacity = '1';
    }
  }
});

// Navigation logic
function switchView(viewId) {
  // Update navs
  document.querySelectorAll('.nav-item').forEach(nav => {
    nav.classList.toggle('active', nav.getAttribute('data-view') === viewId);
  });
  // 同步手机端底部导航
  document.querySelectorAll('.mobile-nav-item').forEach(nav => {
    nav.classList.toggle('active', nav.getAttribute('data-view') === viewId);
  });

  // Update views
  document.querySelectorAll('.page-view').forEach(view => {
    if (view.id === viewId) {
      view.style.display = 'block';
      view.classList.add('active-view');
      // Force trigger layout if needed
      if (viewId === 'view-platform') {
        applyPlatformFilters();
      } else if (viewId === 'view-global') {
        renderGlobalDashboard();
      }
    } else {
      view.style.display = 'none';
      view.classList.remove('active-view');
    }
  });
}

document.querySelectorAll('.nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const viewId = item.getAttribute('data-view');
    if (viewId) switchView(viewId);
  });
});

// 手机端底部导航栏
document.querySelectorAll('.mobile-nav-item').forEach(item => {
  item.addEventListener('click', () => {
    const viewId = item.getAttribute('data-view');
    if (viewId) switchView(viewId);
  });
});

const logo = document.getElementById('nav-brand-logo');
if (logo) {
  logo.addEventListener('click', () => switchView('view-global'));
}

// -- Modal Click Event Delegation --
document.body.addEventListener('click', function (e) {
  // Try to find the closest element with the modal trigger class.
  // This solves the issue where clicking the inner text doesn't trigger if the <a> tag is wrapping it.
  const link = e.target.closest('.insight-trigger-link');
  if (link) {
    e.preventDefault();
    const title = link.getAttribute('data-title');
    const angle = link.getAttribute('data-angle');
    const url = link.getAttribute('data-url');
    const source = link.getAttribute('data-source');
    openNewsModal(title, angle, url, source);
  }
});

// Initialization
init();
