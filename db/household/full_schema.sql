--
-- PostgreSQL database dump
--

\restrict Go9sW9QOGQWEpMur8eCivDMI2HMGSjZ8DqYEoT7hdP4MZdSoLsBoUc7EIsNGz0F

-- Dumped from database version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)
-- Dumped by pg_dump version 18.6 (Ubuntu 18.6-0ubuntu0.26.04.1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: culina; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA culina;


--
-- Name: SCHEMA culina; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON SCHEMA culina IS 'Схема для кулинарного проекта и каталога продуктов';


--
-- Name: gardening; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA gardening;


--
-- Name: infrastructure; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA infrastructure;


--
-- Name: medicine; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA medicine;


--
-- Name: projects; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA projects;


--
-- Name: repair; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA repair;


--
-- Name: texere; Type: SCHEMA; Schema: -; Owner: -
--

CREATE SCHEMA texere;


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


--
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS "uuid-ossp" WITH SCHEMA public;


--
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: -
--

COMMENT ON EXTENSION "uuid-ossp" IS 'generate universally unique identifiers (UUIDs)';


--
-- Name: schedule_status; Type: TYPE; Schema: medicine; Owner: -
--

CREATE TYPE medicine.schedule_status AS ENUM (
    'active',
    'completed',
    'overdue',
    'paused',
    'archived'
);


--
-- Name: mat_type; Type: TYPE; Schema: texere; Owner: -
--

CREATE TYPE texere.mat_type AS ENUM (
    'textile',
    'hardware',
    'consumable'
);


--
-- Name: fn_check_daily_supplement_limit(); Type: FUNCTION; Schema: medicine; Owner: -
--

CREATE FUNCTION medicine.fn_check_daily_supplement_limit() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_already_taken INT4;
    v_supplement_name VARCHAR(255);
BEGIN
    -- Считаем, сколько единиц этого препарата УЖЕ было принято в указанный день
    -- (Исключаем текущую строку, если это UPDATE, чтобы не считать её дважды)
    SELECT COALESCE(SUM(amount), 0)
    INTO v_already_taken
    FROM medicine.intakes
    WHERE intake_date = NEW.intake_date
      AND supplement_id = NEW.supplement_id
      AND id <> NEW.id;

    -- Проверяем: если старое количество + новое превышает 5, выбрасываем ошибку
    IF (v_already_taken + NEW.amount) > 5 THEN
        -- Получаем название препарата для красивого текста ошибки
        SELECT name INTO v_supplement_name 
        FROM medicine.supplements 
        WHERE id = NEW.supplement_id;

        RAISE EXCEPTION 'Ошибка превышения суточной дозировки! Вы пытаетесь внести % шт. Препарат "%" на дату % уже принят в количестве % шт. Суммарный лимит превысит 5 шт. за день.', 
            NEW.amount, v_supplement_name, NEW.intake_date, v_already_taken;
    END IF;

    -- Если проверка прошла, разрешаем запись
    RETURN NEW;
END;
$$;


--
-- Name: fn_sync_schedule_statuses(); Type: FUNCTION; Schema: medicine; Owner: -
--

CREATE FUNCTION medicine.fn_sync_schedule_statuses() RETURNS void
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Переводим в 'overdue' те курсы, которые активны, но их end_date уже в прошлом
    UPDATE medicine.schedules
    SET status = 'overdue'
    WHERE status = 'active' 
      AND end_date < CURRENT_DATE;
      
    -- (Опционально) Если курс был на паузе, но срок его конца наступил, 
    -- мы можем перевести его в completed или оставить в архиве на ваше усмотрение
END;
$$;


--
-- Name: log_system_verification(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.log_system_verification() RETURNS text
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_total_count INTEGER;
    v_verified_count INTEGER;
    v_total_balance_sum NUMERIC(19, 4);
    v_verified_ids UUID[]; 
    v_last_transaction_id UUID;
    v_status_id UUID;
    v_verification_hash VARCHAR(64);
    v_rows_affected INTEGER;
BEGIN
    -- 1. Находим ID последней актуальной транзакции на текущий момент
    SELECT id INTO v_last_transaction_id
    FROM public.transactions
    ORDER BY created_at DESC
    LIMIT 1;

    -- 2. Собираем показатели из уже сформированного отчета
    SELECT 
        COUNT(*),
        COUNT(*) FILTER (WHERE r.account_balance_status = 'verified'),
        COALESCE(SUM(r.balance) FILTER (WHERE r.account_balance_status = 'verified'), 0),
        ARRAY_AGG(a.id ORDER BY a.id) FILTER (WHERE r.account_balance_status = 'verified'),
        md5(ARRAY_TO_STRING(ARRAY_AGG(a.id::text || ':' || r.balance::text ORDER BY a.id) FILTER (WHERE r.account_balance_status = 'verified'), ','))
    INTO 
        v_total_count, 
        v_verified_count,
        v_total_balance_sum,
        v_verified_ids,
        v_verification_hash
    FROM reports.account_state_report r
    LEFT JOIN dicts.accounts a ON r.account_id = a.account_id;

    -- 3. Проверка жесткого условия
    IF v_total_count > 0 AND v_total_count = v_verified_count THEN
        
        SELECT id INTO v_status_id 
        FROM dicts.dict_statuses 
        WHERE entity_type = 'SYSTEM_VERIFICATION' AND code = 'SUCCESS';

        IF v_status_id IS NULL THEN
            INSERT INTO dicts.dict_statuses (entity_type, code, name)
            VALUES ('SYSTEM_VERIFICATION', 'SUCCESS', 'All accounts verified')
            RETURNING id INTO v_status_id;
        END IF;

        -- Пытаемся записать лог
        INSERT INTO reports.system_verification_log (
            status_id,
            total_accounts_processed, 
            verified_count, 
            total_balance_sum,
            verified_account_ids,
            last_transaction_id,
            verification_hash
        )
        VALUES (
            v_status_id,
            v_total_count, 
            v_verified_count, 
            v_total_balance_sum,
            COALESCE(v_verified_ids, '{}'::UUID[]),
            v_last_transaction_id,
            v_verification_hash
        )
        ON CONFLICT (verification_hash) DO NOTHING;

        -- Проверяем, вставилась ли реальная новая строка
        GET DIAGNOSTICS v_rows_affected = ROW_COUNT;

        IF v_rows_affected > 0 THEN
            RETURN 'All accounts verified, log registered';
        ELSE
            RETURN 'All accounts verified, but no changes detected (duplicate skipped)';
        END IF;
        
    ELSE
        RETURN 'Not all accounts are verified';
    END IF;

END;
$$;


--
-- Name: refresh_account_state_report(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.refresh_account_state_report() RETURNS void
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_total_count INTEGER;
    v_verified_count INTEGER;
    v_total_balance_sum NUMERIC(19, 4);
    v_verified_ids UUID[]; -- Массив настоящих UUID
    v_status_id UUID;
    v_verification_hash VARCHAR(64);
BEGIN
    -- 1. Очищаем старый отчет
    TRUNCATE TABLE reports.account_state_report;

    -- 2. Генерируем новый отчет и вставляем данные
    INSERT INTO reports.account_state_report (
        account_id, 
        account_name, 
        entity, 
        balance, 
        account_balance_status, 
        last_updated, 
        account_state, 
        snapshot_tr_id, 
        acc_last_tr_id, 
        acc_balance_snapshot_balance
    )
    WITH latest_ledger AS (
        SELECT 
            account_id,
            MAX(transaction_id) as last_tr_id,
            (ARRAY_AGG(acc_balance ORDER BY transaction_id DESC))[1] as current_balance
        FROM public.ledger 
        GROUP BY account_id
    ),
    latest_snapshot AS (
        SELECT DISTINCT ON (account_id)
            account_id,
            tr_id::integer as snapshot_tr_id,
            balance::numeric as snapshot_balance
        FROM public.acc_balance_snapshot_register
        ORDER BY account_id, code DESC
    ),
    combined AS (
        SELECT 
            acc.account_id::varchar(50),
            acc.account_name,
            ent.entity_name,
            ll.current_balance,
            CASE 
                WHEN ls.snapshot_tr_id IS NULL THEN 'no_snapshot'
                WHEN ls.snapshot_tr_id < ll.last_tr_id THEN 'outdated'
                WHEN ls.snapshot_balance != ll.current_balance THEN 'balance_mismatch'
                ELSE 'verified'
            END as status,
            CURRENT_TIMESTAMP as last_updated,
            CASE 
                WHEN EXISTS (
                    SELECT 1 FROM public.ledger l 
                    WHERE l.account_id = acc.account_id 
                      AND l.operation_date > CURRENT_DATE - INTERVAL '3 months'
                ) OR ll.current_balance != 0 THEN 'active'
                ELSE 'inactive'
            END as state,
            ls.snapshot_tr_id,
            ll.last_tr_id,
            ls.snapshot_balance
        FROM dicts.accounts acc
        JOIN latest_ledger ll ON acc.account_id = ll.account_id
        LEFT JOIN latest_snapshot ls ON acc.account_id = ls.account_id
        LEFT JOIN dicts.entities ent ON acc.entity_id = ent.entity_id
        WHERE (ll.current_balance != 0 OR EXISTS (SELECT 1 FROM public.ledger WHERE account_id = acc.account_id))
    )
    SELECT * FROM combined;

    -- 3. Вызываем отдельную функцию логирования
    PERFORM public.log_system_verification();

END;
$$;


--
-- Name: update_receipts_from_transactions(); Type: FUNCTION; Schema: public; Owner: -
--

CREATE FUNCTION public.update_receipts_from_transactions() RETURNS integer
    LANGUAGE plpgsql
    AS $$
DECLARE
    updated_count integer;
BEGIN
    WITH transactions_agg AS (
        SELECT 
            amount, 
            operation_date, 
            array_agg(id::uuid) AS transaction_ids -- Принудительно делаем массив UUID
        FROM public.transactions
        WHERE contragent_to_id IS NOT NULL
        GROUP BY amount, operation_date
    )
    UPDATE processing.receipts r
    SET transaction_id = ta.transaction_ids
    FROM transactions_agg ta
    WHERE r.amount = ta.amount 
      AND r.operation_date = ta.operation_date 
      AND r.transaction_id IS NULL;

    GET DIAGNOSTICS updated_count = ROW_COUNT;
    RETURN updated_count;
END;
$$;


--
-- Name: fn_calculate_total_fabric(); Type: FUNCTION; Schema: texere; Owner: -
--

CREATE FUNCTION texere.fn_calculate_total_fabric() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
DECLARE
    v_total numeric(10, 3) := 0.000;
BEGIN
    -- Проверяем, есть ли элементы в items внутри jsonb materials
    IF NEW.materials IS NOT NULL AND NEW.materials -> 'items' IS NOT NULL THEN
        SELECT COALESCE(SUM(
            COALESCE((val->>'total_consumption_m')::numeric, 0) + 
            COALESCE((val->>'consumption_m')::numeric, 0)
        ), 0.000)
        INTO v_total
        FROM jsonb_each(NEW.materials -> 'items') AS t(key, val);
    END IF;

    -- Записываем результат в наш новый столбец
    NEW.total_fabric_consumption := v_total;
    RETURN NEW;
END;
$$;


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: verified_products; Type: TABLE; Schema: culina; Owner: -
--

CREATE TABLE culina.verified_products (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    barcode character varying(50),
    verified_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL
);


--
-- Name: TABLE verified_products; Type: COMMENT; Schema: culina; Owner: -
--

COMMENT ON TABLE culina.verified_products IS 'Таблица верифицированных продуктов с UUID идентификаторами';


--
-- Name: COLUMN verified_products.meta; Type: COMMENT; Schema: culina; Owner: -
--

COMMENT ON COLUMN culina.verified_products.meta IS 'Метаданные продукта: БЖУ, калорийность, состав на русском языке и бренд';


--
-- Name: box_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.box_register (
    box_id character varying(50) NOT NULL,
    box_name character varying(255),
    box_type character varying(50)
);


--
-- Name: event_type; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.event_type (
    event_type character varying(50) NOT NULL,
    event_type_ru character varying(100)
);


--
-- Name: events_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.events_register (
    code integer NOT NULL,
    event_id uuid DEFAULT public.uuid_generate_v4() NOT NULL,
    object_id character varying(50) NOT NULL,
    event_with_object character varying(50) NOT NULL,
    event_type character varying(50) NOT NULL,
    event_time date NOT NULL,
    created_at timestamp with time zone DEFAULT now() CONSTRAINT events_register_recorded_at_not_null NOT NULL,
    meta jsonb
);


--
-- Name: events_register_code_seq; Type: SEQUENCE; Schema: gardening; Owner: -
--

ALTER TABLE gardening.events_register ALTER COLUMN code ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME gardening.events_register_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: fertilizer; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.fertilizer (
    fertilizer_id character varying(50) NOT NULL,
    fertilizer_name character varying(255),
    description text,
    type character varying(50)
);


--
-- Name: flower_box_history; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.flower_box_history (
    code integer NOT NULL,
    flower_id character varying(50) NOT NULL,
    box_id character varying(50) NOT NULL,
    created_at date
);


--
-- Name: flower_register; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.flower_register (
    code integer NOT NULL,
    flower_id character varying(50) NOT NULL,
    flower_name_ru character varying(255) NOT NULL,
    flower_name_en character varying(255)
);


--
-- Name: garden_state_report; Type: VIEW; Schema: gardening; Owner: -
--

CREATE VIEW gardening.garden_state_report AS
 WITH latest_events AS (
         SELECT DISTINCT ON (events_register.object_id) events_register.object_id AS flower_id,
            events_register.event_type,
            events_register.event_time,
            events_register.created_at,
            events_register.meta
           FROM gardening.events_register
          WHERE ((events_register.event_with_object)::text = 'Flower'::text)
          ORDER BY events_register.object_id, events_register.event_time DESC, events_register.created_at DESC
        )
 SELECT f.code AS flower_code,
    f.flower_id,
    f.flower_name_ru,
    f.flower_name_en,
        CASE
            WHEN ((le.event_type)::text = 'DISPOSAL'::text) THEN 'INACTIVE'::text
            ELSE 'ACTIVE'::text
        END AS current_state,
    COALESCE((le.meta ->> 'lifecycle_stage'::text), 'Unknown'::text) AS current_lifecycle_stage,
    COALESCE((le.meta ->> 'box_id'::text), ( SELECT (events_register.meta ->> 'box_id'::text)
           FROM gardening.events_register
          WHERE (((events_register.object_id)::text = (f.flower_id)::text) AND ((events_register.meta ->> 'box_id'::text) IS NOT NULL))
          ORDER BY events_register.event_time DESC, events_register.created_at DESC
         LIMIT 1)) AS current_box_id,
    ( SELECT br.box_name
           FROM gardening.box_register br
          WHERE ((br.box_id)::text = COALESCE((le.meta ->> 'box_id'::text), ( SELECT (events_register.meta ->> 'box_id'::text)
                   FROM gardening.events_register
                  WHERE (((events_register.object_id)::text = (f.flower_id)::text) AND ((events_register.meta ->> 'box_id'::text) IS NOT NULL))
                  ORDER BY events_register.event_time DESC, events_register.created_at DESC
                 LIMIT 1)))) AS current_box_name,
    le.event_time AS last_observed_at
   FROM (gardening.flower_register f
     LEFT JOIN latest_events le ON (((f.flower_id)::text = (le.flower_id)::text)))
  ORDER BY f.code;


--
-- Name: lifecycle; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.lifecycle (
    lifecycle_name character varying(50) NOT NULL,
    lifecycle_name_ru character varying(100)
);


--
-- Name: notes; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.notes (
    code integer NOT NULL,
    note_name character varying(255) NOT NULL,
    note_id character varying(50) NOT NULL,
    entity_id character varying(50),
    description text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: notes_code_seq; Type: SEQUENCE; Schema: gardening; Owner: -
--

ALTER TABLE gardening.notes ALTER COLUMN code ADD GENERATED ALWAYS AS IDENTITY (
    SEQUENCE NAME gardening.notes_code_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1
);


--
-- Name: planted_seeds; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.planted_seeds (
    code integer NOT NULL,
    seed_name character varying(255),
    seed_planting_id character varying(50) NOT NULL,
    state character varying(50),
    planted_at date,
    seed_quantity integer,
    seed_pack character varying(50),
    box_id character varying(50)
);


--
-- Name: seed_pack; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.seed_pack (
    seed_pack_id character varying(50) NOT NULL,
    seed_pack_name character varying(255),
    flower_latin_name character varying(255),
    seed_quantity character varying(50),
    produced_by character varying(255),
    best_before_date character varying(50),
    pack_date character varying(50),
    price_kzt numeric
);


--
-- Name: state; Type: TABLE; Schema: gardening; Owner: -
--

CREATE TABLE gardening.state (
    state character varying(50) NOT NULL
);


--
-- Name: v_gardening_dashboard; Type: VIEW; Schema: gardening; Owner: -
--

CREATE VIEW gardening.v_gardening_dashboard AS
 WITH last_box_events AS (
         SELECT DISTINCT ON (events_register.object_id) events_register.object_id AS box_id,
            events_register.event_type
           FROM gardening.events_register
          WHERE ((events_register.event_with_object)::text = 'Box'::text)
          ORDER BY events_register.object_id, events_register.event_time DESC, events_register.created_at DESC
        ), free_boxes_inventory AS (
         SELECT b.box_id,
            b.box_type
           FROM ((gardening.box_register b
             LEFT JOIN gardening.garden_state_report r ON ((((b.box_id)::text = r.current_box_id) AND (r.current_state = 'ACTIVE'::text))))
             LEFT JOIN last_box_events lbe ON (((b.box_id)::text = (lbe.box_id)::text)))
          WHERE ((r.flower_id IS NULL) AND ((b.box_id)::text !~~ 'FGB%'::text) AND ((lbe.event_type IS NULL) OR ((lbe.event_type)::text <> ALL (ARRAY['DISPOSAL'::text, 'ARCHIVED'::text]))))
        )
 SELECT ( SELECT count(*) AS count
           FROM gardening.garden_state_report
          WHERE (garden_state_report.current_state = 'ACTIVE'::text)) AS total_flowers,
    ( SELECT count(*) AS count
           FROM gardening.garden_state_report
          WHERE ((garden_state_report.current_state = 'ACTIVE'::text) AND ((garden_state_report.flower_name_ru)::text ~~ 'Пеларгония%'::text) AND (garden_state_report.current_lifecycle_stage = 'Flowering'::text))) AS flowering_count,
    ( SELECT count(*) AS count
           FROM gardening.planted_seeds
          WHERE (((planted_seeds.state)::text = 'ACTIVE'::text) AND (((planted_seeds.seed_name)::text ~~ '%Цикламен%'::text) OR ((planted_seeds.seed_name)::text ~~ '%Авокадо%'::text)))) AS seeds_germinating,
    ( SELECT count(*) AS count
           FROM free_boxes_inventory
          WHERE ((free_boxes_inventory.box_type)::text = 'постоянный'::text)) AS free_const_boxes_count,
    ( SELECT count(*) AS count
           FROM free_boxes_inventory
          WHERE ((free_boxes_inventory.box_type)::text = 'для рассады'::text)) AS free_seedling_boxes_count,
    ( SELECT count(*) AS count
           FROM free_boxes_inventory
          WHERE ((free_boxes_inventory.box_type)::text = 'перевалочный'::text)) AS free_transplant_boxes_count,
    ( SELECT count(DISTINCT events_register.object_id) AS count
           FROM gardening.events_register
          WHERE (((events_register.event_type)::text = ANY (ARRAY['MOLD_DETECTED'::text, 'DRYING_DETECTED'::text])) AND (events_register.event_time >= ('2026-11-06'::date - '14 days'::interval)))) AS active_alerts_count;


--
-- Name: disposal_points; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.disposal_points (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255),
    type character varying(255),
    coordinates public.geography(Point,4326) NOT NULL,
    created_at timestamp with time zone DEFAULT now(),
    contragent_id uuid
);


--
-- Name: disposal_precedents; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.disposal_precedents (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    material_disposition_id uuid NOT NULL,
    precedent_name character varying(255) NOT NULL,
    unit_type character varying(50) NOT NULL,
    quantity numeric(10,2) NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    notes text
);


--
-- Name: material_disposition; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.material_disposition (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    resource_id uuid NOT NULL,
    quantity numeric(15,3) NOT NULL,
    utilized_at date DEFAULT CURRENT_TIMESTAMP,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    device_id uuid,
    weighing_type character varying(50) DEFAULT 'gross'::character varying NOT NULL,
    disposal_point uuid NOT NULL
);


--
-- Name: measuring_devices; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.measuring_devices (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    device_name character varying(255) NOT NULL,
    max_weight numeric(15,3),
    unit character varying(50),
    uncertainty numeric(10,4),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: resource_catalog; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.resource_catalog (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    material_name character varying(255) NOT NULL,
    resource_type character varying(100),
    default_unit character varying(50),
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    container_type character varying(100),
    notes text
);


--
-- Name: time_tracker; Type: TABLE; Schema: infrastructure; Owner: -
--

CREATE TABLE infrastructure.time_tracker (
    id uuid NOT NULL,
    task_name character varying(255) NOT NULL,
    start_time timestamp with time zone NOT NULL,
    end_time timestamp with time zone,
    comment text,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    is_deleted boolean DEFAULT false NOT NULL
);


--
-- Name: v_material_disposition_current_month_report; Type: VIEW; Schema: infrastructure; Owner: -
--

CREATE VIEW infrastructure.v_material_disposition_current_month_report AS
 SELECT (date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone))::date AS interval_start,
    rc.material_name AS resource_name,
    rc.resource_type,
    rc.default_unit AS unit,
    mdv.device_name,
    mdv.uncertainty,
    md.quantity,
    md.utilized_at,
    md.created_at,
    dp.name AS disposal_point_name,
    dp.type AS disposal_point_type
   FROM (((infrastructure.material_disposition md
     JOIN infrastructure.resource_catalog rc ON ((md.resource_id = rc.id)))
     LEFT JOIN infrastructure.measuring_devices mdv ON ((md.device_id = mdv.id)))
     LEFT JOIN infrastructure.disposal_points dp ON ((md.disposal_point = dp.id)))
  WHERE ((md.utilized_at >= date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone)) AND (md.utilized_at < (date_trunc('month'::text, (CURRENT_DATE)::timestamp with time zone) + '1 mon'::interval)));


--
-- Name: v_material_disposition_summary; Type: VIEW; Schema: infrastructure; Owner: -
--

CREATE VIEW infrastructure.v_material_disposition_summary AS
 SELECT 'by_resource'::text AS report_type,
    TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text)) AS report_month,
    rc.material_name AS grouping_key,
    sum(md.quantity) AS total_mass,
    count(md.id) AS total_count
   FROM (infrastructure.material_disposition md
     JOIN infrastructure.resource_catalog rc ON ((md.resource_id = rc.id)))
  GROUP BY (TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text))), rc.material_name
