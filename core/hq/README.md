# HQ — Headquarters Core (ex-agent_builder)

Центральный аппарат будущей корпорации. Локальный оркестратор контекстных окон и цифровых сотрудников поверх `api_manager` и PostgreSQL.

> `core/hq` — это столица. Город (`core/city`) вырастет из него.

### Концепция
Вместо тяжелых внешних фреймворков (LangGraph, CrewAI) используем собственных сотрудников. HQ — точка входа в корпорацию, где сидят первые лица.

### Структура HQ
hq/
├── mayor.py            # CEO / Mayor — главный роутер, лобби корпорации
├── context_store.py    # Память HQ: hq.sessions, hq.messages (UUID, tool_calls, billing)
├── departments/
│   ├── ceo/            # CEO — стратегия и роутинг запросов
│   ├── cfo/            # CFO — Ledger, Household, reports.* (только READ ONLY SELECT)
│   ├── cmo/            # CMO — doc_ingress_hub, классификация чеков, staging_transactions
│   └── cso/            # CSO / Security — аудит действий, защита api_manager, контроль кэша
├── blueprints/         # Шаблоны для будущих районов города
└── sandboxes/          # Изолированная сборка модулей до прод-верификации

### Первые лица (v1)
- CEO / Mayor — встречает запрос, делегирует в нужный департамент.
- CFO — отвечает за финансы. Работает только по актуальным DDL из ~/Projects/db/, SELECT по reports.*.
- CMO — маркетинг и документы: doc_ingress_hub -> классификация -> staging.
- CSO — безопасность: проверка audit.workers_registry, логов core/logs/, доступа к processing.api_request_blobs_cache.

### Память HQ (Roadmap v1)
- CREATE SCHEMA hq;
- hq.sessions + hq.messages — история окон, system prompt, tool_calls, токены.
- Context Compaction — суммаризация длинных сессий.
- Мультимодальный кэш — переиспользование api_request_blobs_cache без повторной отправки PDF.

### Конвейер Строителей (Roadmap v2)
- Архитектор: анализ задачи по DDL и графу знаний kernel.nodes/edges.
- Строитель: генерация .py/.sh с телеметрией worker_tracker.py через api_manager.
- Инспектор (QA): py_compile, прогон транзакций с ROLLBACK, подготовка development.version_updates.

### Прикладные сотрудники (Roadmap v3)
- SRE-дежурный: триггер по ALERT_FAILED в reports.v_workers_health.
- Аналитик Ledger: NL-запросы в Reflex PWA -> безопасный SELECT.
- Цепочки: doc_ingress_hub -> CMO -> CFO -> CSO audit.

### Принципы HQ
1. Никакого WRITE кроме hq.* и sandboxes/.
2. Любой SQL только после чтения DDL.
3. Любой код — через py_compile в песочнице.

HQ is the capital. City comes later.