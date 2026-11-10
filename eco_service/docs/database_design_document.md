# Database Design Document (DBDD)
## Project: Auroville Eco-Service ERP
**Document Version:** 1.0.0  
**Target Engine:** PostgreSQL 13+ (with PostGIS extension)  
**Timezone Context:** UTC 0 (Strict)  

---

## 1. System Schemas Isomorphic Segregation
The database architecture is split into three isolated schemas to ensure modularity, security, and clean separation of concerns:
* **`dicts`**: Stores master catalogs, static domain configurations, and system classifiers.
* **`infrastructure`**: Holds the append-only transactional log (Event Store) and operational real-time read views.
* **`security`**: Manages authentication, authorization, user credentials, and session logs to isolate security vectors from business logic.

---

## 2. Master Domain Catalogs (`dicts` Schema)

### 2.1 Table: `dicts.yards`
Spatial directory of Auroville communities and waste collection hubs.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `yard_id` | `UUID` | `PRIMARY KEY` | Unique identifier for the collection point. |
| `name` | `VARCHAR(150)` | `NOT NULL` | Community name (e.g., 'Aspiration'). |
| `address` | `TEXT` | `NULL` | Physical address details. |
| `location` | `GEOMETRY(Point, 4326)` | `NULL` | PostGIS geographic GPS coordinates (SRID WGS 84). |
| `is_active` | `BOOLEAN` | `DEFAULT TRUE NOT NULL` | Operational flag for active logistics routing. |
| `created_at` | `TIMESTAMP` | `DEFAULT (timezone('utc', now())) NOT NULL` | Row creation timestamp (UTC 0). |
| `updated_at` | `TIMESTAMP` | `DEFAULT (timezone('utc', now())) NOT NULL` | Row modification timestamp (UTC 0). |

* **Indexes:**
  * `idx_yards_location` USING `GIST (location)` — Enables immediate spatial proximity searches and rickshaw route optimizations.

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
Dictionary of immutable system codes mapping the lifecycles of single waste units.

| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `event_type_id` | `UUID` | `PRIMARY KEY` | Unique event type token. |
| `code` | `VARCHAR(50)` | `UNIQUE NOT NULL` | String slug for backend business rules (`BagWeighed`). |
| `name` | `VARCHAR(100)` | `NOT NULL` | User interface display name. |
| `description` | `TEXT` | `NULL` | Detailed business scope of the event. |
| `created_at` | `TIMESTAMP` | `NOT NULL` | Mapping registration timestamp. |

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
Classifier for basic waste bag categorization declared by residents.

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
Internal matrix of Eco-Service staff mapping directly to Role-Based Access Control policies.

```sql
CREATE TABLE dicts.operators (
    operator_id UUID PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    full_name VARCHAR(150) NOT NULL,
    role VARCHAR(30) NOT NULL,            -- 'COLLECTOR', 'SORTER', 'MANAGER', 'CEO'
    access_level INT NOT NULL DEFAULT 0,  -- 0 = Collector/Sorter, 2 = Manager, 3 = CEO
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
Immutable passport tracking discrete collection bags. Records only birth attributes of a bag unit.

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

ALTER TABLE infrastructure.bags ADD CONSTRAINT fk_bag_type FOREIGN KEY (type_id) REFERENCES dicts.bag_types(type_id);
ALTER TABLE infrastructure.bags ADD CONSTRAINT fk_bag_yard FOREIGN KEY (yard_id) REFERENCES dicts.yards(yard_id);
```

### 3.2 Table: `infrastructure.bag_events`
Unified append-only transaction ledger (Event Store) tracking historical mutation chains for all bags.

```sql
CREATE TABLE infrastructure.bag_events (
    event_id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    bag_id UUID NOT NULL,
    event_type_id UUID NOT NULL,
    operator_id UUID,
    payload JSONB NOT NULL, -- Dynamic payload layout: {"weight_kg": 2.5}, {"allocations": [...]}
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
Material resource counting engine powering analytical dashboard streams on the fly.

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
Primary lookup seed initializing invariant system UUID identifiers across nodes.

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

-- Community Separation Profiles
INSERT INTO dicts.bag_types (type_id, code, name, description) VALUES
('5e7f9a1b-3c5d-4e5f-2a3b-0c1d2e3f4a5b', 'CLEAN_DRY', 'Clean & Dry Recyclables', 'Plastic bottles, paper, cardboard, glass packaging, metals.'),
('6f8a0b2c-4d6e-4f6a-3b4c-1d2e3f4a5b6c', 'DIRTY_MIXED', 'Dirty Mixed Waste', 'Residual landfill waste that cannot be recycled.'),
('7a9b1c3d-5e7f-4a7b-4c5d-2e3f4a5b6c7d', 'ORGANIC', 'Organic / Compostable', 'Food waste, fruit peels, yard trimmings.')
ON CONFLICT (type_id) DO NOTHING;
```

