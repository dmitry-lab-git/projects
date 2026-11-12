# Фоновые процессы и цифровые сотрудники (`cron/jobs`)

Централизованная директория фоновых воркеров, служб резервного копирования, конвейеров обработки данных и системных инспекторов.

## Архитектура и телеметрия
Все процессы в этой папке подключены к единому **UUID-реестру в PostgreSQL** (БД `ledger`):
* **`audit.workers_registry`** — паспорт каждого цифрового сотрудника, расписание и порог SLA (`max_silence_minutes`).
* **`audit.workers_execution_log`** — журнал каждого запуска по уникальному клиентскому `run_id` (`UUID`), длительность (`duration_ms`), код выхода и JSONB-метрики.
* **`reports.v_workers_health`** — аналитическое представление текущего здоровья всех процессов (`HEALTHY`, `WORKING`, `ALERT_FAILED`, `ALERT_OVERDUE`, `DISABLED`).
* **`worker_tracker.py`** — единый CLI- и Python-модуль телеметрии и дебаунса запусков.

---

## Штат цифровых сотрудников

| Код (`worker_code`) | Точка входа | Движок | Расписание | Назначение |
| :--- | :--- | :--- | :--- | :--- |
| `backup_ledger` | `make_dump.sh` | `CRON` | `0 22 * * *` | Ежедневный бинарный дамп БД `ledger` |
| `backup_household` | `make_dump_household.sh` | `CRON` | `10 22 * * *` | Ежедневный бинарный дамп БД `household` |
| `backup_git` | `make_dump_git.sh` | `CRON` | `20 22 * * *` | Создание `.bundle`-архивов Git-репозиториев |
| `archive_untouchable` | `archive_untouchable.sh` | `CRON` | `40 22 * * *` | Перенос понедельничных копий в долгосрочный архив |
| `clean_and_rotate` | `clean_and_rotate.sh` | `CRON` | `50 22 * * *` | Ротация ежедневных бэкапов старше 7 дней |
| `pwa_workers_inspector` | `pwa_workers_inspector.sh` | `CRON` | `0 21 * * 4` | Еженедельный аудит контуров и отправка акта на почту |
| `doc_ingress_hub` | `run_doc_ingress.sh` | `CRON` | `*/30 * * * *` | Конвейер приема, AI-классификации и разбора документов |
| `dump_schema_versioning` | `db_dump.sh` | `CRON` | По триггеру | Экспорт DDL-схем БД и генерация `VERSIONING.md` |
| `readme_metrics_updater` | `readme_updater.py` | `APSCHEDULER` | `0 0 * * *` | Обновление сводки метрик в корневом `README.md` |
| `pwa_dashboard_metrics` | `metrics_updater.py` | `APSCHEDULER` | Каждые 6 ч | Выгрузка JSON-метрик для Digital Living Room |
| `force_full_backup` | `run_all_now.sh` | `MANUAL` | Вручную | Внеочередной форсированный бэкап всех 3 контуров |
| `infra_events_collector` | `infra_events_collector.sh` | `CRON` | *В разработке* | Единый сборщик событий со всей инфраструктуры (`DRAFT`) |

---

## Служебные файлы и манифесты
* `schedule.conf` / `update_schedule.sh` — конфигурация расписания и генератор системного `crontab`.
* `git_service.py` — сервис безопасного `git commit` и `git push` с ретраями и `pull --rebase`.
* `worker_creation_manifest.txt` — архитектурный контракт и чек-лист создания новых цифровых сотрудников (используется разработчиком и `agent_builder`).
