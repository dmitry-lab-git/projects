# Traffic Tracker (TT)

Система учета трафика, где телефон — главный, а ПК — датчик.

Телефон раздает интернет и считает общий лимит.
ПК не гонит трафик через туннель, а сам отчитывается о себе.
Туннеля нет. Есть только легкий агент-счетчик.

## Архитектура

### 1. TT App (телефон, Android)
Главный сервер, база и экран.

Видит:
- Свой собственный трафик: по приложениям, Wi-Fi / мобильный
- Общий трафик через раздачу
- ПК — только одной цифрой: TOTAL up/down

Не видит:
- Разбивку ПК по приложениям
- Сайты ПК

Считает лимит так:
`Общий = Телефон + ПК (total) + Остальные (разница)`
`Остальные = Раздача (total) - ПК (total)`

### 2. PC Agent (ПК, Python)
Легкий счетчик внутри ПК. Трафик идет как обычно, без туннеля.

Отправляет телефону раз в секунду:
- `device_id: PC`
- `up / down: total`

Хранит у себя локально в SQLite:
- Разбивку по приложениям
- Домены, без истории браузера

### Как ПК узнает сайты без туннеля и без истории
1. Смотрит активные соединения: IP + порт + процесс
2. Сопоставляет IP с доменом через DNS-кэш / обратный DNS
3. Пишет в БД

HTTPS-контент не читается. Виден только домен.
Точность домена на ПК — приблизительная, по DNS-кэшу.

## Что выкинули
- Туннель / VPN между ПК и телефоном
- Зависимость от истории браузера

## Что осталось
- Телефон = сервер + UI + лимит
- ПК = агент + своя локальная детализация

---

## Хранение: household, не ledger

**Storage: household, retention 30 days, no ledger**

Ledger — деньги, неизменяемость, аудит. У нас — телеметрия дома.
Можно агрегировать, чистить, удалять старое. Потеря 1 секунды — не страшно.

- **Оперативное:** SQLite на телефоне и на ПК — для UI и лимита, 30 дней.
- **Архив / Источник правды для истории:** `household.network` в PostgreSQL (WSL) — туда сливается агрегат.

---

## SOURCE OF TRUTH — DB SQL

### 1. БД Телефона (SQLite, Android)

```sql
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    last_seen INTEGER NOT NULL,
    created_at INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS traffic_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    device_id TEXT NOT NULL DEFAULT 'phone',
    app_name TEXT NOT NULL,
    network_type TEXT NOT NULL,
    bytes_up INTEGER NOT NULL DEFAULT 0,
    bytes_down INTEGER NOT NULL DEFAULT 0
);
CREATE INDEX IF NOT EXISTS idx_traffic_log_ts ON traffic_log(timestamp);

CREATE TABLE IF NOT EXISTS tether_total (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    bytes_up INTEGER NOT NULL DEFAULT 0,
    bytes_down INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS pc_reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    device_id TEXT NOT NULL DEFAULT 'pc',
    bytes_up_total INTEGER NOT NULL DEFAULT 0,
    bytes_down_total INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS domains_phone (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp INTEGER NOT NULL,
    app_name TEXT NOT NULL,
    domain TEXT NOT NULL,
    bytes_up INTEGER NOT NULL DEFAULT 0,
    bytes_down INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS limits (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    daily_limit_mb INTEGER NOT NULL DEFAULT 0,
    updated_at INTEGER NOT NULL
);