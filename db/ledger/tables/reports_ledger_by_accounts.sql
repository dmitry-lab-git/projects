--
-- PostgreSQL database dump
--

\restrict 0izBA2enQO7EMX7hEDGfGtlQOcnRKIyUHs5KRptYeJJ90cxuqHL6EC9kbsS0gCl

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
-- Name: ledger_by_accounts; Type: TABLE; Schema: reports; Owner: -
--

CREATE TABLE reports.ledger_by_accounts (
    transaction_id integer NOT NULL,
    account_id character varying(50) NOT NULL,
    account_balance numeric(19,4) NOT NULL,
    system_balance numeric(19,4) NOT NULL,
    transaction_name text,
    account_is_verified boolean NOT NULL,
    system_is_verified boolean NOT NULL
);


--
-- Name: ledger_by_accounts ledger_by_accounts_pkey; Type: CONSTRAINT; Schema: reports; Owner: -
--

ALTER TABLE ONLY reports.ledger_by_accounts
    ADD CONSTRAINT ledger_by_accounts_pkey PRIMARY KEY (transaction_id, account_id);


--
-- Name: idx_reports_ledger_acc; Type: INDEX; Schema: reports; Owner: -
--

CREATE INDEX idx_reports_ledger_acc ON reports.ledger_by_accounts USING btree (account_id);


--
-- Name: TABLE ledger_by_accounts; Type: ACL; Schema: reports; Owner: -
--

GRANT SELECT ON TABLE reports.ledger_by_accounts TO reflex_app_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 0izBA2enQO7EMX7hEDGfGtlQOcnRKIyUHs5KRptYeJJ90cxuqHL6EC9kbsS0gCl

