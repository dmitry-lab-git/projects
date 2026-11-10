# Database Design Document (DBDD)
## Project: Auroville Eco-Service ERP
**Document Version:** 1.0.0  
**Target Engine:** PostgreSQL 13+ (with PostGIS extension)  
**Timezone Context:** UTC 0 (Strict)  

---

## 1. System Schemas Isomorphic Segregation
Архитектура базы данных разделена на две изолированные схемы для обеспечения модульности и декомпозиции данных:
* **`dicts`**: Хранит мастер-справочники, статические конфигурации домена и системные классификаторы.
* **`infrastructure`**: Хранит append-only транзакционный лог событий (Event Store) и оперативные витрины данных.

---

## 2. Master Domain Catalogs (`dicts` Schema)

### 2.1 Table: `dicts.yards`
Пространственный справочник общин и точек сбора отходов Ауровиля.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `yard_id` | `UUID` | `PRIMARY KEY` | Уникальный идентификатор точки сбора. |
| `name` | `VARCHAR(150)` | `NOT NULL` | Название общины (например, 'Aspiration'). |
| `address` | `TEXT` | `NULL` | Физический адрес локации. |
| `location` | `GEOMETRY(Point, 4326)` | `NULL` | Географические GPS-координаты PostGIS (SRID WGS 84). |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE NOT NULL` | Флаг активности точки для логистических маршрутов. |
| `created_at` | `TIMESTAMP` | `DEFAULT (timezone('utc', now())) NOT NULL` | Время создания записи (UTC 0). |
| `updated_at` | `TIMESTAMP` | `DEFAULT (timezone('utc', now())) NOT NULL` | Время обновления записи (UTC 0). |

* **Indexes:**
  * `idx_yards_location` USING `GIST (location)` — Обеспечивает мгновенный поиск радиусов и оптимизацию маршрутов рикш.

```sql
CREATE TABLE dicts.yards (
    yard_id UUID PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT,
    location GEOMETRY(Point, 4326),
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL
);
CREATE INDEX idx_yards_location ON dicts.yards USING gist (location);
```

### 2.2 Table: `dicts.bag_event_types`
Справочник стабильных системных кодов и типов событий жизненного цикла мешка.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `event_type_id` | `UUID` | `PRIMARY KEY` | Идентификатор типа события. |
| `code` | `VARCHAR(50)` | `UNIQUE NOT NULL` | Строковый код для бизнес-логики бэкенда (`BagWeighed`). |
| `name` | `VARCHAR(100)` | `NOT NULL` | Название для пользовательского интерфейса. |
| `description` | `TEXT` | `NULL` | Описание назначения события. |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Время фиксации типа события. |

```sql
CREATE TABLE dicts.bag_event_types (
    event_type_id UUID PRIMARY KEY,
    code VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL
);
```

### 2.3 Table: `dicts.bag_types`
Классификатор базовых типов мешков, заявляемых жителями при раздельном сборе.

```sql
CREATE TABLE dicts.bag_types (
    type_id UUID PRIMARY KEY,
    code VARCHAR(30) UNIQUE NOT NULL, -- 'CLEAN_DRY', 'DIRTY_MIXED', 'ORGANIC'
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL
);
```

### 2.4 Table: `dicts.operators`
Матрица сотрудников Eco-Service и уровней доступа (Role-Based Access Control).

```sql
CREATE TABLE dicts.operators (
    operator_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(30) NOT NULL,            -- 'COLLECTOR', 'SORTER', 'MANAGER', 'CEO'
    access_level INT NOT NULL DEFAULT 0,  -- 0 = Collector, 1 = Sorter, 2 = Manager, 3 = CEO
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    created_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL,
    updated_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL,
    CONSTRAINT chk_operator_role CHECK (role IN ('COLLECTOR', 'SORTER', 'MANAGER', 'CEO')),
    CONSTRAINT chk_access_level CHECK (access_level BETWEEN 0 AND 3)
);
```

---

## 3. Transaction Log & Aggregate Registers (`infrastructure` Schema)

### 3.1 Table: `infrastructure.bags`
Неизменяемый мастер-реестр (паспорт) дискретных единиц сбора. Хранит только атрибуты «рождения» мешка.

```sql
CREATE TABLE infrastructure.bags (
    bag_id uuid NOT NULL,
    resident_id uuid NOT NULL,
    yard_id uuid NOT NULL,
    type_id uuid NOT NULL,
    created_at timestamp DEFAULT timezone('utc'::text, now()) NOT NULL,
    CONSTRAINT bags_bag_id_not_null NOT NULL bag_id,
    CONSTRAINT bags_created_at_not_null NOT NULL created_at,
    CONSTRAINT bags_pkey PRIMARY KEY (bag_id),
    CONSTRAINT bags_resident_id_not_null NOT NULL resident_id,
    CONSTRAINT bags_type_id_not_null NOT NULL type_id,
    CONSTRAINT bags_yard_id_not_null NOT NULL yard_id
);
CREATE INDEX idx_bags_resident_id ON infrastructure.bags USING btree (resident_id);
CREATE INDEX idx_bags_yard_id ON infrastructure.bags USING btree (yard_id);