UNION ALL
 SELECT 'by_disposal_point'::text AS report_type,
    TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text)) AS report_month,
    COALESCE(dp.name, 'Не указан'::character varying) AS grouping_key,
    sum(md.quantity) AS total_mass,
    count(md.id) AS total_count
   FROM (infrastructure.material_disposition md
     LEFT JOIN infrastructure.disposal_points dp ON ((md.disposal_point = dp.id)))
  GROUP BY (TRIM(BOTH FROM to_char((md.utilized_at)::timestamp with time zone, 'fmMonth YYYY'::text))), dp.name;


--
-- Name: intakes; Type: TABLE; Schema: medicine; Owner: -
--

CREATE TABLE medicine.intakes (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    intake_date date NOT NULL,
    supplement_id uuid NOT NULL,
    amount integer DEFAULT 1 NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: observations; Type: TABLE; Schema: medicine; Owner: -
--

CREATE TABLE medicine.observations (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    observation_date date NOT NULL,
    notes text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL
);


--
-- Name: schedules; Type: TABLE; Schema: medicine; Owner: -
--

CREATE TABLE medicine.schedules (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    supplement_id uuid NOT NULL,
    start_date date NOT NULL,
    end_date date,
    target_daily_amount integer NOT NULL,
    frequency_per_day integer DEFAULT 1 NOT NULL,
    notification_times time without time zone[] DEFAULT '{}'::time without time zone[] NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    status medicine.schedule_status DEFAULT 'active'::medicine.schedule_status NOT NULL,
    CONSTRAINT check_dates CHECK (((end_date IS NULL) OR (end_date >= start_date))),
    CONSTRAINT check_positive_amount CHECK ((target_daily_amount > 0)),
    CONSTRAINT check_positive_frequency CHECK ((frequency_per_day > 0))
);


--
-- Name: supplements; Type: TABLE; Schema: medicine; Owner: -
--

CREATE TABLE medicine.supplements (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name character varying(255) NOT NULL,
    brand character varying(100),
    unit_type character varying(50) DEFAULT 'таблетка'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    description text,
    ingredients text,
    is_vegan boolean DEFAULT false NOT NULL,
    total_quantity integer,
    dosage_per_unit character varying(100),
    expiration_date_months integer
);


--
-- Name: COLUMN supplements.is_vegan; Type: COMMENT; Schema: medicine; Owner: -
--

COMMENT ON COLUMN medicine.supplements.is_vegan IS 'Флаг строго определен: true - подтвержденный веган, false - содержит животные компоненты / не проверен';


--
-- Name: v_intakes_analysis; Type: VIEW; Schema: medicine; Owner: -
--

CREATE VIEW medicine.v_intakes_analysis AS
 SELECT i.id AS intake_id,
    i.intake_date,
    to_char((i.intake_date)::timestamp with time zone, 'TMDay'::text) AS day_of_week,
    i.supplement_id,
    s.name AS supplement_name,
    s.brand AS supplement_brand,
    s.unit_type,
    i.amount AS units_taken,
    dense_rank() OVER (PARTITION BY i.supplement_id ORDER BY i.intake_date) AS course_day_number,
    sum(i.amount) OVER (PARTITION BY i.supplement_id ORDER BY i.intake_date ROWS BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW) AS cumulative_total_taken,
    s.is_vegan,
    i.created_at AS logged_at
   FROM (medicine.intakes i
     JOIN medicine.supplements s ON ((i.supplement_id = s.id)));


--
-- Name: v_monthly_supplements_summary; Type: VIEW; Schema: medicine; Owner: -
--

CREATE VIEW medicine.v_monthly_supplements_summary AS
 SELECT s.name AS supplement_name,
    s.brand AS supplement_brand,
    s.unit_type,
    count(DISTINCT i.intake_date) AS days_taken_count,
    sum(i.amount) AS total_units_taken,
    round(avg(i.amount), 2) AS avg_daily_dosage,
    min(i.intake_date) AS first_intake_in_period,
    max(i.intake_date) AS last_intake_in_period
   FROM (medicine.intakes i
     JOIN medicine.supplements s ON ((i.supplement_id = s.id)))
  WHERE (i.intake_date >= (CURRENT_DATE - '1 mon'::interval))
  GROUP BY s.id, s.name, s.brand, s.unit_type;


--
-- Name: metadata; Type: TABLE; Schema: projects; Owner: -
--

CREATE TABLE projects.metadata (
    project_id uuid NOT NULL,
    title character varying(255) NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP
);


--
-- Name: projects; Type: TABLE; Schema: repair; Owner: -
--

CREATE TABLE repair.projects (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    name_ru character varying(255) NOT NULL,
    name_en character varying(255) NOT NULL,
    status character varying(50) DEFAULT 'planning'::character varying NOT NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    completed_at date
);


--
-- Name: v_project_consolidated_report; Type: VIEW; Schema: repair; Owner: -
--

CREATE VIEW repair.v_project_consolidated_report AS
 SELECT count(*) AS total_projects,
    count(*) FILTER (WHERE ((status)::text = 'completed'::text)) AS completed_projects,
    count(*) FILTER (WHERE ((status)::text = 'planning'::text)) AS planning_projects,
    count(*) FILTER (WHERE (((meta ->> 'outsource'::text))::boolean = true)) AS outsourced_count,
    round((((count(*) FILTER (WHERE (((meta ->> 'outsource'::text))::boolean = true)))::numeric / (count(*))::numeric) * (100)::numeric), 1) AS outsource_share_percent,
    count(*) FILTER (WHERE ((((meta ->> 'disposed'::text))::boolean = true) OR ((meta ->> 'disposal_status'::text) = 'disposed'::text))) AS disposed_count
   FROM repair.projects;


--
-- Name: consumables_inventory; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.consumables_inventory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    consumable_type character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    merchant_name character varying(255),
    unit character varying(20) DEFAULT 'шт'::character varying NOT NULL,
    initial_quantity numeric(10,3) NOT NULL,
    current_balance numeric(10,3) NOT NULL,
    total_cost_kzt numeric(12,2) DEFAULT 0.00 NOT NULL,
    price_per_unit numeric(12,2) GENERATED ALWAYS AS (
CASE
    WHEN (initial_quantity > (0)::numeric) THEN (total_cost_kzt / initial_quantity)
    ELSE 0.00
END) STORED,
    transaction_uuid uuid,
    tx_code integer,
    entry_date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL,
    CONSTRAINT chk_consumables_balance_limit CHECK ((current_balance <= initial_quantity)),
    CONSTRAINT consumables_inventory_current_balance_check CHECK ((current_balance >= (0)::numeric)),
    CONSTRAINT consumables_inventory_initial_quantity_check CHECK ((initial_quantity >= (0)::numeric)),
    CONSTRAINT consumables_inventory_total_cost_kzt_check CHECK ((total_cost_kzt >= (0)::numeric))
);


