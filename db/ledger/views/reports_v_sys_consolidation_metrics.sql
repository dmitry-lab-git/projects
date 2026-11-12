--
-- PostgreSQL database dump
--

\restrict 1SBp8JeyK9icx9Hxg1HAc3kFm0t6j8utvjMMvVXy93bducNEuHlHNSLGGIJ1N4z

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
-- Name: v_sys_consolidation_metrics; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_sys_consolidation_metrics AS
 WITH tx_aggregates AS (
         SELECT count(*) AS total_count,
            count(*) FILTER (WHERE (((lower((transactions.transaction_name)::text) ~~ '%ревизия%'::text) OR (transactions.type_id = ANY (ARRAY['57f201e7-10ee-4219-a18d-ad6a8777f5a8'::uuid, '7bf484c8-1a59-41d2-8ee3-f1a38a0e4125'::uuid]))) AND (transactions.amount <> (0)::numeric))) AS target_count,
            sum(abs(transactions.amount)) FILTER (WHERE (((lower((transactions.transaction_name)::text) ~~ '%ревизия%'::text) OR (transactions.type_id = ANY (ARRAY['57f201e7-10ee-4219-a18d-ad6a8777f5a8'::uuid, '7bf484c8-1a59-41d2-8ee3-f1a38a0e4125'::uuid]))) AND (transactions.amount <> (0)::numeric))) AS target_volume,
            sum(transactions.amount) FILTER (WHERE (transactions.type_id = '1cff2885-bbdf-45f0-a2e5-1ffeac8d938b'::uuid)) AS total_income,
            count(*) FILTER (WHERE (lower((transactions.transaction_name)::text) ~~ '%ревизия%'::text)) AS tx_revisions_count
           FROM public.transactions
        ), current_balance AS (
         SELECT COALESCE(sum(account_state_report.balance), (0)::numeric) AS total_sys_balance
           FROM reports.account_state_report
        ), snapshot_aggregates AS (
         SELECT count(*) AS snapshot_count
           FROM public.acc_balance_snapshot_register
        ), calculated_metrics AS (
         SELECT t.total_count,
            t.target_count,
            t.target_volume,
            t.total_income,
            (t.tx_revisions_count + s.snapshot_count) AS total_audits_count,
            NULLIF((t.total_income - b.total_sys_balance), (0)::numeric) AS money_passed_through
           FROM ((tx_aggregates t
             CROSS JOIN current_balance b)
             CROSS JOIN snapshot_aggregates s)
        )
 SELECT total_count AS "Всего транзакций (шт)",
    target_count AS "Из них Корректировок (шт)",
    round(((100.0 * (target_count)::numeric) / (NULLIF(total_count, 0))::numeric), 2) AS "Доля корректировок по шт (%)",
    COALESCE(money_passed_through, (0)::numeric) AS "Деньги прошедшие через систему",
    COALESCE(target_volume, (0)::numeric) AS "Объем корректировок (сумма)",
    round(((100.0 * COALESCE(target_volume, (0)::numeric)) / money_passed_through), 2) AS "Доля корректировок по сумме (%)",
    total_audits_count AS "Количество сверок счетов (шт)"
   FROM calculated_metrics;


--
-- Name: TABLE v_sys_consolidation_metrics; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_sys_consolidation_metrics TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 1SBp8JeyK9icx9Hxg1HAc3kFm0t6j8utvjMMvVXy93bducNEuHlHNSLGGIJ1N4z