---

## 6. Pilot Waste Stream Forecasting (MVP Model)
This descriptive analytics profile covers the MVP metrics modeled for 10 distinct Auroville commercial and educational entities. The core operational metric treats a 60–80L bag as a single volume allocation token (alternative shapes such as tied cardboard bundle structures or glass crates map to an equivalent bag metric).

### 6.1 Entity-Level Stream Volume Forecast (60-Day Horizon)

* **Restaurants (1 site: Auroville Bakery)**
  * `ORGANIC`: 120 – 150 bags total (1,440 – 1,800 kg). Dispatch Frequency: Daily.
  * `CLEAN_DRY`: 60 – 80 bags total (300 – 400 kg). Dispatch Frequency: 2–3 times per week.
  * `DIRTY_MIXED`: 20 – 30 bags total (200 – 300 kg). Dispatch Frequency: 1–2 times per week.
* **Offices & Retail (3 sites: PTDC, Visitors Centre Shop, Computation Group)**
  * `CLEAN_DRY`: 40 – 50 bags total (160 – 200 kg). Dispatch Frequency: 2–3 times per week.
  * `ORGANIC`: 15 – 20 bags total (120 – 160 kg). Dispatch Frequency: 1–2 times per week.
  * `DIRTY_MIXED`: 10 – 15 bags total (70 – 105 kg). Dispatch Frequency: Once per week.
* **Factories & Workshops (2 sites: Auroville Press, La Ferme Woodworks)**
  * `CLEAN_DRY`: 70 – 90 bags total (560 – 720 kg). Dispatch Frequency: 3–4 times per week (dense manufacturing offsets/trimmings).
  * `DIRTY_MIXED`: 15 – 25 bags total (135 – 225 kg). Dispatch Frequency: Once per week.
  * `ORGANIC`: 10 – 15 bags total (80 – 120 kg). Dispatch Frequency: Once per week.
* **Guesthouses (2 sites: Sadhana Forest, Quiet Healing Center)**
  * `ORGANIC`: 80 – 100 bags total (800 – 1000 kg). Dispatch Frequency: Daily / Alternative days. (*Note: Sadhana Forest emphasizes localized backyard composting pipelines, reducing actual external dispatch streams relative to physical processing totals*).
  * `CLEAN_DRY`: 50 – 70 bags total (200 – 280 kg). Dispatch Frequency: 2–3 times per week.
  * `DIRTY_MIXED`: 15 – 20 bags total (120 – 160 kg). Dispatch Frequency: Once per week.
* **Schools & Gardens (2 sites: Isai Ambalam School, Auroville Botanical Garden)**
  * `ORGANIC`: 40 – 60 bags total (360 – 540 kg). Dispatch Frequency: 2–3 times per week (active learning schedules).
  * `CLEAN_DRY`: 25 – 35 bags total (125 – 175 kg). Dispatch Frequency: 1–2 times per week.
  * `DIRTY_MIXED`: 10 – 15 bags total (70 – 105 kg). Dispatch Frequency: Once per week.

### 6.2 Aggregate Pilot Metrics
* **Total Bag Generation Token Count**: ~580 – 760 units over 60 days.
* **Total Simulated Mass Volume**: ~4,820 – 6,385 kg.
* **Mean Daily Influx Baseline**: 10 – 12 physical bags processed per diurnal period.

### 6.3 B2C Simulation Strategy & Generation Logic
Instead of chaotic log noise injection (Bottom-Up framework), the subsystem incorporates a deductive analytical structure (**Top-Down architecture**). Transactional lifecycle history generation for 2 full months (September and October 2026) parses macro weight metrics recorded from a single real-world benchmark household (2-person baseline per calendar month).

#### Generation Modeling Lifecycle:
1. **Input Baseline**: Real single residential flat monthly audit yields form the deterministic seed state.
2. **Scale Extrapolation**: Baseline metrics multiply linearly against the pilot cohort size (**50 target households**) over the exact operational period (**2 calendar months**).
3. **Stream Resolution via PL/pgSQL Routine**: Loop routines issue discrete daily bags, matching target balances down to single-gram precisions:
   * **Step 1 (`.bags`)**: Initializes a persistent single state card (`bag_id`) linking randomly to an active community entry (`yard_id`) in `dicts`.
   * **Step 2 (`.bag_events`)**: Dispatches a `BagSubmitted` state flag void of an operational user token (representing autonomous submission via the residential Telegram Mini App).
   * **Step 3 (`.bag_events`)**: Shifts time metrics to emulate collection routes, appending a `BagArrivedAtHub` log stamped with a `COLLECTOR` operator UUID.
   * **Step 4 (`.bag_events`)**: Issues a `BagWeighed` event. Mass attributes derive dynamically from fraction tables injected with deviation coefficients (random noise).
   * **Step 5 (`.bag_events`)**: Concludes transaction lifecycles by changing the state to `BagSorted`. Physical grams map into an inline `allocations` recordset array array, binding tightly to target category signatures (`dicts.categories`).