--
-- Name: external_services; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.external_services (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    service_type character varying(100) NOT NULL,
    description text NOT NULL,
    contractor_name character varying(255),
    total_cost_kzt numeric(12,2) DEFAULT 0.00 NOT NULL,
    transaction_uuid uuid,
    tx_code integer,
    entry_date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL,
    CONSTRAINT external_services_total_cost_kzt_check CHECK ((total_cost_kzt >= (0)::numeric))
);


--
-- Name: fabric_treatment_protocols; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.fabric_treatment_protocols (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    fabric_type character varying(150) NOT NULL,
    density_gsm integer,
    pre_soaking_required boolean DEFAULT true,
    soaking_details text,
    washing_temperature_c integer DEFAULT 30,
    washing_duration_minutes integer,
    spin_rpm integer DEFAULT 0,
    detergents_meta jsonb DEFAULT '{}'::jsonb,
    drying_method text,
    ironing_modes text,
    critical_issues text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    CONSTRAINT chk_spin_rpm CHECK ((spin_rpm >= 0)),
    CONSTRAINT chk_washing_temp CHECK (((washing_temperature_c >= 0) AND (washing_temperature_c <= 95)))
);


--
-- Name: TABLE fabric_treatment_protocols; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON TABLE texere.fabric_treatment_protocols IS 'База знаний и протоколы технологических процессов ВТО, замачивания и стирки отрезов для предотвращения дефектов (заломов, потери цвета).';


