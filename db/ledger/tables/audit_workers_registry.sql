--
-- PostgreSQL database dump
--

\restrict 6JqI3HPzZKuKfBIDVfd6ITvKUnWGLMoxIfsCEjHLHjHaNCpHHKyXsjP9LiDHkXp

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: workers_registry; Type: TABLE; Schema: audit; Owner: -
--

CREATE TABLE audit.workers_registry (
    worker_id uuid DEFAULT gen_random_uuid() NOT NULL,
    worker_code character varying(64) NOT NULL,
    title character varying(150) NOT NULL,
    executor_type character varying(32) NOT NULL,
    schedule_expr character varying(64),
    script_path text NOT NULL,
    max_silence_minutes integer DEFAULT 1500 NOT NULL,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT workers_registry_executor_type_check CHECK (((executor_type)::text = ANY ((ARRAY['CRON'::character varying, 'APSCHEDULER'::character varying, 'MANUAL'::character varying])::text[])))
);


--
-- Name: workers_registry workers_registry_pkey; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.workers_registry
    ADD CONSTRAINT workers_registry_pkey PRIMARY KEY (worker_id);


--
-- Name: workers_registry workers_registry_worker_code_key; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.workers_registry
    ADD CONSTRAINT workers_registry_worker_code_key UNIQUE (worker_code);


--
-- Name: TABLE workers_registry; Type: ACL; Schema: audit; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE audit.workers_registry TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 6JqI3HPzZKuKfBIDVfd6ITvKUnWGLMoxIfsCEjHLHjHaNCpHHKyXsjP9LiDHkXp