#### Business Validation Layer (Read Model Replay)
By parsing fixed event codes (`et.code = 'BagSorted'`), the analytical view structure executes continuous stream replays across transactional event layers. The database yields instant mass totals matching the baseline composition properties of the target pilot grid exactly.

---

## 7. Automated Data Seeding & Simulation Rules
To enable rapid local provisioning inside WSL/Docker runtime containers and ensure robust integration workflows, an automated Python data seeding mechanism is coupled to the core layer.

### 7.1 Key Seeding Constraints
1. **Idempotence and Complete Teardown**: Executions enforce structural cascade wipes (`TRUNCATE ... CASCADE`) across transaction arrays (`infrastructure`) and tables (`dicts`), ensuring predictable initial states before logic mutations are tested.
2. **Dual-Layer End-to-End Invariant Provisioning**:
   * *Dictionary Invariants (`dicts`)*: Locks static deployment signatures (UUIDv4) for state changes and profiling streams.
   * *Ledger States (`infrastructure`)*: Iteratively evaluates synthetic transaction streams from invariant lookups.
3. **Top-Down Scale Invariant Simulation Model**: Replaces pure uniform random mutations with targeted distribution algorithms based on micro-consumption frameworks.
4. **Contract Validation (Fail-Fast Verification)**: Data models evaluate inline structural targets via **Pydantic v2 schemas** prior to database pipeline insertion, protecting JSON fields against contract drift.
5. **Asynchronous Isolation Context**: Operates using an isolated interpreter stack (`venv`) calling `asyncpg` execution nodes, scaling massive multi-month operation grids (thousands of objects) within 2 seconds.

---

## 8. Database-Driven Security & Access Control Layer (RBAC)
Authentication, authorization vectors, and granular operational records isolate inside an explicitly isolated database realm named the `security` schema.

### 8.1 Core Architectural Security Directives
1. **Credential Segregation**: User authentication targets (bcrypt hash parameters, access metrics, Telegram client tokens) decouple physically from system dictionaries and transaction stores.
2. **Unified Subject Scope**: System actors (Amma sort specialists, rickshaw transit teams, community citizens) bind under a single `user_id` identifier (UUIDv4), mapping downstream as polymorphic references across schemas.
3. **Granular RBAC Constraint Mapping**: Enforcement uses database rules and values check configurations (`access_level BETWEEN 0 AND 3`) handled directly within database transaction walls.
4. **Immutable Audit Trails**: Session metrics (Telegram Client parameters, source IP mapping, context stamps) write immediately upon application engagement.

### 8.2 Access Matrix Specifications

| Role | Access Level | Target Client Interface | Permitted Functionality Scope |
| :--- | :---: | :--- | :--- |
| **GUEST / RESIDENT** | `0` | Resident PWA / Telegram Mini App | Browse local collection calendars; file bulk special-waste collection requests; view personal yard metrics. |
| **COLLECTOR** | `1` | Field Mobility Transit PWA | Record physical cargo pickups from community yards; scan node QR tokens; log vehicle properties (`truck`/`rickshaw`). |
| **SORTER** | `1` | Sorting Hub Scale Tablet | Commit gross mass payload statistics; flag contamination parameters; display local shift batch updates. |
| **MANAGER** | `2` | Central Dispatch Operations Desktop | Supervise logistic loops; audit contamination alerts; manage community directories; query performance indices. |
| **CEO** | `3` | Executive Metrics Dashboard | Full access scope; sweep security system history; adjust global operational flags; administer operator parameters. |

* **Data Isolation and Visibility Directives:**
  * *Level 0 (Citizens)*: Barred from direct transaction tables (`infrastructure.bags`). Operations process through specialized backend validation API routes. Neighboring rows remain fully masked.
  * *Level 1 (Field Personnel)*: Limited to row append operations (`INSERT` on `bag_events`). Historical log deletion or runtime mutations are physically restricted.
  * *Levels 2–3 (Management Matrix)*: Fully authorized for analytical aggregations and master lookup modifications.

### 8.3 Agnostic Messenger Polymorphism
The software retains absolute decoupling from specific communication utility platforms. Client authentication bridges using an abstract polymorphic record design mapping two tracking strings:
1. `messenger_provider`: Defines target service profiles (e.g., `'TELEGRAM'`, `'WHATSAPP'`, `'MATRIX'`, `'INTERNAL'`).
2. `messenger_uid`: Stores platform-specific alphanumeric identifiers (Account tags, unique chat identifiers, or system tokens).

This approach allows client interfaces (Mini Apps, chat automations, or native wrappers) to scale and pivot without triggering core schema migrations.
