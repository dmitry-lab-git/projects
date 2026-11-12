#!/bin/bash
set -e

# --- WORKER TRACKER ---
PY="/home/fujitsu-u745/Projects/core/venv/bin/python"
TRACKER="/home/fujitsu-u745/Projects/Ledger/pwa/src/services/cron/jobs/worker_tracker.py"
RUN_ID=$($PY "$TRACKER" start "archive_untouchable" --trigger "SCHEDULED")
trap 'RC=$?; [ $RC -eq 0 ] && ST="SUCCESS" || ST="FAILED"; $PY "$TRACKER" finish "$RUN_ID" --status "$ST" --code $RC' EXIT
# ----------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_FILE="$SCRIPT_DIR/schedule.conf"
if [ -f "$CONF_FILE" ]; then source "$CONF_FILE"; fi

echo "=== ЗАПУСК АРХИВАЦИИ НЕПРИКАСАЕМЫХ ФАЙЛОВ ==="
mkdir -p "$ARCHIVE_DIR"

FLAG_FILE="$SCRIPT_DIR/archive_success.flag"
rm -f "$FLAG_FILE"

FILES_MOVED=0

# Находим файлы за Понедельник и перемещаем
while IFS= read -r file; do
    [ -z "$file" ] && continue
    echo "Перенос файла в долгосрочный архив: $(basename "$file")"
    mv -f "$file" "$ARCHIVE_DIR/"
    FILES_MOVED=1
done < <(find "$MAIN_BACKUP_DIR" -maxdepth 1 -type f -name "*_Mon.*")

echo "Архивация успешно выполнена: $(date)" > "$FLAG_FILE"
echo "Квитанция создана: $FLAG_FILE, перенесено: $FILES_MOVED"
