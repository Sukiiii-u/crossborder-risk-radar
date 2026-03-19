#!/bin/bash
# 跨境风险雷达 - 每日自动数据刷新脚本
# 完整管线：抓取数据 → AI分析 → 生成前端数据

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_ROOT="$(dirname "$SCRIPT_DIR")"
SCRIPTS_DIR="$SKILL_ROOT/scripts"
UI_DIR="$SKILL_ROOT/ui"
LOG_DIR="$SKILL_ROOT/runtime/logs"
PYTHON="${PYTHON:-python3}"

mkdir -p "$LOG_DIR"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/daily_refresh_${TIMESTAMP}.log"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG_FILE"
}

log "===== 开始每日数据刷新 ====="

# 步骤1：抓取最新事件
log "步骤1/3：抓取最新事件..."
if $PYTHON "$SCRIPTS_DIR/fetch_real_events.py" >> "$LOG_FILE" 2>&1; then
    log "✅ 事件抓取完成"
else
    log "⚠️ 事件抓取出错（继续执行后续步骤）"
fi

# 步骤2：运行 AI 分析生成 brief
log "步骤2/3：AI 分析与 brief 生成..."
if $PYTHON "$SCRIPTS_DIR/run_radar.py" --format json --output "$SKILL_ROOT/runtime/data/latest_run.json" >> "$LOG_FILE" 2>&1; then
    log "✅ AI 分析完成"
else
    log "⚠️ AI 分析出错（继续执行后续步骤）"
fi

# 步骤3：同步到前端 radar-data.js
log "步骤3/3：同步前端数据..."
if $PYTHON "$UI_DIR/refresh_radar_data.py" >> "$LOG_FILE" 2>&1; then
    log "✅ 前端数据同步完成"
else
    log "⚠️ 前端数据同步出错"
fi

# 清理超过7天的旧日志
find "$LOG_DIR" -name "daily_refresh_*.log" -mtime +7 -delete 2>/dev/null || true

log "===== 每日数据刷新完成 ====="
