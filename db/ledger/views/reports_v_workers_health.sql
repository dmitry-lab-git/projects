--
-- PostgreSQL database dump
--

\restrict KslmLsXtV7uwXLwHibOORP1mUrVeyUQ5dTzITmAi3aFSZhVw995V3ZbqUDxunqf

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
-- Name: v_workers_health; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_workers_health AS
 WITH last_runs AS (
         SELECT DISTINCT ON (workers_execution_log.worker_id) workers_execution_log.worker_id,
            workers_execution_log.run_id,
            workers_execution_log.status AS last_status,
            workers_execution_log.trigger_source,
            workers_execution_log.started_at AS last_started_at,
            workers_execution_log.finished_at AS last_finished_at,
            workers_execution_log.duration_ms AS last_duration_ms,
            workers_execution_log.exit_code,
            workers_execution_log.details
           FROM audit.workers_execution_log
          ORDER BY workers_execution_log.worker_id, workers_execution_log.started_at DESC
        ), last_success AS (
         SELECT DISTINCT ON (workers_execution_log.worker_id) workers_execution_log.worker_id,
            workers_execution_log.finished_at AS last_success_at
           FROM audit.workers_execution_log
          WHERE ((workers_execution_log.status)::text = 'SUCCESS'::text)
          ORDER BY workers_execution_log.worker_id, workers_execution_log.finished_at DESC
        )
 SELECT r.worker_id,
    r.worker_code,
    r.title,
    r.executor_type,
    r.schedule_expr,
    r.is_active,
    lr.last_status,
    lr.last_started_at,
    lr.last_duration_ms,
    ls.last_success_at,
    round((EXTRACT(epoch FROM (now() - COALESCE(ls.last_success_at, r.created_at))) / (60)::numeric)) AS silence_minutes,
    r.max_silence_minutes,
        CASE
            WHEN (NOT r.is_active) THEN 'DISABLED'::text
            WHEN ((lr.last_status)::text = 'FAILED'::text) THEN 'ALERT_FAILED'::text
            WHEN ((EXTRACT(epoch FROM (now() - COALESCE(ls.last_success_at, r.created_at))) / (60)::numeric) > (r.max_silence_minutes)::numeric) THEN 'ALERT_OVERDUE'::text
            WHEN ((lr.last_status)::text = 'RUNNING'::text) THEN 'WORKING'::text
            ELSE 'HEALTHY'::text
        END AS health_state,
    lr.details AS last_details
   FROM ((audit.workers_registry r
     LEFT JOIN last_runs lr ON ((r.worker_id = lr.worker_id)))
     LEFT JOIN last_success ls ON ((r.worker_id = ls.worker_id)));


--
-- Name: TABLE v_workers_health; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_workers_health TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict KslmLsXtV7uwXLwHibOORP1mUrVeyUQ5dTzITmAi3aFSZhVw995V3ZbqUDxunqf