--
-- Name: hardware_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.hardware_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    parent_id uuid,
    product_id uuid NOT NULL,
    hardware_list jsonb DEFAULT '[]'::jsonb NOT NULL,
    has_custom_work boolean DEFAULT false NOT NULL,
    comments text,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL
);


--
-- Name: materials_inventory; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.materials_inventory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    material_type texere.mat_type NOT NULL,
    name character varying(255) NOT NULL,
    merchant_name character varying(255),
    unit character varying(20) DEFAULT 'м'::character varying NOT NULL,
    initial_quantity numeric(10,3) NOT NULL,
    current_balance numeric(10,3) NOT NULL,
    total_cost_kzt numeric(12,2) DEFAULT 0.00 NOT NULL,
    price_per_unit numeric(12,2) GENERATED ALWAYS AS (
CASE
    WHEN (initial_quantity > (0)::numeric) THEN (total_cost_kzt / initial_quantity)
    ELSE 0.00
END) STORED,
    transaction_uuid uuid,
    tx_code integer,
    entry_date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL,
    CONSTRAINT chk_balance_limit CHECK ((current_balance <= initial_quantity)),
    CONSTRAINT materials_inventory_current_balance_check CHECK ((current_balance >= (0)::numeric)),
    CONSTRAINT materials_inventory_initial_quantity_check CHECK ((initial_quantity >= (0)::numeric)),
    CONSTRAINT materials_inventory_total_cost_kzt_check CHECK ((total_cost_kzt >= (0)::numeric))
);


--
-- Name: patterns_inventory; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.patterns_inventory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    pattern_type character varying(50) DEFAULT 'Физическая'::character varying NOT NULL,
    product_category character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    size_range character varying(100),
    storage_location character varying(255),
    merchant_name character varying(255),
    unit character varying(20) DEFAULT 'компл'::character varying NOT NULL,
    initial_quantity numeric(10,3) DEFAULT 1.000 NOT NULL,
    current_balance numeric(10,3) DEFAULT 1.000 NOT NULL,
    total_cost_kzt numeric(12,2) DEFAULT 0.00 NOT NULL,
    price_per_unit numeric(12,2) GENERATED ALWAYS AS (
CASE
    WHEN (initial_quantity > (0)::numeric) THEN (total_cost_kzt / initial_quantity)
    ELSE 0.00
END) STORED,
    transaction_uuid uuid,
    tx_code integer,
    entry_date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL,
    CONSTRAINT chk_patterns_balance_limit CHECK ((current_balance <= initial_quantity)),
    CONSTRAINT patterns_inventory_current_balance_check CHECK ((current_balance >= (0)::numeric)),
    CONSTRAINT patterns_inventory_initial_quantity_check CHECK ((initial_quantity >= (0)::numeric)),
    CONSTRAINT patterns_inventory_total_cost_kzt_check CHECK ((total_cost_kzt >= (0)::numeric))
);


--
-- Name: product_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.product_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title character varying(255) NOT NULL,
    item_count integer DEFAULT 1 CONSTRAINT product_registry_quantity_not_null NOT NULL,
    materials jsonb DEFAULT '{}'::jsonb NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    completion_date date,
    quality_rating integer,
    comments text,
    project_cost_kzt numeric(12,2),
    macro_category character varying(100),
    category_l2 character varying(100),
    subcategory_l3 character varying(100),
    item_size character varying(50) DEFAULT 'Custom Size'::character varying NOT NULL,
    gender character varying(20),
    size_standard character varying(50),
    batches_count integer NOT NULL,
    production_type character varying(50) NOT NULL,
    using_status character varying(50),
    fabric_consumption numeric(10,2),
    total_fabric_consumption numeric(10,3) DEFAULT 0.000 NOT NULL,
    CONSTRAINT chk_quality_range CHECK (((quality_rating >= 1) AND (quality_rating <= 10)))
);


--
-- Name: COLUMN product_registry.fabric_consumption; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON COLUMN texere.product_registry.fabric_consumption IS 'Расход ткани (например, в метрах или килограммах)';


--
-- Name: COLUMN product_registry.total_fabric_consumption; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON COLUMN texere.product_registry.total_fabric_consumption IS 'Автоматически рассчитанный суммарный расход ткани (в метрах) на основе поля materials';


--
-- Name: raw_transactions; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.raw_transactions (
    tx_date date,
    tx_code integer,
    merchant character varying(255),
    status_desc character varying(100),
    status character varying(50),
    category character varying(100),
    description text,
    amount numeric(12,2),
    project character varying(255),
    uuid1 uuid,
    uuid2 uuid,
    uuid3 uuid,
    uuid4 uuid
);


