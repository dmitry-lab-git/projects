--
-- PostgreSQL database dump
--

\restrict amf5M6cYkpjmflOFFlMMCwMKkdk3twV6CzkFxZ7J2ovYJONStVt3SJcahWHlGKt

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
-- Name: v_ledger_metrics; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_ledger_metrics AS
 SELECT ( SELECT count(*) AS count
           FROM public.transactions) AS transactions,
    ( SELECT count(*) AS count
           FROM public.acc_balance_snapshot_register) AS acc_balance_snapshot_register,
    ( SELECT count(*) AS count
           FROM reports.system_verification_log
          WHERE (system_verification_log.verified_at >= '2026-10-13 00:00:00+05'::timestamp with time zone)) AS system_verification_log,
    ( SELECT count(*) AS count
           FROM audit.staging_transactions) AS staging_transactions;


--
-- Name: TABLE v_ledger_metrics; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_ledger_metrics TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict amf5M6cYkpjmflOFFlMMCwMKkdk3twV6CzkFxZ7J2ovYJONStVt3SJcahWHlGKt

