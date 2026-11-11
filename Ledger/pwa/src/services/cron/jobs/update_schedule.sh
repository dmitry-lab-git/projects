#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONF_FILE="$SCRIPT_DIR/schedule.conf"

if [ ! -f "$CONF_FILE" ]; then
    echo "ОШИБКА: Файл конфигурации schedule.conf не найден в $SCRIPT_DIR"
    exit 1
fi

source "$CONF_FILE"

# Регистрируем все 7 процессов
(
echo "$TIME_LEDGER * * * /bin/bash $SCRIPT_DIR/make_dump.sh"
echo "$TIME_HOUSEHOLD * * * /bin/bash $SCRIPT_DIR/make_dump_household.sh"
echo "$TIME_GIT * * * /bin/bash $SCRIPT_DIR/make_dump_git.sh"
echo "$TIME_ARCHIVE * * * /bin/bash $SCRIPT_DIR/archive_untouchable.sh"
echo "$TIME_CLEAN * * * /bin/bash $SCRIPT_DIR/clean_and_rotate.sh"
echo "$TIME_INSPECTOR /bin/bash $SCRIPT_DIR/pwa_workers_inspector.sh"
echo "$TIME_DOC_INGRESS /bin/bash $SCRIPT_DIR/run_doc_ingress.sh"
) | crontab -

echo "Расписание CRON успешно обновлено для всех 7 постоянных процессов из $SCRIPT_DIR"
crontab -l