--
-- Name: tools_inventory; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.tools_inventory (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    tool_type character varying(100) NOT NULL,
    name character varying(255) NOT NULL,
    merchant_name character varying(255),
    unit character varying(20) DEFAULT 'шт'::character varying NOT NULL,
    initial_quantity numeric(10,3) NOT NULL,
    scrapped_quantity numeric(10,3) DEFAULT 0.000 NOT NULL,
    total_cost_kzt numeric(12,2) DEFAULT 0.00 NOT NULL,
    price_per_unit numeric(12,2) GENERATED ALWAYS AS (
CASE
    WHEN (initial_quantity > (0)::numeric) THEN (total_cost_kzt / initial_quantity)
    ELSE 0.00
END) STORED,
    condition_status character varying(100) DEFAULT 'В работе'::character varying,
    transaction_uuid uuid,
    tx_code integer,
    entry_date date DEFAULT CURRENT_DATE NOT NULL,
    created_at timestamp without time zone DEFAULT clock_timestamp() NOT NULL,
    CONSTRAINT chk_tools_scrapped_limit CHECK ((scrapped_quantity <= initial_quantity)),
    CONSTRAINT tools_inventory_initial_quantity_check CHECK ((initial_quantity >= (0)::numeric)),
    CONSTRAINT tools_inventory_scrapped_quantity_check CHECK ((scrapped_quantity >= (0)::numeric)),
    CONSTRAINT tools_inventory_total_cost_kzt_check CHECK ((total_cost_kzt >= (0)::numeric))
);


--
-- Name: reconciled_transactions_summary; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.reconciled_transactions_summary AS
 SELECT t.tx_date,
    t.tx_code,
    t.merchant,
    t.amount AS original_amount,
    t.description AS original_description,
    t.uuid2 AS transaction_uuid,
    'materials_inventory'::text AS target_table,
    m.id AS record_id,
    m.name AS target_item_name,
    m.total_cost_kzt AS recorded_cost
   FROM (texere.raw_transactions t
     JOIN texere.materials_inventory m ON (((m.transaction_uuid = t.uuid2) OR (m.tx_code = t.tx_code))))
UNION ALL
 SELECT t.tx_date,
    t.tx_code,
    t.merchant,
    t.amount AS original_amount,
    t.description AS original_description,
    t.uuid2 AS transaction_uuid,
    'consumables_inventory'::text AS target_table,
    c.id AS record_id,
    c.name AS target_item_name,
    c.total_cost_kzt AS recorded_cost
   FROM (texere.raw_transactions t
     JOIN texere.consumables_inventory c ON (((c.transaction_uuid = t.uuid2) OR (c.tx_code = t.tx_code))))
UNION ALL
 SELECT t.tx_date,
    t.tx_code,
    t.merchant,
    t.amount AS original_amount,
    t.description AS original_description,
    t.uuid2 AS transaction_uuid,
    'patterns_inventory'::text AS target_table,
    p.id AS record_id,
    p.name AS target_item_name,
    p.total_cost_kzt AS recorded_cost
   FROM (texere.raw_transactions t
     JOIN texere.patterns_inventory p ON (((p.transaction_uuid = t.uuid2) OR (p.tx_code = t.tx_code))))
UNION ALL
 SELECT t.tx_date,
    t.tx_code,
    t.merchant,
    t.amount AS original_amount,
    t.description AS original_description,
    t.uuid2 AS transaction_uuid,
    'tools_inventory'::text AS target_table,
    tool.id AS record_id,
    tool.name AS target_item_name,
    tool.total_cost_kzt AS recorded_cost
   FROM (texere.raw_transactions t
     JOIN texere.tools_inventory tool ON (((tool.transaction_uuid = t.uuid2) OR (tool.tx_code = t.tx_code))))
UNION ALL
 SELECT t.tx_date,
    t.tx_code,
    t.merchant,
    t.amount AS original_amount,
    t.description AS original_description,
    t.uuid2 AS transaction_uuid,
    'external_services'::text AS target_table,
    s.id AS record_id,
    (((s.service_type)::text || ': '::text) || s.description) AS target_item_name,
    s.total_cost_kzt AS recorded_cost
   FROM (texere.raw_transactions t
     JOIN texere.external_services s ON (((s.transaction_uuid = t.uuid2) OR (s.tx_code = t.tx_code))));


--
-- Name: repair_registry; Type: TABLE; Schema: texere; Owner: -
--

CREATE TABLE texere.repair_registry (
    id uuid DEFAULT gen_random_uuid() NOT NULL,
    title character varying(255) NOT NULL,
    item_count integer DEFAULT 1 NOT NULL,
    defect_description text NOT NULL,
    work_performed text,
    materials jsonb DEFAULT '{}'::jsonb NOT NULL,
    meta jsonb DEFAULT '{}'::jsonb NOT NULL,
    receipt_date date DEFAULT CURRENT_DATE NOT NULL,
    completion_date date,
    quality_rating integer,
    comments text,
    repair_cost_kzt numeric(12,2),
    macro_category character varying(100),
    category_l2 character varying(100),
    subcategory_l3 character varying(100),
    item_size character varying(50) DEFAULT 'Custom Size'::character varying NOT NULL,
    gender character varying(20),
    size_standard character varying(50),
    origin_country character varying(100),
    repair_status character varying(50) DEFAULT 'Pending'::character varying NOT NULL,
    CONSTRAINT chk_repair_quality_range CHECK (((quality_rating >= 1) AND (quality_rating <= 10)))
);


--
-- Name: unreconciled_transactions; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.unreconciled_transactions AS
 SELECT tx_date,
    tx_code,
    merchant,
    amount,
    description,
    uuid2
   FROM texere.raw_transactions t
  WHERE (NOT (EXISTS ( SELECT 1
           FROM texere.materials_inventory m
          WHERE ((m.transaction_uuid = t.uuid2) OR (m.tx_code = t.tx_code))
        UNION ALL
         SELECT 1
           FROM texere.consumables_inventory c
          WHERE ((c.transaction_uuid = t.uuid2) OR (c.tx_code = t.tx_code))
        UNION ALL
         SELECT 1
           FROM texere.patterns_inventory p
          WHERE ((p.transaction_uuid = t.uuid2) OR (p.tx_code = t.tx_code))
        UNION ALL
         SELECT 1
           FROM texere.tools_inventory tool
          WHERE ((tool.transaction_uuid = t.uuid2) OR (tool.tx_code = t.tx_code))
        UNION ALL
         SELECT 1
           FROM texere.external_services s
          WHERE ((s.transaction_uuid = t.uuid2) OR (s.tx_code = t.tx_code)))));


