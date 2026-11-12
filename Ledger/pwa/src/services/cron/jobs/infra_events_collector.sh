#!/bin/bash
set -e

# --- WORKER TRACKER ---
PY="/home/fujitsu-u745/Projects/core/venv/bin/python"
TRACKER="/home/fujitsu-u745/Projects/Ledger/pwa/src/services/cron/jobs/worker_tracker.py"
RUN_ID=$($PY "$TRACKER" start "infra_events_collector" --trigger "SCHEDULED")
trap 'RC=$?; [ $RC -eq 0 ] && ST="SUCCESS" || ST="FAILED"; $PY "$TRACKER" finish "$RUN_ID" --status "$ST" --code $RC' EXIT
# ----------------------

LOCK_FILE="/tmp/infra_events_collector.lock"
LOG_DIR="/home/fujitsu-u745/Projects/core/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/infra_events_collector_$(date +%Y-%m-%d).log"

exec 200>"$LOCK_FILE"
flock -n 200 || {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Пропуск: предыдущий процесс infra_events_collector еще активен." >> "$LOG_FILE"
    $PY "$TRACKER" finish "$RUN_ID" --status "SKIPPED" --code 0
    trap - EXIT
    exit 0
}

echo "[$(date '+%Y-%m-%d %H:%M:%S')] Старт infra_events_collector" >> "$LOG_FILE"
cd /home/fujitsu-u745/Projects/Ledger/pwa
$PY -m src.services.cron.jobs.infra_events_collector >> "$LOG_FILE" 2>&1
echo "[$(date '+%Y-%m-%d %H:%M:%S')] Завершение infra_events_collector" >> "$LOG_FILE"
