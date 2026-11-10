# Eco-Service ERP

ERP-система учета отходов. Каждый мешок получает паспорт и QR-код. Система знает откуда мешок, кто его привез, сколько весит и на что разобран.

### Структура проекта (как у тебя в `~/Projects/eco_service`)
eco_service/
├── ddl/                           # Структура БД
│   ├── full_schema_auroville_eco_service.sql  # Вся база в одном файле
│   ├── 00_extensions_postgis.sql  # PostGIS
│   ├── 01_dicts.sql               # Справочники
│   ├── 02_infrastructure.sql      # Мешки и события
│   ├── 03_security.sql            # Пользователи и доступ
│   └── 04_analytics.sql           # Витрина отчетов
├── docs/
│   └── DBDD.md                    # Описание всех таблиц
├── app/                           # Код сайта Reflex (PWA)
├── .web/                          # Собранный фронтенд (генерит Reflex)
├── BP.md                          # Бизнес-процесс
├── config.py                      # Настройки pydantic-settings
├── model_config.py                # Pydantic модели
├── database.py                    # Подключение asyncpg
├── security_utils.py              # bcrypt и пароли
├── set_operator_password.py       # Скрипт установки пароля
├── environment_initializer.py     # Сид-движок (генерация тестовых данных)
├── rxconfig.py                    # Конфиг Reflex
├── requirements.txt               # Зависимости Python
├── .states/                       # Состояния Reflex
└── venv/                          # Виртуальное окружение (не коммитится)javascript
База `auroville_eco_service` — 4 схемы: dicts, infrastructure, security, analytics. Таймзона UTC 0.

### Что нужно

**Софт:** Ubuntu / WSL, Python 3.11+, PostgreSQL 13+ с PostGIS, DBeaver.
**Железо для поля:** Принтер Niimbot B1/B21 + рулон влагостойких PET-наклеек для QR. Планшет для сборщика.

Зависимости из `requirements.txt`: reflex>=0.6.0, asyncpg, bcrypt, pydantic, python-dotenv и др.

### Как восстановить базу

Делает IT принимающей стороны один раз. Создается пустая база `auroville_eco_service` и в нее прогоняется `ddl/full_schema_auroville_eco_service.sql`. Все таблицы появятся сами. Проверить в DBeaver — должны быть видны 4 схемы.

### Что такое Reflex PWA и как развернуть

PWA — сайт, который ставится как приложение. Без App Store. Один сайт, три вида:
- Житель (Level 0): заявляет мешок.
- Сборщик/сортировщик (Level 1): отмечает забор, вес, сортировку на планшете.
- Менеджер/CEO (Level 2-3): дашборд с картой и KPI.

**На ПК (черновик):** База и сайт рядом на одном компе. Сайт по адресу localhost, никто извне не видит. Для тестов и печати QR.

**На VPS (боевая для Eco Service):** VPS — комп в интернете 24/7. Туда ставится PostgreSQL, заливается `ddl/full_schema...sql`, заливается код из `app/`, ставятся зависимости из `requirements.txt`, запускается Reflex и прячется за Nginx с доменом и https. После этого все работают по одной ссылке.

Локальный запуск для разработки:
- `source venv/bin/activate`
- `python environment_initializer.py` — чистит базу, заливает справочники и генерит 2 месяца истории.
- `reflex run`

### Что передавать принимающей стороне

Достаточно дать ссылку на репозиторий. Внутри уже все: структура БД в `ddl/`, описание в `docs/DBDD.md`, бизнес-логика в `BP.md`, код сайта в `app/`.