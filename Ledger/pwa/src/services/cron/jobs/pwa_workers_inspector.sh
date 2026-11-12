#!/bin/bash
set -e

# --- WORKER TRACKER ---
PY="/home/fujitsu-u745/Projects/core/venv/bin/python"
TRACKER="/home/fujitsu-u745/Projects/Ledger/pwa/src/services/cron/jobs/worker_tracker.py"
RUN_ID=$($PY "$TRACKER" start "pwa_workers_inspector" --trigger "SCHEDULED")
trap 'RC=$?; [ $RC -eq 0 ] && ST="SUCCESS" || ST="FAILED"; $PY "$TRACKER" finish "$RUN_ID" --status "$ST" --code $RC' EXIT
# ----------------------


SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="/home/fujitsu-u745/Projects/core/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/pwa_workers_inspector_$(date +%Y-%m-%d).log"

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Запуск pwa_workers_inspector..." >> "$LOG_FILE"
/home/fujitsu-u745/Projects/core/venv/bin/python "$SCRIPT_DIR/pwa_workers_inspector.py" >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Инспекция и отправка отчета завершены." >> "$LOG_FILE"