--
-- Name: v_international_media_catalog; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_international_media_catalog AS
 WITH expanded_fabrics AS (
         SELECT product_registry.id,
            COALESCE(NULLIF(product_registry.total_fabric_consumption, 0.000), ( SELECT sum(((fabric.value ->> 'consumption_m'::text))::numeric) AS sum
                   FROM jsonb_array_elements(
                        CASE
                            WHEN (jsonb_typeof((product_registry.materials -> 'fabrics'::text)) = 'array'::text) THEN (product_registry.materials -> 'fabrics'::text)
                            ELSE '[]'::jsonb
                        END) fabric(value)), ((product_registry.meta ->> 'fabric_cutting_length_m'::text))::numeric, NULLIF(("substring"(((product_registry.meta -> 'normalization_stamp'::text) ->> 'consumption_note'::text), 'Расход ([0-9.]+)'::text))::numeric, 0.000), NULLIF(("substring"(product_registry.comments, 'расход ([0-9.]+)'::text))::numeric, 0.000), NULLIF(("substring"(product_registry.comments, 'велюр Visavi 30 \(([0-9.]+)\)'::text))::numeric, 0.000), (0)::numeric) AS total_project_consumption_raw
           FROM texere.product_registry
        ), item_counts AS (
         SELECT pr_counts.id,
            pr_counts.item_count AS actual_item_count
           FROM texere.product_registry pr_counts
        )
 SELECT
        CASE
            WHEN ((pr.id = '9b594a7e-9e9a-4f00-b1cf-09feadba13c7'::uuid) AND ((pr.macro_category)::text = 'Upcycling & Accessories'::text)) THEN '9b594a7e-9e9a-4f00-b1cf-09feadba13c8'::uuid
            ELSE pr.id
        END AS product_id,
    COALESCE((pr.meta ->> 'title_en'::text), (pr.title)::text) AS title_en,
        CASE
            WHEN ((pr.macro_category)::text = ANY (ARRAY[('Home Textiles'::character varying)::text, ('Interior'::character varying)::text, ('Home Textiles & Interior'::character varying)::text])) THEN ('Home Textiles & Interior'::text)::character varying
            WHEN ((pr.macro_category)::text = ANY (ARRAY[('Apparel'::character varying)::text, ('Tops'::character varying)::text, ('Bottoms'::character varying)::text])) THEN ('Apparel (Tops & Bottoms)'::text)::character varying
            WHEN (((pr.macro_category)::text = ANY (ARRAY[('Accessories'::character varying)::text, ('Upcycling'::character varying)::text])) OR (((pr.meta ->> 'is_upcycling'::text))::boolean = true)) THEN ('Upcycling & Accessories'::text)::character varying
            ELSE pr.macro_category
        END AS macro_category,
    pr.category_l2,
    pr.subcategory_l3,
    COALESCE((pr.meta ->> 'suit_set_code'::text), 'Single Item'::text) AS suit_set_code,
        CASE
            WHEN (pr.quality_rating <= 5) THEN 'Defect'::text
            WHEN (((pr.using_status)::text ~~ '%в архиве%'::text) OR ((pr.using_status)::text ~~ '%в хранении%'::text)) THEN 'In Storage'::text
            WHEN (((pr.using_status)::text ~~ '%утеряно%'::text) OR ((pr.using_status)::text ~~ '%изношено%'::text)) THEN 'Worn Out / Lost (From Gifted)'::text
            WHEN (((pr.using_status)::text ~~ '%подарено%'::text) AND ((pr.using_status)::text ~~ '%активно используется%'::text)) THEN 'Gifted & Actively Used'::text
            WHEN (((pr.using_status)::text ~~ '%подарено%'::text) OR ((pr.meta ->> 'gift_recipient'::text) IS NOT NULL) OR ((pr.meta ->> 'recipient'::text) IS NOT NULL)) THEN 'Gifted (In Wardrobe / Used)'::text
            ELSE 'Actively Used'::text
        END AS item_status,
    pr.using_status AS usage,
        CASE
            WHEN (((pr.gender)::text = 'male'::text) OR ((pr.gender)::text = 'Мужская'::text)) THEN 'Men'::text
            WHEN (((pr.gender)::text = 'female'::text) OR ((pr.gender)::text = 'Женская'::text)) THEN 'Women'::text
            ELSE 'Unisex'::text
        END AS target_audience,
    pr.item_size,
    pr.size_standard,
    ic.actual_item_count AS items,
    pr.batches_count,
        CASE
            WHEN (((pr.meta ->> 'is_upcycling'::text))::boolean = true) THEN 'Upcycling'::text
            ELSE 'New Materials'::text
        END AS production_type,
    COALESCE(pr.completion_date, (((pr.meta -> 'workflow_timestamps'::text) ->> 'completion_approx_date'::text))::date) AS completed_at,
    (ef.total_project_consumption_raw)::numeric(10,3) AS total_project_consumption_m
   FROM ((texere.product_registry pr
     JOIN expanded_fabrics ef ON ((pr.id = ef.id)))
     JOIN item_counts ic ON ((pr.id = ic.id)))
  WHERE (((pr.meta ->> 'data_checked'::text))::boolean = true);


--
-- Name: v_product_fabric_analytics; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_product_fabric_analytics AS
 SELECT id AS product_id,
    title AS product_title,
    (meta ->> 'title_en'::text) AS product_title_en,
    completion_date,
    item_count,
    macro_category,
    category_l2,
    subcategory_l3,
    item_size,
    production_type,
    using_status,
        CASE
            WHEN ((materials -> 'items'::text) IS NOT NULL) THEN ( SELECT COALESCE(sum((COALESCE(((t.val ->> 'total_consumption_m'::text))::numeric, (0)::numeric) + COALESCE(((t.val ->> 'consumption_m'::text))::numeric, (0)::numeric))), 0.000) AS "coalesce"
               FROM jsonb_each((product_registry.materials -> 'items'::text)) t(key, val))
            WHEN (((materials -> 'fabrics'::text) IS NOT NULL) AND (jsonb_typeof((materials -> 'fabrics'::text)) = 'array'::text)) THEN ( SELECT COALESCE(sum(COALESCE(((elem.value ->> 'consumption_m'::text))::numeric, (0)::numeric)), 0.000) AS "coalesce"
               FROM jsonb_array_elements((product_registry.materials -> 'fabrics'::text)) elem(value))
            ELSE 0.000
        END AS total_fabric_consumption
   FROM texere.product_registry;


--
-- Name: VIEW v_product_fabric_analytics; Type: COMMENT; Schema: texere; Owner: -
--

COMMENT ON VIEW texere.v_product_fabric_analytics IS 'Постоянное аналитическое представление для контроля расхода тканей, статусов использования изделий и категорийного анализа (с поддержкой title_en)';


--
-- Name: v_project_summary_post; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_project_summary_post AS
 SELECT id AS project_id,
    title AS project_title,
    COALESCE((meta ->> 'title_en'::text), (title)::text) AS project_title_en,
    macro_category,
    category_l2,
    subcategory_l3,
    item_size,
    size_standard,
    item_count AS quantity,
    batches_count,
    production_type,
    using_status,
    quality_rating,
    project_cost_kzt,
    COALESCE(completion_date, (((meta -> 'workflow_timestamps'::text) ->> 'completion_approx_date'::text))::date) AS completion_date,
        CASE
            WHEN (quality_rating <= 5) THEN 'Требует доработки / Опыт'::text
            WHEN (((meta ->> 'gift_recipient'::text) IS NOT NULL) OR ((meta ->> 'recipient'::text) IS NOT NULL)) THEN 'Подарочный проект'::text
            ELSE 'Основная линейка'::text
        END AS project_category_status
   FROM texere.product_registry
  WHERE (((meta ->> 'data_checked'::text))::boolean = true);


--
-- Name: v_textile_production_metrics; Type: VIEW; Schema: texere; Owner: -
--

CREATE VIEW texere.v_textile_production_metrics AS
 SELECT macro_category,
    count(DISTINCT product_id) AS total_projects,
    sum(items) AS total_items_produced,
    round(sum(total_project_consumption_m), 2) AS total_fabric_consumed_m,
    round(avg(total_project_consumption_m), 2) AS avg_consumption_per_project
   FROM texere.v_international_media_catalog
  GROUP BY macro_category;


--
-- Name: verified_products verified_products_barcode_key; Type: CONSTRAINT; Schema: culina; Owner: -
--

ALTER TABLE ONLY culina.verified_products
    ADD CONSTRAINT verified_products_barcode_key UNIQUE (barcode);


--
-- Name: verified_products verified_products_pkey; Type: CONSTRAINT; Schema: culina; Owner: -
--

ALTER TABLE ONLY culina.verified_products
    ADD CONSTRAINT verified_products_pkey PRIMARY KEY (id);


--
-- Name: box_register box_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.box_register
    ADD CONSTRAINT box_register_pkey PRIMARY KEY (box_id);


--
-- Name: event_type event_type_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.event_type
    ADD CONSTRAINT event_type_pkey PRIMARY KEY (event_type);


--
-- Name: events_register events_register_event_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_event_id_key UNIQUE (event_id);


--
-- Name: events_register events_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_pkey PRIMARY KEY (code);


--
-- Name: fertilizer fertilizer_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.fertilizer
    ADD CONSTRAINT fertilizer_pkey PRIMARY KEY (fertilizer_id);


--
-- Name: flower_box_history flower_box_history_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_box_history
    ADD CONSTRAINT flower_box_history_pkey PRIMARY KEY (code);


--
-- Name: flower_register flower_register_flower_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_register
    ADD CONSTRAINT flower_register_flower_id_key UNIQUE (flower_id);


--
-- Name: flower_register flower_register_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_register
    ADD CONSTRAINT flower_register_pkey PRIMARY KEY (code);


--
-- Name: lifecycle lifecycle_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.lifecycle
    ADD CONSTRAINT lifecycle_pkey PRIMARY KEY (lifecycle_name);


--
-- Name: notes notes_note_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.notes
    ADD CONSTRAINT notes_note_id_key UNIQUE (note_id);


--
-- Name: notes notes_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.notes
    ADD CONSTRAINT notes_pkey PRIMARY KEY (code);


--
-- Name: planted_seeds planted_seeds_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_pkey PRIMARY KEY (code);


--
-- Name: planted_seeds planted_seeds_seed_planting_id_key; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_seed_planting_id_key UNIQUE (seed_planting_id);


--
-- Name: seed_pack seed_pack_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.seed_pack
    ADD CONSTRAINT seed_pack_pkey PRIMARY KEY (seed_pack_id);


--
-- Name: state state_pkey; Type: CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.state
    ADD CONSTRAINT state_pkey PRIMARY KEY (state);


--
-- Name: disposal_points disposal_points_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.disposal_points
    ADD CONSTRAINT disposal_points_pkey PRIMARY KEY (id);


--
-- Name: disposal_precedents disposal_precedents_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.disposal_precedents
    ADD CONSTRAINT disposal_precedents_pkey PRIMARY KEY (id);


--
-- Name: material_disposition material_disposition_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.material_disposition
    ADD CONSTRAINT material_disposition_pkey PRIMARY KEY (id);


--
-- Name: measuring_devices measuring_devices_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.measuring_devices
    ADD CONSTRAINT measuring_devices_pkey PRIMARY KEY (id);


--
-- Name: resource_catalog resource_catalog_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.resource_catalog
    ADD CONSTRAINT resource_catalog_pkey PRIMARY KEY (id);


