--
-- PostgreSQL database dump
--

\restrict kg4XCR3ivYBolTQIlU8iLIdpe08X9jmOZUcZfvkyjxvVeTNo7jXd00eah86ZQRM

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
-- Name: v_sys_verification_summary; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_sys_verification_summary AS
 SELECT count(*) AS total_audit_events_count,
    count(*) FILTER (WHERE (is_verified_state = 1)) AS fully_verified_states_count,
    count(*) FILTER (WHERE ((is_verified_state = 0) AND (verification_issue ~~ 'Промежуточная%'::text))) AS intermediate_package_rows_count,
    count(*) FILTER (WHERE ((is_verified_state = 0) AND (verification_issue ~~ 'Неполный аудит%'::text))) AS failed_verification_points_count,
    round(((100.0 * (count(*) FILTER (WHERE (is_verified_state = 1)))::numeric) / (NULLIF(count(*), 0))::numeric), 2) AS ledger_reliability_index_pct,
    count(*) FILTER (WHERE ((is_verified_state = 1) AND (verification_model = 'Старая'::text))) AS verified_via_old_model_count,
    count(*) FILTER (WHERE ((is_verified_state = 1) AND (verification_model = 'Node (Новая)'::text))) AS verified_via_new_model_count,
    count(*) FILTER (WHERE ((is_verified_state = 1) AND (verification_model = 'Финальная (Лог)'::text))) AS verified_via_log_model_count
   FROM reports.v_verified_state_ledger;


--
-- Name: TABLE v_sys_verification_summary; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_sys_verification_summary TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict kg4XCR3ivYBolTQIlU8iLIdpe08X9jmOZUcZfvkyjxvVeTNo7jXd00eah86ZQRM

