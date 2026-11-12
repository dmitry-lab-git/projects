--
-- PostgreSQL database dump
--

\restrict 0QiCALOaEHXDqPK725NscuHYdgC5Ht2ejWawHWG2vRTPfTJxt0ZH4RgrvfrEQpr

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
-- Name: v_verified_state_ledger; Type: VIEW; Schema: reports; Owner: -
--

CREATE VIEW reports.v_verified_state_ledger AS
 WITH ledger_raw AS (
         SELECT ledger.transaction_id AS tx_code,
            ledger.transaction_uuid AS tx_id,
            ledger.name AS transaction_name,
            ledger.operation_date,
            ledger.account_id AS acc_uuid,
            ledger.amount,
            ledger.acc_balance AS running_acc_balance,
            ledger.system_balance AS running_system_balance
           FROM public.ledger
        ), linked_logs AS (
         SELECT log.id AS log_id,
            log.verified_at,
            ( SELECT l_sub.transaction_id
                   FROM public.ledger l_sub
                  WHERE (l_sub.operation_date <= log.verified_at)
                  ORDER BY l_sub.operation_date DESC, l_sub.transaction_id DESC
                 LIMIT 1) AS max_tx_code_for_log
           FROM reports.system_verification_log log
        ), new_model_snapshot_txs AS (
         SELECT DISTINCT (r.tr_id)::integer AS tx_code
           FROM public.acc_balance_snapshot_register r
          WHERE ((r.tr_id IS NOT NULL) AND ((r.tr_id)::text <> ''::text))
        ), ledger_flagged AS (
         SELECT l.tx_code,
            l.tx_id,
            l.transaction_name,
            l.operation_date,
            l.acc_uuid,
            l.amount,
            l.running_acc_balance,
            l.running_system_balance,
                CASE
                    WHEN (EXISTS ( SELECT 1
                       FROM linked_logs ll
                      WHERE (ll.max_tx_code_for_log = l.tx_code))) THEN 'Финальная (Лог)'::text
                    WHEN ((l.tx_code >= 1363) AND (EXISTS ( SELECT 1
                       FROM new_model_snapshot_txs nms
                      WHERE (nms.tx_code = l.tx_code)))) THEN 'Node (Новая)'::text
                    WHEN ((l.tx_code < 1363) AND ((lower(l.transaction_name) ~~ '%ревизия%'::text) OR (l.transaction_name = 'Ревизия'::text))) THEN 'Старая'::text
                    ELSE 'Операционная'::text
                END AS current_row_model
           FROM ledger_raw l
        ), account_states_history AS (
         SELECT lf.tx_code,
            lf.tx_id,
            lf.transaction_name,
            lf.operation_date,
            lf.acc_uuid,
            lf.amount,
            lf.running_acc_balance,
            lf.running_system_balance,
            lf.current_row_model,
            sum(
                CASE
                    WHEN (lf.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text, 'Финальная (Лог)'::text])) THEN 1
                    WHEN (lf.amount <> (0)::numeric) THEN '-1'::integer
                    ELSE 0
                END) OVER (PARTITION BY lf.acc_uuid ORDER BY lf.tx_code) AS account_clean_score
           FROM ledger_flagged lf
        ), account_dirty_flags AS (
         SELECT ash.tx_code,
            ash.tx_id,
            ash.transaction_name,
            ash.operation_date,
            ash.acc_uuid,
            ash.amount,
            ash.running_acc_balance,
            ash.running_system_balance,
            ash.current_row_model,
            ash.account_clean_score,
                CASE
                    WHEN (ash.account_clean_score <= 0) THEN 1
                    ELSE 0
                END AS is_account_dirty
           FROM account_states_history ash
        ), global_system_dirt_counter AS (
         SELECT adf.tx_code,
            adf.tx_id,
            adf.transaction_name,
            adf.operation_date,
            adf.acc_uuid,
            adf.amount,
            adf.running_acc_balance,
            adf.running_system_balance,
            adf.current_row_model,
            adf.account_clean_score,
            adf.is_account_dirty,
            sum(adf.is_account_dirty) OVER (PARTITION BY adf.tx_code) AS global_dirty_accounts_count
           FROM account_dirty_flags adf
        ), audit_packages AS (
         SELECT ledger_flagged.tx_code,
            ledger_flagged.operation_date AS op_date,
            ledger_flagged.current_row_model,
            max(ledger_flagged.tx_code) OVER (PARTITION BY ledger_flagged.operation_date, ledger_flagged.current_row_model) AS max_tx_code_of_batch
           FROM ledger_flagged
          WHERE (ledger_flagged.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text, 'Финальная (Лог)'::text]))
        )
 SELECT DISTINCT g.tx_code,
    g.tx_id AS transaction_id,
    (g.operation_date)::timestamp without time zone AS transaction_date,
    g.running_system_balance AS state_balance,
    g.current_row_model AS verification_model,
        CASE
            WHEN (g.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text, 'Финальная (Лог)'::text])) THEN 1
            ELSE 0
        END AS is_row_verified,
        CASE
            WHEN (g.current_row_model = 'Финальная (Лог)'::text) THEN 1
            WHEN ((g.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text])) AND (g.tx_code = ap.max_tx_code_of_batch) AND (g.global_dirty_accounts_count = 0)) THEN 1
            ELSE 0
        END AS is_verified_state,
        CASE
            WHEN (g.current_row_model = 'Финальная (Лог)'::text) THEN 'Система успешно подтверждена записью в системном журнале логов'::text
            WHEN ((g.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text])) AND (g.tx_code = ap.max_tx_code_of_batch) AND (g.global_dirty_accounts_count = 0)) THEN 'Верификация успешна: все измененные балансы счетов подтверждены аудитом'::text
            WHEN ((g.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text])) AND (g.tx_code <> ap.max_tx_code_of_batch)) THEN (('Промежуточная часть распределенной сверки пакета (смещение на код '::text || ap.max_tx_code_of_batch) || ')'::text)
            WHEN ((g.current_row_model = ANY (ARRAY['Старая'::text, 'Node (Новая)'::text])) AND (g.global_dirty_accounts_count > 0)) THEN ('Неполный audit системы: обнаружено необработанных операционных счетов — '::text || g.global_dirty_accounts_count)
            ELSE 'Обычная операционная транзакция: изменяет состояние баланса системы'::text
        END AS verification_issue,
    ap.max_tx_code_of_batch AS max_audit_code_of_batch
   FROM (global_system_dirt_counter g
     JOIN audit_packages ap ON ((g.tx_code = ap.tx_code)))
  WHERE (g.current_row_model <> 'Операционная'::text);


--
-- Name: TABLE v_verified_state_ledger; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.v_verified_state_ledger TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 0QiCALOaEHXDqPK725NscuHYdgC5Ht2ejWawHWG2vRTPfTJxt0ZH4RgrvfrEQpr

