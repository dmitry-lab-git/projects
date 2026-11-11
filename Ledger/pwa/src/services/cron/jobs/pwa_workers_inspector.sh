#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/home/fujitsu-u745/Projects/core/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pwa_workers_inspector_$(date +%Y-%m-%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск pwa_workers_inspector..." >> "$LOG_FILE"
/home/fujitsu-u745/Projects/core/venv/bin/python "$SCRIPT_DIR/pwa_workers_inspector.py" >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инспекция и отправка отчета завершены." >> "$LOG_FILE"