-- Foreign keys linking registers to master dictionaries
ALTER TABLE infrastructure.bags ADD CONSTRAINT fk_bag_type FOREIGN KEY (type_id) REFERENCES dicts.bag_types(type_id);
ALTER TABLE infrastructure.bags ADD CONSTRAINT fk_bag_yard FOREIGN KEY (yard_id) REFERENCES dicts.yards(yard_id);
```

### 3.2 Table: `infrastructure.bag_events`
Единый append-only лог транзакционных событий (Event Store) для всех мешков.

```sql
CREATE TABLE infrastructure.bag_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_id UUID NOT NULL,
    event_type_id UUID NOT NULL,
    operator_id UUID,
    payload JSONB NOT NULL, -- Динамический контекст: {"weight_kg": 2.5}, {"allocations": [...]}
    occurred_at TIMESTAMP WITHOUT TIME ZONE DEFAULT (timezone('utc', now())) NOT NULL,
    
    CONSTRAINT fk_event_bag FOREIGN KEY (bag_id) REFERENCES infrastructure.bags (bag_id),
    CONSTRAINT fk_event_type FOREIGN KEY (event_type_id) REFERENCES dicts.bag_event_types (event_type_id),
    CONSTRAINT fk_event_operator FOREIGN KEY (operator_id) REFERENCES dicts.operators (operator_id)
);
CREATE INDEX idx_bag_events_bag_id ON infrastructure.bag_events (bag_id);
CREATE INDEX idx_bag_events_type_id ON infrastructure.bag_events (event_type_id);
```

---

## 4. Analytical Real-Time View (Read Model)
Представление для динамического расчета материального учета и вывода метрик на дашборд.

```sql
CREATE OR REPLACE VIEW infrastructure.view_material_resource_accounting AS
SELECT 
    c.code AS resource_code,
    c.name AS resource_material,
    ROUND(SUM((alloc.payload_record->>'weight_kg')::NUMERIC), 3) AS total_mass_kg,
    COUNT(DISTINCT e.bag_id) AS total_bags_count,
    ROUND(
        SUM((alloc.payload_record->>'weight_kg')::NUMERIC) / 
        COALESCE(NULLIF(EXTRACT(EPOCH FROM (MAX(e.occurred_at) - MIN(e.occurred_at))) / 2592000, 0), 1)::NUMERIC, 
        3
    ) AS monthly_average_kg
FROM infrastructure.bag_events e
JOIN dicts.bag_event_types et ON e.event_type_id = et.event_type_id
JOIN LATERAL jsonb_to_recordset(e.payload->'allocations') AS alloc(payload_record JSONB) ON TRUE
JOIN dicts.categories c ON (alloc.payload_record->>'category_id')::UUID = c.category_id
WHERE et.code = 'BagSorted'
GROUP BY c.code, c.name;
```

---

## 5. Deterministic Master Seed Data Script
Первичная синхронизация неизменяемых системных UUID.

```sql
SET search_path TO dicts, public;

