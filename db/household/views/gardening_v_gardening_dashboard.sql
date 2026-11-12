--
-- PostgreSQL database dump
--

\restrict TcAiOgGZjQbBQ7IuRH2KJz4bQqGCwOw6hykarLBAbqLNeySQThuChdKlhZR8Cga

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
-- Name: TABLE v_gardening_dashboard; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.v_gardening_dashboard TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict TcAiOgGZjQbBQ7IuRH2KJz4bQqGCwOw6hykarLBAbqLNeySQThuChdKlhZR8Cga

