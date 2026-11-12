#!/bin/bash
set -e

# --- WORKER TRACKER ---
PY="/home/fujitsu-u745/Projects/core/venv/bin/python"
TRACKER="/home/fujitsu-u745/Projects/Ledger/pwa/src/services/cron/jobs/worker_tracker.py"
RUN_ID=$($PY "$TRACKER" start "force_full_backup" --trigger "MANUAL_FORCE")
trap 'RC=$?; [ $RC -eq 0 ] && ST="SUCCESS" || ST="FAILED"; $PY "$TRACKER" finish "$RUN_ID" --status "$ST" --code $RC' EXIT
# ----------------------

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "=== ЗАПУСК ПОЛНОГО ФОРСИРОВАННОГО БЭКАПА ==="

echo "1/3 Выполнение бэкапа БД Ledger..."
/bin/bash "$SCRIPT_DIR/make_dump.sh"

echo "2/3 Выполнение бэкапа БД Household..."
/bin/bash "$SCRIPT_DIR/make_dump_household.sh"

echo "3/3 Выполнение бэкапа Git..."
/bin/bash "$SCRIPT_DIR/make_dump_git.sh"

echo "============================================="
echo "Все процессы успешно принудительно завершены!"

powershell.exe -Command "[System.Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null; [System.Windows.Forms::MessageBox]::Show('ВНЕОЧЕРЕДНОЙ ПОЛНЫЙ БЭКАП ЗАВЕРШЕН! Все 3 архива (Git, Household, Ledger) успешно обновлены и проверены.', 'Ручной бэкап системы', [System.Windows.Forms.MessageBoxButtons]::OK, [System.Windows.Forms.MessageBoxIcon]::Warning)" > /dev/null 2>&1 || true