-- Core Workflow States
INSERT INTO dicts.bag_event_types (event_type_id, code, name, description) VALUES
('fa4e5b22-8356-42d4-bb9e-4e4bf7e9b0e1', 'BagSubmitted', 'Bag Submitted', 'The resident registered the bag at the collection point via the mini-app.'),
('3c2b81fa-9d1a-4d24-82a1-5fe11c784ab2', 'BagArrivedAtHub', 'Bag Arrived at Hub', 'Collector #1 brought the bag and unloaded it inside the sorting garage.'),
('9f8e7d6c-5b4a-4321-bd23-1a2b3c4d5e6f', 'BagWeighed', 'Bag Weighed', 'Collector #2 scanned the bag and put it on the scale to record primary weight.'),
('da2a13f5-62bb-4c22-b5e1-8f4b7a2c3d10', 'BagSorted', 'Bag Sorted and Closed', 'The bag was processed on the sorting table, and its weight distributed to hub inventory.'),
('b7d8e9fa-1c2b-43d4-bc5e-6f7a8b9c0d1e', 'BagRejected', 'Bag Rejected', 'The operator rejected the bag due to critical organic contamination.')
ON CONFLICT (event_type_id) DO NOTHING;

-- Commmunity Separation Profiles
INSERT INTO dicts.bag_types (type_id, code, name, description) VALUES
('5e7f9a1b-3c5d-4e5f-2a3b-0c1d2e3f4a5b', 'CLEAN_DRY', 'Clean & Dry Recyclables', 'Plastic bottles, paper, cardboard, glass packaging, metals.'),
('6f8a0b2c-4d6e-4f6a-3b4c-1d2e3f4a5b6c', 'DIRTY_MIXED', 'Dirty Mixed Waste', 'Residual landfill waste that cannot be recycled.'),
('7a9b1c3d-5e7f-4a7b-4c5d-2e3f4a5b6c7d', 'ORGANIC', 'Organic / Compostable', 'Food waste, fruit peels, yard trimmings.')
ON CONFLICT (type_id) DO NOTHING;
```

### 6.2 B2C Simulation Strategy & Generation Logic

Вместо хаотичного заполнения лога (Bottom-Up) в системе применен **дедуктивный аналитический подход (Top-Down)**. Генерация транзакционной истории за 2 полных месяца (сентябрь и октябрь 2026 года) строится на базе декомпозиции макроэкономических показателей реального домохозяйства.

#### Архитектурная схема моделирования:

1. **Базовая метрика (Входной паттерн):** За основу берутся точные зафиксированные объемы отходов одной жилой квартиры (2 человека) за 1 календарный месяц.
2. **Экстраполяция масштаба (Пилотная группа):** Данные квартиры линейно умножаются на масштаб пилотного сегмента системы (**50 идентичных квартир**) и на период симуляции (**2 месяца**).
3. **Генерация Стримов (PL/pgSQL Процедура):** Циклический алгоритм ежедневно симулирует дискретное поступление мешков, обеспечивая схождение итогового баланса с точностью до грамма:
   * **Шаг 1 (.bags):** Инициализирует постоянный паспорт (`bag_id`) с привязкой к случайной жилой общине Ауровиля (`yard_id`) в схеме `dicts`.
   * **Шаг 2 (.bag_events):** Генерирует событие `BagSubmitted` без указания оператора (через Telegram Mini App жителя).
   * **Шаг 3 (.bag_events):** С временным сдвигом логистики вносит событие `BagArrivedAtHub` с фиксацией UUID оператора-сборщика (`role = 'COLLECTOR'`).
   * **Шаг 4 (.bag_events):** Генерирует событие `BagWeighed`. Вес мешка динамически рассчитывается как средняя масса фракции из бытовой таблицы с внесением случайной девиации (шума).
   * **Шаг 5 (.bag_events):** Завершает жизненный цикл мешка событием `BagSorted`. Физический вес перетекает в массив `allocations`, жестко связываясь по UUID с целевой категорией сырья из `dicts.categories`.

#### Бизнес-проверка модели (Read Model Replay)
Применение стабильных строковых кодов (`et.code = 'BagSorted'`) в аналитическом представлении `view_material_resource_accounting` позволяет на лету выполнять операцию Replay над сгенерированным логом. На выходе СУБД формирует готовую витрину материального учета, которая является математически точным отражением бытовой структуры отходов пилотного сектора.

## 7. Automated Data Seeding & Simulation Concept

Для обеспечения быстрой локальной разработки (в среде WSL/Docker) и проведения сквозного тестирования ERP-системы, в ядро закладывается концепция **автономного автоматического сид-движка (Data Seeding Engine)** на Python.

### 7.1 Ключевые архитектурные правила сид-движка

1. **Идемпотентность и полный сброс (Teardown & Setup):**
   * Каждый запуск скрипта должен начинаться с каскадной очистки (`TRUNCATE ... CASCADE`) всех транзакционных таблиц схемы `infrastructure` и справочников схемы `dicts`. 
   * Это гарантирует предсказуемое состояние базы данных при тестировании новых веток логики.

2. **Двухслойная сквозная инициализация:**
   * **Слой справочников (`dicts`):** Скрипт синхронизирует жестко зафиксированные системные UUIDv4 для типов событий (`BagSubmitted`, `BagSorted`), профилей мешков (`CLEAN_DRY`, `ORGANIC`) и базовых категорий сырья.
   * **Слой лога (`infrastructure`):** На основе мастер-данных скрипт реплеит (воспроизводит) транзакционную историю, формируя паспорта мешков и цепочки их событий.

3. **Масштабируемая дедуктивная модель (Top-Down Simulation):**
   * Вместо генерации случайного цифрового шума, симулятор принимает на вход точные метрики реального хозяйства (базовый паттерн генерации отходов на 2 человека в месяц).
   * Алгоритм линейно масштабирует этот паттерн на размер пилотного сектора (N квартир) и временной шаг (M месяцев), нарезая макро-объемы на дискретные мешки.

4. **Контрактная валидация перед записью (Fail-Fast):**
   * Симулятор не пишет данные в PostgreSQL «вслепую». Перед сборкой JSON-поля `payload` (например, распределения весов `allocations`) структура данных обязана пройти валидацию через схемы **Pydantic v2**.
   * Если логика симулятора нарушит доменный контракт (сгенерирует отрицательный вес или некорректный строковый код), скрипт упадет до обращения к СУБД, защищая лог от загрязнения.

5. **Асинхронность и изоляция окружения:**
   * Движок выполняется в изолированном виртуальном окружении Python (`venv`) внутри WSL проекта `eco_service` и использует неблокирующий драйвер `asyncpg`, что позволяет разворачивать двухмесячную историю пилота (тысячи транзакций) менее чем за 2 секунды.
## 9. Database-Driven Security & Access Control Layer

Для централизованного управления аутентификацией, авторизацией и аудитом действий пользователей в СУБД выделяется независимый изолированный контур — схема `security`.

### 9.1 Архитектурные принципы слоя безопасности

1. **Изоляция учетных записей (Separation of Concerns):**
   * Все данные, связанные с безопасностью (хэши паролей, сессионные токены, ключи Telegram, уровни доступа), физически отделены от бизнес-справочников (`dicts`) и транзакционных логов (`infrastructure`).

2. **Единый идентификатор безопасности (Security Subject):**
   * Каждый субъект системы (будь то Amma-сортировщик, рикша-сборщик или житель общины) получает сквозной `user_id` (UUIDv4). Этот ID является первичным ключом в схеме `security` и используется как `operator_id` или `resident_id` во всех остальных слоях базы данных.

3. **Гранулярный RBAC (Role-Based Access Control):**
   * Схема жестко контролирует системные роли и числовые уровни доступа (`access_level` от 0 до 3), гарантируя валидацию прав на уровне ограничений СУБД (`CHECK constraints`).

4. **Аудит сессионного контекста (Immutable Audit Trail):**
   * Любой вход в систему через Telegram Mini App или PWA фиксируется в журнале сессий с привязкой к IP-адресу, User-Agent и временной метке в UTC 0, обеспечивая прозрачный аудит безопасности.
### 9.2 Агностическая интеграция с внешними мессенджерами

ERP-система является полностью агностической по отношению к провайдерам связи и не привязывается к конкретным коммерческим брендам (Telegram, WhatsApp и др.). 

Авторизация внешних клиентов (как жителей, так и операторов) базируется на полиморфной связке двух полей:
1. `messenger_provider`: Строковый идентификатор платформы (например, 'TELEGRAM', 'WHATSAPP', 'MATRIX', 'INTERNAL').
2. `messenger_uid`: Уникальный текстовый идентификатор пользователя внутри этой платформы (UID, Handle или ID чата).

Это позволяет переключать или комбинировать интерфейсы взаимодействия (Mini Apps, боты, PWA) без проведения миграций и структурных изменений в ядре базы данных.

## 10. Automated Initialization & Master Seeding Engine

Для развертывания системы в локальном окружении разработки (WSL/Docker) используется асинхронный сид-движок, выполняющий сквозную инициализацию всех слоев хранения (Security, Dicts, Infrastructure) в рамках единого жизненного цикла.

### 10.1 Алгоритм работы движка
1. **Каскадная очистка (Teardown):** Полное обнуление транзакционных таблиц и справочников для обеспечения идемпотентности повторных запусков.
2. **Синхронизация инвариантов (Master Seed):** Запись жестко зафиксированных системных UUIDv4 и строковых кодов, на которых базируются наши Read-модели.
3. **Криптографическая защита (Credential Hashing):** Нативная генерация солей и хэширование паролей административного персонала по стандарту bcrypt до момента их отправки в СУБД.
4. **Дедуктивная симуляция (B2C Stream Generation):** Развертывание двухмесячной истории пилотного двора (50 квартир) с точностью до грамма на основе реальных метрик потребления.



Итоговый прогноз образования отходов (Период: 2 месяца / 60 дней)

Данный анализ составлен для MVP-модели учета отходов в 10 организациях Ауровиля. В качестве базовой расчетной единицы принят стандартный плотный мешок объемом 60–80 литров. Любые сопутствующие форматы (например, связанные стопки картона или ящики со стеклом) для простоты моделирования приравниваются к объему одного мешка.

1. Сводные показатели генерации отходов


Рестораны (1 объект: Auroville Bakery)

• Органические отходы (ORGANIC): 120 – 150 мешков (всего 1440 – 1800 кг).
	• Частота вывоза: Ежедневно.
• Сухое вторсырье (CLEAN_DRY): 60 – 80 мешков (всего 300 – 400 кг).
	• Частота вывоза: 2–3 раза в неделю.
• Смешанный мусор (DIRTY_MIXED): 20 – 30 мешков (всего 200 – 300 кг).
	• Частота вывоза: 1–2 раза в неделю.

Офисы и Магазины (3 объекта: PTDC, Visitors Centre Shop, Computation Group)

• Сухое вторсырье (CLEAN_DRY): 40 – 50 мешков (всего 160 – 200 кг).
	• Частота вывоза: 2–3 раза в неделю.
• Органические отходы (ORGANIC): 15 – 20 мешков (всего 120 – 160 кг).
	• Частота вывоза: 1–2 раза в неделю.
• Смешанный мусор (DIRTY_MIXED): 10 – 15 мешков (всего 70 – 105 кг).
	• Частота вывоза: 1 раз в неделю.

Фабрики и Мастерские (2 объекта: Auroville Press, La Ferme Woodworks)

• Сухое вторсырье (CLEAN_DRY): 70 – 90 мешков (всего 560 – 720 кг).
	• Частота вывоза: 3–4 раза в неделю (высокий объем обрезков и упаковки).
• Смешанный мусор (DIRTY_MIXED): 15 – 25 мешков (всего 135 – 225 кг).
	• Частота вывоза: 1 раз в неделю.
• Органические отходы (ORGANIC): 10 – 15 мешков (всего 80 – 120 кг).
	• Частота вывоза: 1 раз в неделю.

Гестхаусы (2 объекта: Sadhana Forest, Quiet Healing Center)

• Органические отходы (ORGANIC): 80 – 100 мешков (всего 800 – 1000 кг).
	• Частота вывоза: Ежедневно или через день. (Примечание: В Sadhana Forest органика преимущественно компостируется на месте, поэтому объем внешнего вывоза может быть меньше физического накопления).
• Сухое вторсырье (CLEAN_DRY): 50 – 70 мешков (всего 200 – 280 кг).
	• Частота вывоза: 2–3 раза в неделю.
• Смешанный мусор (DIRTY_MIXED): 15 – 20 мешков (всего 120 – 160 кг).
	• Частота вывоза: 1 раз в неделю.

Школы и Другие объекты (2 объекта: Isai Ambalam School, Auroville Botanical Garden)

• Органические отходы (ORGANIC): 40 – 60 мешков (всего 360 – 540 кг).
	• Частота вывоза: 2–3 раза в неделю (в учебные и рабочие дни).
• Сухое вторсырье (CLEAN_DRY): 25 – 35 мешков (всего 125 – 175 кг).
	• Частота вывоза: 1–2 раза в неделю.
• Смешанный мусор (DIRTY_MIXED): 10 – 15 мешков (всего 70 – 105 кг).
	• Частота вывоза: 1 раз в неделю.

Итоговые показатели по всем 10 объектам

• Общее количество мешков: ~580 – 760 штук за 2 месяца.
• Общая масса отходов: ~4 820 – 6 385 кг.
• Среднесуточный поток: Суммарно со всех точек собирается около 10–12 мешков в день.


================================================================================
4. АРХИТЕКТУРА ДОСТУПА И РОЛЕВАЯ МОДЕЛЬ (RBAC)
================================================================================

Для обеспечения легкого управления системой силами малой команды (10 человек)
и предотвращения ошибок ввода применяется четкое разграничение уровней доступа
(Role-Based Access Control). Система разделена на 4 уровня доступа
(access_level: 0–3) в СУБД PostgreSQL.

--------------------------------------------------------------------------------
4.1. Матрица ролей и полномочий
--------------------------------------------------------------------------------

1. GUEST / RESIDENT (Уровень доступа: 0)
   - Представители: Жители (50+ HH), Менеджеры организаций (10 Org)
   - Интерфейс: Внешний PWA / Telegram Mini App
   - Функционал:
     * Просмотр расписания вывоза по своему Ярду (yard_id).
     * Подача заявок на спец-вывоз (крупногабарит / опасные отходы).
     * Просмотр личной и локальной статистики переработки.

2. COLLECTOR (Уровень доступа: 1)
   - Представители: Anand, Raman, Vijay
   - Интерфейс: Полевой PWA сборщика
   - Функционал:
     * Фиксация забора партий от Ярдов и организаций (в 1 клик).
     * Сканирование QR-кодов точек и контейнеров.
     * Логирование статуса ARRIVED и привязка вида транспорта (truck/rickshaw).

3. SORTER (Уровень доступа: 1)
   - Представители: Lakshmi, Saraswati, Selvi, Devi, Parvathi
   - Интерфейс: Планшет сортировочного хаба (на весах)
   - Функционал:
     * Приемка и автоматический/ручной ввод веса партии (WEIGHED).
     * Фиксация структуры фракций и признаков загрязнения (SORTED).
     * Просмотр загрузки текущей смены.

4. MANAGER (Уровень доступа: 2)
   - Представители: Palani, Sophie
   - Интерфейс: Диспетчерский веб-кабинет
   - Функционал:
     * Мониторинг логистических маршрутов и загрузки Ярдов.
     * Разбор инцидентов (некачественная сортировка, пропущенные заборы).
     * Управление справочниками Ярдов, организаций и резидентов.
     * Доступ к представлениям analytics.v_yard_performance и v_operator_performance.

5. CEO (Уровень доступа: 3)
   - Представитель: Kali Borg
   - Интерфейс: Стратегический дашборд (Полный доступ)
   - Функционал:
     * Сквозной аудит системы и ключевых KPI (analytics.v_kpi_summary,
       v_daily_trends, v_waste_by_category).
     * Экспорт отчетности для администрации Ауровиля и эко-фондов.
     * Управление правами доступа и записями операторов (dicts.operators).

--------------------------------------------------------------------------------
4.2. Разграничение на уровне базы данных и безопасности
--------------------------------------------------------------------------------

- Табличные ограничения (CHECK Constraints):
  В таблице dicts.operators уровень доступа ограничен валидацией
  access_level BETWEEN 0 AND 3. Роли строго соответствуют перечню:
  'COLLECTOR', 'SORTER', 'MANAGER', 'CEO'.

- Ограничение видимости данных (Group Privacy):
  * Уровень 0 (Резиденты): Не имеют прямого доступа к таблицам инфраструктуры
    (infrastructure.bags, infrastructure.bag_events). Взаимодействие идет
    через изолированные API-эндпоинты. Данные соседних домохозяйств скрыты,
    доступна только агрегированная статистика по Ярду.
  * Уровень 1 (Полевая команда): Имеют право создавать записи событий
    (INSERT в bag_events), но не могут редактировать или удалять исторические
    логи транзакций.
  * Уровни 2–3 (Менеджмент): Полный доступ на чтение аналитики analytics
    и корректировку справочников dicts.

- Аутентификация и сессии:
  Авторизация операторов (Уровни 1–3) осуществляется по логину (username)
  и паролю/PIN-коду с выдачей JWT-токенов. Для сборщиков и сортировщиков
  интерфейс оптимизирован под сенсорные экраны для быстрого переключения смен.
================================================================================
