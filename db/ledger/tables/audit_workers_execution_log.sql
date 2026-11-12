--
-- PostgreSQL database dump
--

\restrict 7JFlm12ot3yVUdciX8qCXJYajMgduCClrbgapQRYkOSib09Oeh4Lf3pIWXAmn8z

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
-- Name: workers_execution_log; Type: TABLE; Schema: audit; Owner: -
--

CREATE TABLE audit.workers_execution_log (
    run_id uuid NOT NULL,
    worker_id uuid NOT NULL,
    trigger_source character varying(32) DEFAULT 'SCHEDULED'::character varying NOT NULL,
    status character varying(20) NOT NULL,
    started_at timestamp with time zone DEFAULT now() NOT NULL,
    finished_at timestamp with time zone,
    duration_ms integer GENERATED ALWAYS AS ((EXTRACT(epoch FROM (finished_at - started_at)) * (1000)::numeric)) STORED,
    exit_code integer,
    details jsonb DEFAULT '{}'::jsonb,
    CONSTRAINT workers_execution_log_status_check CHECK (((status)::text = ANY ((ARRAY['RUNNING'::character varying, 'SUCCESS'::character varying, 'FAILED'::character varying, 'SKIPPED'::character varying])::text[])))
);


--
-- Name: workers_execution_log workers_execution_log_pkey; Type: CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.workers_execution_log
    ADD CONSTRAINT workers_execution_log_pkey PRIMARY KEY (run_id);


--
-- Name: idx_workers_exec_status; Type: INDEX; Schema: audit; Owner: -
--

CREATE INDEX idx_workers_exec_status ON audit.workers_execution_log USING btree (status) WHERE ((status)::text = ANY ((ARRAY['RUNNING'::character varying, 'FAILED'::character varying])::text[]));


--
-- Name: idx_workers_exec_worker_started; Type: INDEX; Schema: audit; Owner: -
--

CREATE INDEX idx_workers_exec_worker_started ON audit.workers_execution_log USING btree (worker_id, started_at DESC);


--
-- Name: workers_execution_log workers_execution_log_worker_id_fkey; Type: FK CONSTRAINT; Schema: audit; Owner: -
--

ALTER TABLE ONLY audit.workers_execution_log
    ADD CONSTRAINT workers_execution_log_worker_id_fkey FOREIGN KEY (worker_id) REFERENCES audit.workers_registry(worker_id) ON DELETE RESTRICT;


--
-- Name: TABLE workers_execution_log; Type: ACL; Schema: audit; Owner: -
--

GRANT SELECT,INSERT,DELETE,UPDATE ON TABLE audit.workers_execution_log TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 7JFlm12ot3yVUdciX8qCXJYajMgduCClrbgapQRYkOSib09Oeh4Lf3pIWXAmn8z