--
-- Name: time_tracker time_tracker_pkey; Type: CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.time_tracker
    ADD CONSTRAINT time_tracker_pkey PRIMARY KEY (id);


--
-- Name: intakes intakes_pkey; Type: CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.intakes
    ADD CONSTRAINT intakes_pkey PRIMARY KEY (id);


--
-- Name: observations observations_pkey; Type: CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.observations
    ADD CONSTRAINT observations_pkey PRIMARY KEY (id);


--
-- Name: schedules schedules_pkey; Type: CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.schedules
    ADD CONSTRAINT schedules_pkey PRIMARY KEY (id);


--
-- Name: supplements supplements_pkey; Type: CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.supplements
    ADD CONSTRAINT supplements_pkey PRIMARY KEY (id);


--
-- Name: metadata projects_metadata_pkey; Type: CONSTRAINT; Schema: projects; Owner: -
--

ALTER TABLE ONLY projects.metadata
    ADD CONSTRAINT projects_metadata_pkey PRIMARY KEY (project_id);


--
-- Name: projects projects_pkey; Type: CONSTRAINT; Schema: repair; Owner: -
--

ALTER TABLE ONLY repair.projects
    ADD CONSTRAINT projects_pkey PRIMARY KEY (id);


--
-- Name: consumables_inventory consumables_inventory_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.consumables_inventory
    ADD CONSTRAINT consumables_inventory_pkey PRIMARY KEY (id);


--
-- Name: external_services external_services_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.external_services
    ADD CONSTRAINT external_services_pkey PRIMARY KEY (id);


--
-- Name: hardware_registry hardware_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.hardware_registry
    ADD CONSTRAINT hardware_registry_pkey PRIMARY KEY (id);


--
-- Name: materials_inventory materials_inventory_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.materials_inventory
    ADD CONSTRAINT materials_inventory_pkey PRIMARY KEY (id);


--
-- Name: patterns_inventory patterns_inventory_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.patterns_inventory
    ADD CONSTRAINT patterns_inventory_pkey PRIMARY KEY (id);


--
-- Name: fabric_treatment_protocols pk_fabric_treatment_protocols; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.fabric_treatment_protocols
    ADD CONSTRAINT pk_fabric_treatment_protocols PRIMARY KEY (id);


--
-- Name: product_registry product_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.product_registry
    ADD CONSTRAINT product_registry_pkey PRIMARY KEY (id);


--
-- Name: repair_registry repair_registry_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.repair_registry
    ADD CONSTRAINT repair_registry_pkey PRIMARY KEY (id);


--
-- Name: tools_inventory tools_inventory_pkey; Type: CONSTRAINT; Schema: texere; Owner: -
--

ALTER TABLE ONLY texere.tools_inventory
    ADD CONSTRAINT tools_inventory_pkey PRIMARY KEY (id);


--
-- Name: idx_disposition_resource_date; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX idx_disposition_resource_date ON infrastructure.material_disposition USING btree (resource_id, utilized_at);


--
-- Name: idx_resource_name; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX idx_resource_name ON infrastructure.resource_catalog USING btree (material_name);


--
-- Name: idx_time_tracker_updated_at; Type: INDEX; Schema: infrastructure; Owner: -
--

CREATE INDEX idx_time_tracker_updated_at ON infrastructure.time_tracker USING btree (updated_at);


--
-- Name: idx_projects_metadata_meta; Type: INDEX; Schema: projects; Owner: -
--

CREATE INDEX idx_projects_metadata_meta ON projects.metadata USING gin (meta);


--
-- Name: idx_consumables_inv_active_balance; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_consumables_inv_active_balance ON texere.consumables_inventory USING btree (current_balance) WHERE (current_balance > (0)::numeric);


--
-- Name: idx_consumables_inv_tx_code; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_consumables_inv_tx_code ON texere.consumables_inventory USING btree (tx_code) WHERE (tx_code IS NOT NULL);


--
-- Name: idx_consumables_inv_tx_link; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_consumables_inv_tx_link ON texere.consumables_inventory USING btree (transaction_uuid) WHERE (transaction_uuid IS NOT NULL);


--
-- Name: idx_consumables_inv_type_name; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_consumables_inv_type_name ON texere.consumables_inventory USING btree (consumable_type, name);


--
-- Name: idx_external_services_lookup; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_external_services_lookup ON texere.external_services USING btree (service_type, contractor_name);


--
-- Name: idx_external_services_tx_code; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_external_services_tx_code ON texere.external_services USING btree (tx_code) WHERE (tx_code IS NOT NULL);


--
-- Name: idx_hardware_registry_list; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_list ON texere.hardware_registry USING gin (hardware_list);


--
-- Name: idx_hardware_registry_parent_id; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_parent_id ON texere.hardware_registry USING btree (parent_id);


--
-- Name: idx_hardware_registry_product_id; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_hardware_registry_product_id ON texere.hardware_registry USING btree (product_id);


--
-- Name: idx_materials_inv_active_balance; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_materials_inv_active_balance ON texere.materials_inventory USING btree (current_balance) WHERE (current_balance > (0)::numeric);


--
-- Name: idx_materials_inv_tx_code; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_materials_inv_tx_code ON texere.materials_inventory USING btree (tx_code) WHERE (tx_code IS NOT NULL);


--
-- Name: idx_materials_inv_tx_link; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_materials_inv_tx_link ON texere.materials_inventory USING btree (transaction_uuid) WHERE (transaction_uuid IS NOT NULL);


--
-- Name: idx_materials_inv_type_name; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_materials_inv_type_name ON texere.materials_inventory USING btree (material_type, name);


--
-- Name: idx_patterns_inv_active_balance; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_patterns_inv_active_balance ON texere.patterns_inventory USING btree (current_balance) WHERE (current_balance > (0)::numeric);


--
-- Name: idx_patterns_inv_lookup; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_patterns_inv_lookup ON texere.patterns_inventory USING btree (product_category, pattern_type, name);


--
-- Name: idx_patterns_inv_tx_code; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_patterns_inv_tx_code ON texere.patterns_inventory USING btree (tx_code) WHERE (tx_code IS NOT NULL);


--
-- Name: idx_patterns_inv_tx_link; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_patterns_inv_tx_link ON texere.patterns_inventory USING btree (transaction_uuid) WHERE (transaction_uuid IS NOT NULL);


--
-- Name: idx_product_registry_cat_l2; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_cat_l2 ON texere.product_registry USING btree (category_l2);


--
-- Name: idx_product_registry_completion_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_completion_date ON texere.product_registry USING btree (completion_date);


--
-- Name: idx_product_registry_gender; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_gender ON texere.product_registry USING btree (gender);


--
-- Name: idx_product_registry_item_size; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_item_size ON texere.product_registry USING btree (item_size);


--
-- Name: idx_product_registry_item_size_standard; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_item_size_standard ON texere.product_registry USING btree (size_standard);


--
-- Name: idx_product_registry_macro_cat; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_macro_cat ON texere.product_registry USING btree (macro_category);


--
-- Name: idx_product_registry_materials; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_materials ON texere.product_registry USING gin (materials);


--
-- Name: idx_product_registry_meta; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_meta ON texere.product_registry USING gin (meta);


--
-- Name: idx_product_registry_production_type; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_production_type ON texere.product_registry USING btree (production_type);


--
-- Name: idx_product_registry_project_cost; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_project_cost ON texere.product_registry USING btree (project_cost_kzt);


--
-- Name: idx_product_registry_total_fabric_consumption; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_product_registry_total_fabric_consumption ON texere.product_registry USING btree (total_fabric_consumption);


--
-- Name: idx_repair_registry_cat_l2; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_cat_l2 ON texere.repair_registry USING btree (category_l2);


--
-- Name: idx_repair_registry_completion_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_completion_date ON texere.repair_registry USING btree (completion_date);


--
-- Name: idx_repair_registry_gender; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_gender ON texere.repair_registry USING btree (gender);


--
-- Name: idx_repair_registry_materials; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_materials ON texere.repair_registry USING gin (materials);


--
-- Name: idx_repair_registry_meta; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_meta ON texere.repair_registry USING gin (meta);


--
-- Name: idx_repair_registry_receipt_date; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_receipt_date ON texere.repair_registry USING btree (receipt_date);


--
-- Name: idx_repair_registry_status; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_repair_registry_status ON texere.repair_registry USING btree (repair_status);


--
-- Name: idx_tools_inv_active; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_tools_inv_active ON texere.tools_inventory USING btree (initial_quantity) WHERE (initial_quantity > scrapped_quantity);


--
-- Name: idx_tools_inv_tx_code; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_tools_inv_tx_code ON texere.tools_inventory USING btree (tx_code) WHERE (tx_code IS NOT NULL);


--
-- Name: idx_tools_inv_tx_link; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_tools_inv_tx_link ON texere.tools_inventory USING btree (transaction_uuid) WHERE (transaction_uuid IS NOT NULL);


--
-- Name: idx_tools_inv_type_name; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_tools_inv_type_name ON texere.tools_inventory USING btree (tool_type, name);


