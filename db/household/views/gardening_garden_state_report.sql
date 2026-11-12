--
-- PostgreSQL database dump
--

\restrict jpuWYbceGFCwfHVr32arDwsPiRmNMnVmBgeQP5Bi9jJE0ugfdQT9T3qRUYEpgEw

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
-- Name: TABLE garden_state_report; Type: ACL; Schema: gardening; Owner: -
--

GRANT SELECT ON TABLE gardening.garden_state_report TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict jpuWYbceGFCwfHVr32arDwsPiRmNMnVmBgeQP5Bi9jJE0ugfdQT9T3qRUYEpgEw

