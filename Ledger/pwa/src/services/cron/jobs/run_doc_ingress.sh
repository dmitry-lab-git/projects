#!/bin/bash
set -e

LOCK_FILE="/tmp/doc_ingress_hub.lock"
LOG_DIR="/home/fujitsu-u745/Projects/core/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/doc_ingress_$(date +%Y-%m-%d).log"

# Защита от наложения запусков: если предыдущий прогон еще идет, тихо выходим
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] Пропуск: предыдущий процесс doc_ingress_hub еще активен." >> "$LOG_FILE"; exit 0; }

echo "==========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Старт doc_ingress_hub" >> "$LOG_FILE"

cd /home/fujitsu-u745/Projects/core
/home/fujitsu-u745/Projects/core/venv/bin/python -m doc_ingress_hub.pipeline >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершение doc_ingress_hub" >> "$LOG_FILE"