--
-- Name: idx_treatment_protocols_fabric_type; Type: INDEX; Schema: texere; Owner: -
--

CREATE INDEX idx_treatment_protocols_fabric_type ON texere.fabric_treatment_protocols USING btree (fabric_type);


--
-- Name: intakes trg_biu_check_daily_supplement_limit; Type: TRIGGER; Schema: medicine; Owner: -
--

CREATE TRIGGER trg_biu_check_daily_supplement_limit BEFORE INSERT OR UPDATE ON medicine.intakes FOR EACH ROW EXECUTE FUNCTION medicine.fn_check_daily_supplement_limit();


--
-- Name: product_registry trg_calculate_total_fabric; Type: TRIGGER; Schema: texere; Owner: -
--

CREATE TRIGGER trg_calculate_total_fabric BEFORE INSERT OR UPDATE ON texere.product_registry FOR EACH ROW EXECUTE FUNCTION texere.fn_calculate_total_fabric();


--
-- Name: events_register events_register_event_type_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.events_register
    ADD CONSTRAINT events_register_event_type_fkey FOREIGN KEY (event_type) REFERENCES gardening.event_type(event_type);


--
-- Name: flower_box_history flower_box_history_box_id_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.flower_box_history
    ADD CONSTRAINT flower_box_history_box_id_fkey FOREIGN KEY (box_id) REFERENCES gardening.box_register(box_id);


--
-- Name: planted_seeds planted_seeds_box_id_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_box_id_fkey FOREIGN KEY (box_id) REFERENCES gardening.box_register(box_id);


--
-- Name: planted_seeds planted_seeds_seed_pack_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_seed_pack_fkey FOREIGN KEY (seed_pack) REFERENCES gardening.seed_pack(seed_pack_id);


--
-- Name: planted_seeds planted_seeds_state_fkey; Type: FK CONSTRAINT; Schema: gardening; Owner: -
--

ALTER TABLE ONLY gardening.planted_seeds
    ADD CONSTRAINT planted_seeds_state_fkey FOREIGN KEY (state) REFERENCES gardening.state(state);


--
-- Name: material_disposition fk_device_id; Type: FK CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.material_disposition
    ADD CONSTRAINT fk_device_id FOREIGN KEY (device_id) REFERENCES infrastructure.measuring_devices(id);


--
-- Name: material_disposition fk_resource_id; Type: FK CONSTRAINT; Schema: infrastructure; Owner: -
--

ALTER TABLE ONLY infrastructure.material_disposition
    ADD CONSTRAINT fk_resource_id FOREIGN KEY (resource_id) REFERENCES infrastructure.resource_catalog(id);


--
-- Name: intakes intakes_supplement_id_fkey; Type: FK CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.intakes
    ADD CONSTRAINT intakes_supplement_id_fkey FOREIGN KEY (supplement_id) REFERENCES medicine.supplements(id) ON DELETE CASCADE;


--
-- Name: schedules schedules_supplement_id_fkey; Type: FK CONSTRAINT; Schema: medicine; Owner: -
--

ALTER TABLE ONLY medicine.schedules
    ADD CONSTRAINT schedules_supplement_id_fkey FOREIGN KEY (supplement_id) REFERENCES medicine.supplements(id) ON DELETE CASCADE;


--
-- Name: SCHEMA gardening; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA gardening TO reflex_app_user;


--
-- Name: SCHEMA infrastructure; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA infrastructure TO reflex_app_user;


--
-- Name: SCHEMA medicine; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA medicine TO reflex_app_user;


--
-- Name: SCHEMA projects; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA projects TO reflex_app_user;


--
-- Name: SCHEMA repair; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA repair TO reflex_app_user;


--
-- Name: SCHEMA texere; Type: ACL; Schema: -; Owner: -
--

GRANT USAGE ON SCHEMA texere TO reflex_app_user;


--
-- Name: TABLE box_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.box_register TO reflex_app_user;


--
-- Name: TABLE event_type; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.event_type TO reflex_app_user;


--
-- Name: TABLE events_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.events_register TO reflex_app_user;


--
-- Name: TABLE fertilizer; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.fertilizer TO reflex_app_user;


--
-- Name: TABLE flower_box_history; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.flower_box_history TO reflex_app_user;


--
-- Name: TABLE flower_register; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.flower_register TO reflex_app_user;


--
-- Name: TABLE garden_state_report; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.garden_state_report TO reflex_app_user;


--
-- Name: TABLE lifecycle; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.lifecycle TO reflex_app_user;


--
-- Name: TABLE notes; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.notes TO reflex_app_user;


--
-- Name: TABLE planted_seeds; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.planted_seeds TO reflex_app_user;


--
-- Name: TABLE seed_pack; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.seed_pack TO reflex_app_user;


--
-- Name: TABLE state; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.state TO reflex_app_user;


--
-- Name: TABLE v_gardening_dashboard; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.v_gardening_dashboard TO reflex_app_user;


--
-- Name: TABLE disposal_points; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.disposal_points TO reflex_app_user;


--
-- Name: TABLE disposal_precedents; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.disposal_precedents TO reflex_app_user;


--
-- Name: TABLE material_disposition; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.material_disposition TO reflex_app_user;


--
-- Name: TABLE measuring_devices; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.measuring_devices TO reflex_app_user;


--
-- Name: TABLE resource_catalog; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.resource_catalog TO reflex_app_user;


--
-- Name: TABLE time_tracker; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.time_tracker TO reflex_app_user;


--
-- Name: TABLE v_material_disposition_current_month_report; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.v_material_disposition_current_month_report TO reflex_app_user;


--
-- Name: TABLE v_material_disposition_summary; Type: ACL; Schema: infrastructure; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE infrastructure.v_material_disposition_summary TO reflex_app_user;


--
-- Name: TABLE intakes; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.intakes TO reflex_app_user;


--
-- Name: TABLE observations; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.observations TO reflex_app_user;


--
-- Name: TABLE schedules; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.schedules TO reflex_app_user;


--
-- Name: TABLE supplements; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.supplements TO reflex_app_user;


--
-- Name: TABLE v_intakes_analysis; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.v_intakes_analysis TO reflex_app_user;


--
-- Name: TABLE v_monthly_supplements_summary; Type: ACL; Schema: medicine; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE medicine.v_monthly_supplements_summary TO reflex_app_user;


--
-- Name: TABLE metadata; Type: ACL; Schema: projects; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE projects.metadata TO reflex_app_user;


--
-- Name: TABLE projects; Type: ACL; Schema: repair; Owner: -
--

GRANT SELECT ON TABLE repair.projects TO reflex_app_user;


--
-- Name: TABLE v_project_consolidated_report; Type: ACL; Schema: repair; Owner: -
--

GRANT SELECT ON TABLE repair.v_project_consolidated_report TO reflex_app_user;


--
-- Name: TABLE consumables_inventory; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.consumables_inventory TO reflex_app_user;


--
-- Name: TABLE external_services; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.external_services TO reflex_app_user;


--
-- Name: TABLE fabric_treatment_protocols; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.fabric_treatment_protocols TO reflex_app_user;


--
-- Name: TABLE hardware_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.hardware_registry TO reflex_app_user;


--
-- Name: TABLE materials_inventory; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.materials_inventory TO reflex_app_user;


--
-- Name: TABLE patterns_inventory; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.patterns_inventory TO reflex_app_user;


--
-- Name: TABLE product_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.product_registry TO reflex_app_user;


--
-- Name: TABLE raw_transactions; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.raw_transactions TO reflex_app_user;


--
-- Name: TABLE tools_inventory; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.tools_inventory TO reflex_app_user;


--
-- Name: TABLE reconciled_transactions_summary; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.reconciled_transactions_summary TO reflex_app_user;


--
-- Name: TABLE repair_registry; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.repair_registry TO reflex_app_user;


--
-- Name: TABLE unreconciled_transactions; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.unreconciled_transactions TO reflex_app_user;


--
-- Name: TABLE v_international_media_catalog; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_international_media_catalog TO reflex_app_user;


--
-- Name: TABLE v_product_fabric_analytics; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_product_fabric_analytics TO reflex_app_user;


--
-- Name: TABLE v_project_summary_post; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_project_summary_post TO reflex_app_user;


--
-- Name: TABLE v_textile_production_metrics; Type: ACL; Schema: texere; Owner: -
--

GRANT SELECT ON TABLE texere.v_textile_production_metrics TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: gardening; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA gardening GRANT SELECT ON TABLES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: infrastructure; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA infrastructure GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: medicine; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA medicine GRANT SELECT,USAGE ON SEQUENCES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: medicine; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA medicine GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: projects; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA projects GRANT SELECT,USAGE ON SEQUENCES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: projects; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA projects GRANT SELECT,INSERT,DELETE,UPDATE ON TABLES TO reflex_app_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: repair; Owner: -
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA repair GRANT SELECT ON TABLES TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict Go9sW9QOGQWEpMur8eCivDMI2HMGSjZ8DqYEoT7hdP4MZdSoLsBoUc7EIsNGz0F

