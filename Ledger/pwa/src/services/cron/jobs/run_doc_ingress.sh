#!/bin/bash
set -e

# --- WORKER TRACKER ---
PY="/home/fujitsu-u745/Projects/core/venv/bin/python"
TRACKER="/home/fujitsu-u745/Projects/Ledger/pwa/src/services/cron/jobs/worker_tracker.py"
RUN_ID=$($PY "$TRACKER" start "doc_ingress_hub" --trigger "SCHEDULED")
trap 'RC=$?; [ $RC -eq 0 ] && ST="SUCCESS" || ST="FAILED"; $PY "$TRACKER" finish "$RUN_ID" --status "$ST" --code $RC' EXIT
# ----------------------


LOCK_FILE="/tmp/doc_ingress_hub.lock"
LOG_DIR="/home/fujitsu-u745/Projects/core/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/doc_ingress_$(date +%Y-%m-%d).log"

# Защита от наложения запусков: если предыдущий прогон еще идет, тихо выходим
exec 200>"$LOCK_FILE"
flock -n 200 || { echo "[$(date '+%Y-%m-%d %H:%M:%S')] Пропуск: предыдущий процесс doc_ingress_hub еще активен." >> "$LOG_FILE"; $PY "$TRACKER" finish "$RUN_ID" --status "SKIPPED" --code 0; trap - EXIT; exit 0; }

echo "==========================================" >> "$LOG_FILE"
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Старт doc_ingress_hub" >> "$LOG_FILE"

cd /home/fujitsu-u745/Projects/core
/home/fujitsu-u745/Projects/core/venv/bin/python -m doc_ingress_hub.pipeline >> "$LOG_FILE" 2>&1

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершение doc_ingress_hub" >> "$LOG_FILE"
